"""
CPA Network Offer Scanner
Scans live CPA network offer pages using browser-harness (CDP).
Works with YOUR logged-in Chrome session.
"""

import sys
import time
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from pathlib import Path

# Add browser-harness to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "browser-harness" / "src"))

from browser_harness.helpers import *


@dataclass
class Offer:
    offer_id: str
    network: str
    name: str
    vertical: str
    geo: str
    payout: float
    flow: str  # CPI, CPL, CPS, SOI, DOI
    cap_daily: int
    lander_url: str
    restrictions: List[str]
    approval_difficulty: int  # 1-10
    source_url: str
    scraped_at: str
    freshness_score: float = 1.0


class CPAOfferScanner:
    """Scans CPA network offer pages for fresh offers."""
    
    NETWORK_URLS = {
        "adcombo": "https://www.adcombo.com/offers",
        "cpalead": "https://www.cpalead.com/offers",
        "alfaleads": "https://alfaleads.com/offers",
        "cpatrend": "https://cpatrend.com/offers",
        "maxbounty": "https://www.maxbounty.com/offers",
        "cpa_grip": "https://www.cpagrip.com/offers",
    }
    
    def __init__(self):
        self.offers = []
    
    def scan_network(self, network: str, geo: str = "IN", 
                     verticals: List[str] = None, 
                     min_payout: float = 3.0,
                     min_cap: int = 1000) -> List[Offer]:
        """Scan a CPA network for offers matching criteria."""
        
        if network not in self.NETWORK_URLS:
            raise ValueError(f"Unknown network: {network}. Available: {list(self.NETWORK_URLS.keys())}")
        
        url = self.NETWORK_URLS[network]
        print(f"Scanning {network} offers: {url}")
        
        goto_url(url)
        wait_for_load()
        time.sleep(3)
        
        # Scroll to load more offers
        for _ in range(5):
            scroll("down", 3)
            time.sleep(1)
        
        # Extract offers
        raw_offers = js(self._get_extraction_js(network))
        offers = self._parse_offers(raw_offers, network, geo, verticals, min_payout, min_cap)
        
        self.offers.extend(offers)
        return offers
    
    def _get_extraction_js(self, network: str) -> str:
        """Return JavaScript for extracting offers from a specific network."""
        
        # Network-specific selectors
        selectors = {
            "adcombo": {
                "container": "[class*='offer'], [class*='campaign'], tr[class*='offer'], .offer-row",
                "name": "[class*='name'], [class*='title'], .offer-title",
                "payout": "[class*='payout'], [class*='price'], [data-payout]",
                "cap": "[class*='cap'], [class*='limit'], [data-cap]",
                "geo": "[class*='geo'], [class*='country'], [data-geo]",
                "vertical": "[class*='vertical'], [class*='category'], [data-vertical]",
                "flow": "[class*='flow'], [class*='conversion'], [data-flow]",
                "lander": "a[href*='land'], a[href*='preview'], .lander-link",
                "restrictions": "[class*='restrict'], [class*='note'], .restrictions"
            },
            "cpalead": {
                "container": "[class*='offer'], [class*='campaign'], .offer-item",
                "name": "[class*='name'], [class*='title']",
                "payout": "[class*='payout'], [class*='price",
                "cap": "[class*='cap']",
                "geo": "[class*='geo'], [class*='country']",
                "vertical": "[class*='vertical'], [class*='category']",
                "flow": "[class*='flow']",
                "lander": "a[href*='land']",
                "restrictions": "[class*='restrict']"
            }
        }
        
        net_selectors = selectors.get(network, selectors["adcombo"])
        
        return f"""
        const offers = [];
        const selectors = {json.dumps(net_selectors)};
        
        const containers = document.querySelectorAll(selectors.container);
        
        containers.forEach(container => {{
            try {{
                const offer = {{
                    network: "{network}",
                    name: "",
                    payout: 0,
                    cap_daily: 0,
                    geo: "",
                    vertical: "",
                    flow: "",
                    lander_url: "",
                    restrictions: [],
                    source_url: window.location.href
                }};
                
                // Name
                const nameEl = container.querySelector(selectors.name);
                if (nameEl) offer.name = nameEl.textContent.trim();
                
                // Payout
                const payoutEl = container.querySelector(selectors.payout);
                if (payoutEl) {{
                    const text = payoutEl.textContent || payoutEl.getAttribute('data-payout') || '';
                    const match = text.match(/([\\d.]+)/);
                    if (match) offer.payout = parseFloat(match[1]);
                }}
                
                // Cap
                const capEl = container.querySelector(selectors.cap);
                if (capEl) {{
                    const text = capEl.textContent || capEl.getAttribute('data-cap') || '';
                    const match = text.match(/([\\d,]+)/);
                    if (match) offer.cap_daily = parseInt(match[1].replace(/,/g, ''));
                }}
                
                // Geo
                const geoEl = container.querySelector(selectors.geo);
                if (geoEl) offer.geo = geoEl.textContent.trim();
                
                // Vertical
                const vertEl = container.querySelector(selectors.vertical);
                if (vertEl) offer.vertical = vertEl.textContent.trim();
                
                // Flow
                const flowEl = container.querySelector(selectors.flow);
                if (flowEl) offer.flow = flowEl.textContent.trim();
                
                // Lander
                const landerEl = container.querySelector(selectors.lander);
                if (landerEl) offer.lander_url = landerEl.href;
                
                // Restrictions
                const restrictEl = container.querySelector(selectors.restrictions);
                if (restrictEl) offer.restrictions = restrictEl.textContent.trim().split('\\n').map(s => s.trim()).filter(Boolean);
                
                if (offer.name) offers.push(offer);
            }} catch (e) {{
                console.log('Error:', e);
            }}
        }});
        
        return offers;
        """
    
    def _parse_offers(self, raw_offers: List[Dict], network: str, geo: str,
                      verticals: List[str], min_payout: float, min_cap: int) -> List[Offer]:
        """Parse raw offers into Offer objects with filtering."""
        offers = []
        for raw in raw_offers:
            try:
                # Filter
                if raw.get('payout', 0) < min_payout:
                    continue
                if raw.get('cap_daily', 0) < min_cap:
                    continue
                if geo and geo.upper() not in raw.get('geo', '').upper():
                    # Some networks don't show geo in list, skip filter
                    pass
                if verticals and raw.get('vertical', '').lower() not in [v.lower() for v in verticals]:
                    pass
                
                offer = Offer(
                    offer_id=f"{network}_{raw.get('name', '').replace(' ', '_').lower()}_{int(time.time())}",
                    network=network,
                    name=raw.get('name', ''),
                    vertical=raw.get('vertical', ''),
                    geo=raw.get('geo', geo),
                    payout=raw.get('payout', 0),
                    flow=raw.get('flow', 'CPI'),
                    cap_daily=raw.get('cap_daily', 0),
                    lander_url=raw.get('lander_url', ''),
                    restrictions=raw.get('restrictions', []),
                    approval_difficulty=5,  # Default
                    source_url=raw.get('source_url', ''),
                    scraped_at=datetime.now().isoformat()
                )
                offers.append(offer)
            except Exception as e:
                continue
        return offers
    
    def scan_all_networks(self, geo: str = "IN", verticals: List[str] = None,
                          min_payout: float = 3.0, min_cap: int = 1000) -> List[Offer]:
        """Scan all configured networks."""
        all_offers = []
        for network in self.NETWORK_URLS:
            try:
                offers = self.scan_network(network, geo, verticals, min_payout, min_cap)
                all_offers.extend(offers)
                print(f"  {network}: {len(offers)} offers")
            except Exception as e:
                print(f"  {network}: ERROR - {e}")
        return all_offers
    
    def save_offers(self, filepath: str):
        """Save offers to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([asdict(o) for o in self.offers], f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    scanner = CPAOfferScanner()
    
    # Scan AdCombo for India gambling/dating/PWA
    offers = scanner.scan_network(
        network="adcombo",
        geo="IN",
        verticals=["gambling", "dating", "pwa_install", "sports"],
        min_payout=3.0,
        min_cap=1000
    )
    
    print(f"Found {len(offers)} offers:")
    for o in offers[:10]:
        print(f"  {o.name} | ${o.payout} | Cap: {o.cap_daily} | Flow: {o.flow} | Geo: {o.geo}")