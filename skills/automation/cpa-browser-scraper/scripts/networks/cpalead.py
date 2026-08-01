---
name: cpalead_scanner
description: CPAlead marketplace scanner
---

from dataclasses import dataclass
from typing import List, Dict, Any
import json
import time

from browser_harness.helpers import *


@dataclass
class Offer:
    offer_id: str
    network: str
    name: str
    vertical: str
    geo: str
    payout: float
    flow: str
    cap_daily: int
    lander_url: str
    restrictions: List[str]
    source_url: str
    creative_angles: List[str]


def scan_cpalead_offers(geo: str = "IN", vertical: str = "gaming", max_pages: int = 3) -> List[Offer]:
    """Scan CPAlead marketplace for offers."""
    
    # CPAlead marketplace URL
    marketplace_url = f"https://www.cpalead.com/offers?geo={geo}&category={vertical}"
    
    goto_url(marketplace_url)
    wait_for_load()
    time.sleep(3)
    
    offers = []
    
    for page in range(max_pages):
        # Extract offers from current page
        page_offers = _extract_cpalead_offers(geo, vertical)
        offers.extend(page_offers)
        
        # Try to go to next page
        next_clicked = js("""
            const nextBtn = document.querySelector('[class*="next"], [class*="pagination"] a:last-child, button:contains("Next")');
            if (nextBtn && !nextBtn.disabled) {
                nextBtn.click();
                return true;
            }
            return false;
        """)
        
        if not next_clicked:
            break
            
        wait_for_load()
        time.sleep(2)
    
    return offers


def _extract_cpalead_offers(geo: str, vertical: str) -> List[Offer]:
    """Extract CPAlead offer data from current page."""
    
    extraction_js = """
    const cards = document.querySelectorAll('[class*="offer"], [class*="campaign"], .offer-card, .campaign-item, tr[class*="offer"]');
    const offers = [];
    
    cards.forEach(card => {
        try {
            const name = card.querySelector('[class*="name"], [class*="title"], .offer-name, .campaign-name')?.textContent?.trim() || '';
            const payoutText = card.querySelector('[class*="payout"], [class*="earning"], [class*="rate"]')?.textContent || '';
            const payout = parseFloat(payoutText.replace(/[^0-9.]/g, '')) || 0;
            
            const flow = card.querySelector('[class*="type"], [class*="conversion"]')?.textContent?.trim() || 'CPA';
            
            const capText = card.querySelector('[class*="cap"], [class*="limit"]')?.textContent || '';
            const cap = parseInt(capText.replace(/[^0-9]/g, '')) || 0;
            
            const landerLink = card.querySelector('a[href*="lander"], a[href*="preview"], a[href*="tracking"]')?.href || '';
            
            const offerId = card.getAttribute('data-offer-id') || card.getAttribute('data-id') || `cpalead_${Date.now()}_${Math.random().toString(36).substr(2,9)}`;
            
            const restrictions = [];
            const restText = card.textContent?.toLowerCase() || '';
            if (restText.includes('preland') || restText.includes('pre-land')) restrictions.push('prelander_required');
            if (restText.includes('adult')) restrictions.push('adult_only');
            if (restText.includes('incent')) restrictions.push('no_incent');
            
            if (name && payout > 0) {
                offers.push({
                    offer_id: offerId,
                    name: name,
                    vertical: vertical,
                    geo: geo,
                    payout: payout,
                    flow: flow,
                    cap_daily: cap,
                    lander_url: landerLink,
                    restrictions: restrictions,
                    source_url: window.location.href
                });
            }
        } catch (e) {
            console.log('Error:', e);
        }
    });
    
    return offers;
    """
    
    raw_offers = js(extraction_js)
    
    offers = []
    for raw in raw_offers:
        try:
            offer = Offer(
                offer_id=raw.get('offer_id', ''),
                network='CPAlead',
                name=raw.get('name', ''),
                vertical=raw.get('vertical', vertical),
                geo=raw.get('geo', geo),
                payout=float(raw.get('payout', 0)),
                flow=raw.get('flow', 'CPA'),
                cap_daily=int(raw.get('cap_daily', 0)),
                lander_url=raw.get('lander_url', ''),
                restrictions=raw.get('restrictions', []),
                source_url=raw.get('source_url', ''),
                creative_angles=[]
            )
            offers.append(offer)
        except Exception as e:
            continue
    
    return offers


if __name__ == "__main__":
    offers = scan_cpalead_offers(geo="IN", vertical="gaming", max_pages=2)
    for o in offers:
        print(f"Offer: {o.name} | Payout: ${o.payout} | Flow: {o.flow} | Cap: {o.cap_daily}/day")