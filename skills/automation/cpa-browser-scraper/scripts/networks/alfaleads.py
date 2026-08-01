---
name: alfaleads_scanner
description: Alfaleads network scanner
---

from dataclasses import dataclass
from typing import List, Dict, Any
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
    approval_difficulty: int = 5  # 1-10


def scan_alfaleads_offers(geo: str = "IN", vertical: str = "gambling", max_pages: int = 3) -> List[Offer]:
    """Scan Alfaleads offers."""
    
    # Alfaleads offer directory (requires login usually)
    base_url = "https://alfaleads.com/offers"
    
    goto_url(base_url)
    wait_for_load()
    time.sleep(3)
    
    # Check if we need to login
    page_title = js("return document.title")
    if "login" in page_title.lower() or "sign in" in page_title.lower():
        print("Alfaleads requires login - please log in manually in Chrome")
        # Wait for manual login
        for i in range(30):
            time.sleep(2)
            current_url = js("return window.location.href")
            if "offers" in current_url and "login" not in current_url:
                break
    
    offers = []
    
    for page in range(max_pages):
        page_offers = _extract_alfaleads_offers(geo, vertical)
        offers.extend(page_offers)
        
        # Next page
        next_clicked = js("""
            const nextBtn = document.querySelector('a.page-link:contains("Next"), [class*="pagination"] a:last-child, button:contains("Next")');
            if (nextBtn && !nextBtn.disabled) { nextBtn.click(); return true; }
            return false;
        """)
        
        if not next_clicked:
            break
        wait_for_load()
        time.sleep(2)
    
    return offers


def _extract_alfaleads_offers(geo: str, vertical: str) -> List[Offer]:
    extraction_js = """
    const cards = document.querySelectorAll('[class*="offer"], .offer-card, .offer-item, tr.offer-row, [data-offer-id]');
    const offers = [];
    
    cards.forEach(card => {
        try {
            const name = card.querySelector('[class*="name"], [class*="title"], .offer-title, h3, h4')?.textContent?.trim() || '';
            const payoutText = card.querySelector('[class*="payout"], [class*="rate"], [class*="price"]')?.textContent || '';
            const payout = parseFloat(payoutText.replace(/[^0-9.]/g, '')) || 0;
            
            const flow = card.querySelector('[class*="type"], [class*="conversion"]')?.textContent?.trim() || 'CPA';
            
            const capText = card.querySelector('[class*="cap"], [class*="limit"]')?.textContent || '';
            const cap = parseInt(capText.replace(/[^0-9]/g, '')) || 0;
            
            const landerLink = card.querySelector('a[href*="lander"], a[href*="preview"], a[href*="land"]')?.href || '';
            
            const offerId = card.getAttribute('data-offer-id') || card.getAttribute('data-id') || `alfaleads_${Date.now()}_${Math.random().toString(36).substr(2,9)}`;
            
            const restrictions = [];
            const restText = card.textContent?.toLowerCase() || '';
            if (restText.includes('preland')) restrictions.push('prelander_required');
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
        } catch (e) {}
    });
    
    return offers;
    """
    
    raw_offers = js(extraction_js)
    
    offers = []
    for raw in raw_offers:
        try:
            offer = Offer(
                offer_id=raw.get('offer_id', ''),
                network='Alfaleads',
                name=raw.get('name', ''),
                vertical=raw.get('vertical', vertical),
                geo=raw.get('geo', geo),
                payout=float(raw.get('payout', 0)),
                flow=raw.get('flow', 'CPA'),
                cap_daily=int(raw.get('cap_daily', 0)),
                lander_url=raw.get('lander_url', ''),
                restrictions=raw.get('restrictions', []),
                source_url=raw.get('source_url', ''),
                approval_difficulty=5
            )
            offers.append(offer)
        except Exception as e:
            continue
    
    return offers


if __name__ == "__main__":
    offers = scan_alfaleads_offers(geo="IN", vertical="gambling", max_pages=1)
    for o in offers:
        print(f"Offer: {o.name} | Payout: ${o.payout} | Flow: {o.flow} | Cap: {o.cap_daily}/day")