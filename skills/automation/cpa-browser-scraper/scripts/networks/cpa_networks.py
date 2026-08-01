"""
CPA Network Offer Scanners using browser-harness.
Scans live offer pages from AdCombo, CPAlead, Alfaleads, CPATrend.
"""
import sys
sys.path.insert(0, '/d/Portable_Soft/hermes/browser-harness/src')

from browser_harness.helpers import *
from scripts.models import Offer
from datetime import datetime
from typing import List, Dict, Any
import time
import json


class CPAOfferScanner:
    """Scans CPA network offer pages for fresh offers."""
    
    NETWORK_CONFIGS = {
        "adcombo": {
            "offers_url": "https://www.adcombo.com/offers",
            "login_url": "https://www.adcombo.com/login",
            "offer_selector": "[class*='offer'], [class*='OfferRow'], tr[class*='offer']",
            "name_selectors": ["[class*='name'], [class*='title'], h3, h4, a[class*='offer']"],
            "payout_selectors": ["[class*='payout'], [class*='price'], [data-payout]"],
            "cap_selectors": ["[class*='cap'], [class*='limit'], [data-cap]"],
            "geo_selectors": ["[class*='geo'], [class*='country'], [data-geo]"],
            "vertical_selectors": ["[class*='vertical'], [class*='category'], [data-vertical]"],
        },
        "cpalead": {
            "offers_url": "https://www.cpalead.com/offers",
            "login_url": "https://www.cpalead.com/login",
            "offer_selector": "[class*='offer'], [class*='OfferCard'], .offer-item",
            "name_selectors": ["[class*='name'], [class*='title'], h3, h4"],
            "payout_selectors": ["[class*='payout'], [class*='earn'], [class*='rate']"],
            "cap_selectors": ["[class*='cap'], [class*='limit']"],
            "geo_selectors": ["[class*='geo'], [class*='country']"],
            "vertical_selectors": ["[class*='vertical'], [class*='category']"],
        },
        "alfaleads": {
            "offers_url": "https://alfaleads.com/offers",
            "login_url": "https://alfaleads.com/login",
            "offer_selector": "[class*='offer'], .offer-card, [data-offer]",
            "name_selectors": ["[class*='name'], [class*='title']"],
            "payout_selectors": ["[class*='payout'], [class*='cpa']"],
            "cap_selectors": ["[class*='cap'], [class*='limit']"],
            "geo_selectors": ["[class*='geo'], [class*='country']"],
            "vertical_selectors": ["[class*='vertical'], [class*='category']"],
        },
        "cpatrend": {
            "offers_url": "https://cpatrend.com/offers",
            "login_url": "https://cpatrend.com/login",
            "offer_selector": "[class*='offer'], .offer-item, [data-offer-id]",
            "name_selectors": ["[class*='name'], [class*='title']"],
            "payout_selectors": ["[class*='payout'], [class*='rate']"],
            "cap_selectors": ["[class*='cap'], [class*='limit']"],
            "geo_selectors": ["[class*='geo'], [class*='country']"],
            "vertical_selectors": ["[class*='vertical'], [class*='category']"],
        }
    }
    
    def __init__(self):
        self.offers = []
    
    def scan_network(self, network: str, geo: str = "IN", verticals: List[str] = None, 
                     min_payout: float = 3.0, min_cap: int = 1000) -> List[Offer]:
        """Scan a CPA network for offers matching criteria."""
        if network not in self.NETWORK_CONFIGS:
            raise ValueError(f"Unknown network: {network}. Supported: {list(self.NETWORK_CONFIGS.keys())}")
        
        config = self.NETWORK_CONFIGS[network]
        self._ensure_logged_in(network, config)
        
        # Navigate to offers page with filters
        offers_url = self._build_offers_url(config, geo, verticals)
        goto_url(offers_url)
        wait_for_load()
        time.sleep(3)
        
        # Apply filters if possible
        self._apply_filters(geo, verticals, min_payout)
        
        # Scroll and extract
        offers = self._extract_offers(config, network, geo, verticals, min_payout, min_cap)
        return offers
    
    def _ensure_logged_in(self, network: str, config: Dict):
        """Check if logged in, if not navigate to login page."""
        current = page_info()
        if config["login_url"] not in current.get("url", "") and "login" not in current.get("url", ""):
            # Check for login indicators
            login_indicators = js("""
                return !!document.querySelector('[type="password"], [name="login"], [name="email"], button[type="submit"]');
            """)
            if login_indicators:
                print(f"Need to log in to {network}. Please log in manually in the browser.")
                # Wait for manual login
                for _ in range(60):
                    time.sleep(1)
                    if "offers" in page_info().get("url", ""):
                        break
    
    def _build_offers_url(self, config: Dict, geo: str, verticals: List[str]) -> str:
        base = config["offers_url"]
        params = []
        if geo:
            params.append(f"geo={geo}")
        if verticals:
            params.append(f"vertical={','.join(verticals)}")
        if params:
            return f"{base}?{'&'.join(params)}"
        return base
    
    def _apply_filters(self, geo: str, verticals: List[str], min_payout: float):
        """Apply filters on the offers page."""
        filter_js = f"""
        // Try to find and set filters
        const geoSelect = document.querySelector('select[name*="geo"], select[id*="geo"], [data-filter="geo"]');
        if (geoSelect) {{
            geoSelect.value = "{geo}";
            geoSelect.dispatchEvent(new Event('change'));
        }}
        
        // Set min payout if input exists
        const payoutInput = document.querySelector('input[name*="payout"], input[id*="payout"], input[placeholder*="payout"]');
        if (payoutInput) {{
            payoutInput.value = "{min_payout}";
            payoutInput.dispatchEvent(new Event('input'));
        }}
        
        // Click apply/refresh button
        const applyBtn = document.querySelector('button[type="submit"], button:contains("Apply"), button:contains("Filter"), [data-action="filter"]');
        if (applyBtn) applyBtn.click();
        
        return "filters applied";
        """
        js(filter_js)
        time.sleep(2)
    
    def _extract_offers(self, config: Dict, network: str, geo: str, verticals: List[str],
                        min_payout: float, min_cap: int) -> List[Offer]:
        """Extract offer data from the page."""
        
        extraction_js = f"""
        const offers = [];
        const seen = new Set();
        
        // Find offer rows/cards
        const selectors = [
            "{config['offer_selector']}",
            "tr[class*='offer']",
            "[class*='offer-row']",
            "[class*='offer-card']",
            "[data-offer-id]",
            ".offer-item"
        ];
        
        let elements = [];
        for (const sel of selectors) {{
            const found = document.querySelectorAll(sel);
            if (found.length > 0) {{
                elements = Array.from(found);
                break;
            }}
        }}
        
        elements.forEach(el => {{
            try {{
                // Name
                let name = "";
                for (const sel of {json.dumps(config['name_selectors'])}) {{
                    const n = el.querySelector(sel);
                    if (n && n.textContent?.trim()) {{
                        name = n.textContent.trim();
                        break;
                    }}
                }}
                if (!name) name = el.textContent?.trim().substring(0, 100) || "";
                
                // Payout
                let payout = 0;
                for (const sel of {json.dumps(config['payout_selectors'])}) {{
                    const p = el.querySelector(sel);
                    if (p) {{
                        const text = p.textContent || p.getAttribute('data-payout') || '';
                        const match = text.match(/([\\d,.]+)\\s*\\$?/);
                        if (match) payout = parseFloat(match[1].replace(',', '.'));
                        break;
                    }}
                }}
                
                // Cap
                let cap = 0;
                for (const sel of {json.dumps(config['cap_selectors'])}) {{
                    const c = el.querySelector(sel);
                    if (c) {{
                        const text = c.textContent || c.getAttribute('data-cap') || '';
                        const match = text.match(/(\\d[\\d,.]*)/);
                        if (match) cap = parseInt(match[1].replace(/[,.]/g, ''));
                        break;
                    }}
                }}
                
                // Geo
                let offerGeo = "{geo}";
                for (const sel of {json.dumps(config['geo_selectors'])}) {{
                    const g = el.querySelector(sel);
                    if (g) {{
                        offerGeo = g.textContent?.trim() || g.getAttribute('data-geo') || offerGeo;
                        break;
                    }}
                }}
                
                // Vertical
                let vertical = "";
                for (const sel of {json.dumps(config['vertical_selectors'])}) {{
                    const v = el.querySelector(sel);
                    if (v) {{
                        vertical = v.textContent?.trim() || v.getAttribute('data-vertical') || "";
                        break;
                    }}
                }}
                
                // Lander URL
                let landerUrl = "";
                const link = el.querySelector('a[href*="land"], a[href*="preview"], a[href*="offer"], a[class*="view"]');
                if (link) landerUrl = link.href;
                
                // Restrictions
                const restrictions = [];
                const text = el.textContent?.toLowerCase() || "";
                if (text.includes('prelander') || text.includes('pre-land')) restrictions.push('prelander_required');
                if (text.includes('adult') || text.includes('18+')) restrictions.push('adult_only');
                if (text.includes('incent') || text.includes('no incent')) restrictions.push('no_incent');
                if (text.includes('cloak') || text.includes('cloaking')) restrictions.push('cloaking_allowed');
                
                // Offer ID
                const offerId = el.getAttribute('data-offer-id') || el.getAttribute('id') || 
                    `offer_${{Date.now()}}_${{Math.random().toString(36).substr(2,9)}}`;
                
                // Source URL
                const sourceUrl = window.location.href;
                
                if (name && !seen.has(name)) {{
                    seen.add(name);
                    offers.push({{
                        offer_id: offerId,
                        name: name,
                        vertical: vertical || "unknown",
                        geo: offerGeo,
                        payout: payout,
                        cap: cap,
                        lander_url: landerUrl,
                        restrictions: restrictions,
                        source_url: sourceUrl
                    }});
                }}
            }} catch (e) {{
                console.log('Error:', e);
            }}
        }});
        
        return offers;
        """
        
        raw_offers = js(extraction_js)
        
        offers = []
        for raw in raw_offers:
            try:
                # Filter by criteria
                if raw.get('payout', 0) < min_payout:
                    continue
                if raw.get('cap', 0) < min_cap:
                    continue
                
                offer = Offer(
                    offer_id=raw.get('offer_id', ''),
                    network=network,
                    name=raw.get('name', ''),
                    vertical=raw.get('vertical', 'unknown'),
                    geo=raw.get('geo', geo),
                    payout=raw.get('payout', 0),
                    flow="CPI",  # Would need to parse from page
                    cap_daily=raw.get('cap', 0),
                    lander_url=raw.get('lander_url', ''),
                    restrictions=raw.get('restrictions', []),
                    approval_difficulty=5,
                    source_url=raw.get('source_url', ''),
                    scraped_at=datetime.now(),
                    confidence_score=0.8
                )
                offers.append(offer)
            except Exception as e:
                continue
        
        return offers
    
    def scan_all_networks(self, geo: str = "IN", verticals: List[str] = None,
                          min_payout: float = 3.0, min_cap: int = 1000) -> Dict[str, List[Offer]]:
        """Scan all supported networks."""
        results = {}
        for network in self.NETWORK_CONFIGS.keys():
            print(f"Scanning {network}...")
            try:
                offers = self.scan_network(network, geo, verticals, min_payout, min_cap)
                results[network] = offers
                print(f"  Found {len(offers)} offers")
            except Exception as e:
                print(f"  Error scanning {network}: {e}")
                results[network] = []
        return results


if __name__ == "__main__":
    scanner = CPAOfferScanner()
    
    # Scan AdCombo for India
    offers = scanner.scan_network("adcombo", geo="IN", verticals=["gambling", "dating"], min_payout=3.0, min_cap=1000)
    
    print(f"Found {len(offers)} offers:")
    for o in offers:
        print(f"  {o.name} | {o.vertical} | ${o.payout} | Cap: {o.cap_daily} | Geo: {o.geo}")