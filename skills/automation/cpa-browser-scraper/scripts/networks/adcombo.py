"""
AdCombo network scraper using browser-harness (CDP).
"""
import sys
sys.path.insert(0, '/d/Portable_Soft/hermes/browser-harness/src')

from browser_harness.helpers import *
from scripts.models import Offer
from datetime import datetime
from typing import List, Dict, Any
import re


def scan_adcombo_offers(geo: str = "IN", vertical: str = "gambling", max_pages: int = 3) -> List[Offer]:
    """
    Navigate to AdCombo offers page, filter by geo/vertical, extract offer cards.
    
    Args:
        geo: Target country code (IN, BR, US, DE, etc.)
        vertical: Vertical name (gambling, dating, nutra, finance, etc.)
        max_pages: Number of pagination pages to scan
    
    Returns:
        List of Offer objects
    """
    offers = []
    
    # Navigate to offers page with filters
    base_url = "https://www.adcombo.com/offers"
    params = f"?geo={geo}&vertical={vertical}"
    goto_url(f"{base_url}{params}")
    wait_for_load()
    
    # Wait for offer cards to load
    import time
    time.sleep(3)
    
    for page in range(max_pages):
        # Extract offer cards from current page
        page_offers = _extract_adcombo_offers(geo, vertical)
        offers.extend(page_offers)
        
        # Try to go to next page
        if page < max_pages - 1:
            if not _click_next = js("""
    const nextBtn = document.querySelector('[class*="pagination"] [class*="next"], a[rel="next"], button:contains("Next")');
    if (nextBtn) { nextBtn.click(); return true; }
    return false;
""")
            if not click_next:
                break
            wait_for_load()
            time.sleep(2)
    
    return offers


def _extract_adcombo_offers(geo: str, vertical: str) -> List[Offer]:
    """Extract offer data from AdCombo offer cards on current page."""
    
    extraction_js = """
    const cards = document.querySelectorAll('[class*="offer-card"], [class*="offer-item"], .offer, [data-offer-id]');
    const offers = [];
    
    cards.forEach(card => {
        try {
            // Try multiple selectors for each field
            const name = card.querySelector('[class*="name"], [class*="title"], h3, h4, .offer-name')?.textContent?.trim() || '';
            const payoutText = card.querySelector('[class*="payout"], [class*="price"], [class*="rate"]')?.textContent || '';
            const payout = parseFloat(payoutText.replace(/[^0-9.]/g, '')) || 0;
            
            const flow = card.querySelector('[class*="flow"], [class*="type"], [class*="conversion"]')?.textContent?.trim() || '';
            const capText = card.querySelector('[class*="cap"], [class*="limit"]')?.textContent || '';
            const cap = parseInt(capText.replace(/[^0-9]/g, '')) || 0;
            
            const landerLink = card.querySelector('a[href*="lander"], a[href*="preview"], a[href*="offer"]')?.href || '';
            const offerId = card.getAttribute('data-offer-id') || card.getAttribute('data-id') || '';
            
            const restrictions = [];
            const restText = card.querySelector('[class*="restriction"], [class*="note"], [class*="tag"]')?.textContent || '';
            if (restText.toLowerCase().includes('preland')) restrictions.push('prelander_required');
            if (restText.toLowerCase().includes('adult')) restrictions.push('adult_only');
            if (restText.toLowerCase().includes('incent')) restrictions.push('no_incent');
            
            if (name && payout > 0) {
                offers.push({
                    offer_id: offerId || `adcombo_${Date.now()}_${Math.random().toString(36).substr(2,9)}`,
                    name: name,
                    vertical: vertical,
                    geo: geo,
                    payout: payout,
                    flow: flow || 'CPA',
                    cap_daily: cap,
                    lander_url: landerLink,
                    restrictions: restrictions,
                    source_url: window.location.href
                });
            }
        } catch (e) {
            console.log('Error extracting card:', e);
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
                network='AdCombo',
                name=raw.get('name', ''),
                vertical=raw.get('vertical', vertical),
                geo=raw.get('geo', geo),
                payout=float(raw.get('payout', 0)),
                flow=raw.get('flow', 'CPA'),
                cap_daily=int(raw.get('cap_daily', 0)),
                lander_url=raw.get('lander_url', ''),
                restrictions=raw.get('restrictions', []),
                source_url=raw.get('source_url', '')
            )
            offers.append(offer)
        except Exception as e:
            print(f"Error creating Offer: {e}")
            continue
    
    return offers


def get_adcombo_offer_details(offer_url: str) -> Dict[str, Any]:
    """Get detailed info for a specific offer by visiting its page."""
    goto_url(offer_url)
    wait_for_load()
    import time
    time.sleep(2)
    
    details_js = """
    const details = {};
    
    // Description
    details.description = document.querySelector('[class*="description"], [class*="desc"]')?.textContent?.trim() || '';
    
    // Landing page preview links
    const landerLinks = Array.from(document.querySelectorAll('a[href*="lander"], a[href*="preview"], a[href*="landing"]'));
    details.lander_urls = landerLinks.map(a => a.href).filter(Boolean);
    
    // Creative examples
    const creatives = Array.from(document.querySelectorAll('[class*="creative"], [class*="banner"], img[src*="creative"], img[src*="banner"]'));
    details.creative_urls = creatives.map(c => c.src || c.href).filter(Boolean);
    
    // Restrictions/tags
    const tags = Array.from(document.querySelectorAll('[class*="tag"], [class*="badge"], [class*="label"]'));
    details.tags = tags.map(t => t.textContent?.trim()).filter(Boolean);
    
    // Approval requirements
    const approvalText = document.querySelector('[class*="approval"], [class*="requirement"]')?.textContent || '';
    details.approval_requirements = approvalText;
    
    return details;
    """
    
    return js(details_js)


def scan_adcombo_by_category(category: str, geo: str = "IN", max_pages: int = 5) -> List[Offer]:
    """Scan AdCombo offers by category (gambling, dating, nutra, finance, etc.)"""
    return scan_adcombo_offers(geo=geo, vertical=category, max_pages=max_pages)


if __name__ == "__main__":
    # Test run
    offers = scan_adcombo_offers(geo="IN", vertical="gambling", max_pages=2)
    for o in offers:
        print(f"Offer: {o.name} | Payout: ${o.payout} | Flow: {o.flow} | Cap: {o.cap_daily}/day")
        print(f"  Lander: {o.lander_url}")
        print(f"  ROI Est: {o.roi_estimate:.1f}%")