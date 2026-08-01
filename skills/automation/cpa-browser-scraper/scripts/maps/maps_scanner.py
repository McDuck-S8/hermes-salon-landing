---
name: google_maps_scanner
description: Scan Google Maps for local businesses (salons, clinics, restaurants, etc.) to find landing page clients
---

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

from browser_harness.helpers import *


@dataclass
class LocalBiz:
    """Local business from Google Maps."""
    name: str
    phone: str
    address: str
    website: str = ""
    rating: float = 0.0
    review_count: int = 0
    photos: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    website_tech: List[str] = field(default_factory=list)
    has_website: bool = False
    website_quality_score: Optional[int] = None
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @property
    def needs_landing_page(self) -> bool:
        """Whether this biz needs a landing page (no site or bad site)."""
        if not self.website:
            return True
        if self.website_quality_score and self.website_quality_score < 5:
            return True
        return False


def scan_google_maps(query: str, max_results: int = 50, lang: str = "ru") -> List[LocalBiz]:
    """
    Scan Google Maps for local businesses matching query.
    
    Args:
        query: Search query like "салон красоты Позняки Киев" or "restaurants in Budva Montenegro"
        max_results: Maximum businesses to extract
        lang: Language code (ru, en, sr, hr, etc.)
    
    Returns:
        List of LocalBiz objects
    """
    from urllib.parse import quote
    
    search_url = f"https://www.google.com/maps/search/{quote(query)}"
    if lang:
        search_url += f"?hl={lang}"
    
    goto_url(search_url)
    wait_for_load()
    time.sleep(5)
    
    businesses = []
    scroll_count = 0
    max_scrolls = 30
    no_new_count = 0
    
    while len(businesses) < max_results and scroll_count < max_scrolls:
        page_businesses = _extract_maps_cards()
        
        # Deduplicate by name + address
        for biz in page_businesses:
            if len(businesses) >= max_results:
                break
            if not any(existing.name == biz.name and existing.address == biz.address for existing in businesses):
                businesses.append(biz)
        
        prev_count = len(businesses)
        
        # Scroll down
        js("window.scrollBy(0, 3000)")
        time.sleep(2)
        scroll_count += 1
        
        if len(businesses) == prev_count:
            no_new_count += 1
            if no_new_count >= 3:
                break
        else:
            no_new_count = 0
    
    return businesses[:max_results]


def _extract_maps_cards() -> List[LocalBiz]:
    """Extract business cards from Google Maps left panel."""
    
    extraction_js = """
    const cards = document.querySelectorAll('[role="article"], [class*="Nv2PK"], [class*="THOPZb"], [jsaction*="pane"]');
    const businesses = [];
    
    cards.forEach((card, i) => {
        try {
            // Name
            const nameEl = card.querySelector('[class*="fontHeadlineSmall"], [class*="qBF1Pd"], h3, [aria-label]');
            const name = nameEl?.textContent?.trim() || nameEl?.getAttribute('aria-label') || '';
            
            // Address
            const addrEl = card.querySelector('[class*="fontBodyMedium"], [class*="W4Efsd"], [data-value="address"]');
            const address = addrEl?.textContent?.trim() || '';
            
            // Phone
            const phoneEl = card.querySelector('[data-value="phone"], [class*="UsdlK"], a[href^="tel:"]');
            const phone = phoneEl?.textContent?.trim() || phoneEl?.getAttribute('href')?.replace('tel:', '') || '';
            
            // Rating
            const ratingEl = card.querySelector('[role="img"][aria-label*="star"], [class*="MW4etd"], [class*="F7nice"]');
            let rating = 0.0;
            if (ratingEl) {
                const ratingText = ratingEl.getAttribute('aria-label') || ratingEl.textContent || '';
                const match = ratingText.match(/([0-9.]+)/);
                if (match) rating = parseFloat(match[1]);
            }
            
            // Review count
            const reviewsEl = card.querySelector('[class*="UY7F9"], [aria-label*="review"]');
            let reviewCount = 0;
            if (reviewsEl) {
                const revText = reviewsEl.textContent || reviewsEl.getAttribute('aria-label') || '';
                const match = revText.match(/([0-9,]+)/);
                if (match) reviewCount = parseInt(match[1].replace(',', ''));
            }
            
            // Categories
            const catEl = card.querySelector('[class*="W4Efsd"]:not([data-value="address"])');
            const categories = catEl?.textContent?.trim().split('·').map(c => c.trim()) || [];
            
            // Website link
            const websiteEl = card.querySelector('a[href^="http"]:not([href*="google.com"])');
            const website = websiteEl?.href || '';
            
            // Photos count
            const photoEl = card.querySelector('[class*="photo"], [class*="image"]');
            const photos = photoEl ? 1 : 0; // Simplified
            
            if (name && name.length > 2) {
                businesses.push({
                    name: name,
                    phone: phone,
                    address: address,
                    website: website,
                    rating: rating,
                    review_count: reviewCount,
                    photos: photos,
                    categories: categories,
                    has_website: !!website,
                    source_url: window.location.href
                });
            }
        } catch (e) {}
    });
    
    return businesses;
    """
    
    raw_businesses = js(extraction_js)
    
    from datetime import datetime
    businesses = []
    for raw in raw_businesses:
        try:
            biz = LocalBiz(
                name=raw.get('name', ''),
                phone=raw.get('phone', ''),
                address=raw.get('address', ''),
                website=raw.get('website', ''),
                rating=float(raw.get('rating', 0.0)),
                review_count=int(raw.get('review_count', 0)),
                photos=[str(raw.get('photos', 0))],
                categories=raw.get('categories', []),
                has_website=raw.get('has_website', False),
                website_quality_score=None,
                scraped_at=datetime.now().isoformat(),
                raw_data=raw
            )
            businesses.append(biz)
        except Exception as e:
            continue
    
    return businesses


def analyze_website_quality(url: str) -> Dict[str, Any]:
    """Analyze a business website for quality score and tech stack."""
    if not url:
        return {"quality_score": 0, "tech_stack": [], "has_ssl": False, "mobile_friendly": False}
    
    goto_url(url)
    wait_for_load()
    time.sleep(3)
    
    analysis = js("""
    const analysis = {
        quality_score: 5,
        tech_stack: [],
        has_ssl: window.location.protocol === 'https:',
        mobile_friendly: false,
        load_time_estimate: 0,
        issues: []
    };
    
    // Mobile friendly checks
    const viewport = document.querySelector('meta[name="viewport"]');
    analysis.mobile_friendly = !!viewport;
    
    // SSL
    analysis.has_ssl = window.location.protocol === 'https:';
    
    // Tech stack
    const scripts = Array.from(document.querySelectorAll('script[src]')).map(s => s.src);
    const inline = Array.from(document.querySelectorAll('script:not([src])')).map(s => s.textContent).join(' ');
    const allScripts = scripts.join(' ') + ' ' + inline;
    
    const techSignatures = {
        'wordpress': ['wp-content', 'wp-includes', 'wordpress'],
        'elementor': ['elementor'],
        'wix': ['wix.com', 'wixstatic.com'],
        'squarespace': ['squarespace.com', 'static.squarespace.com'],
        'shopify': ['shopify.com', 'cdn.shopify.com'],
        'webflow': ['webflow.io', 'webflow.js'],
        'framer': ['framer.com', 'framer-motion'],
        'nextjs': ['_next/', 'next.js'],
        'nuxt': ['_nuxt/', 'nuxt.js'],
        'react': ['react.', 'react-dom'],
        'vue': ['vue.', 'vue-router'],
        'angular': ['angular.', 'ng-'],
        'bootstrap': ['bootstrap'],
        'tailwind': ['tailwind'],
        'jquery': ['jquery'],
        'google_fonts': ['fonts.googleapis.com', 'fonts.gstatic.com'],
        'fontawesome': ['fontawesome', 'font-awesome'],
        'recaptcha': ['recaptcha', 'grecaptcha'],
        'hcaptcha': ['hcaptcha'],
        'hotjar': ['hotjar.com'],
        'clarity': ['clarity.ms'],
        'ga4': ['gtag(', 'google-analytics.com', 'googletagmanager.com'],
        'fb_pixel': ['connect.facebook.net', 'fbq('],
        'tiktok_pixel': ['analytics.tiktok.com', 'ttq.'],
        'yandex_metrika': ['mc.yandex.ru', 'ym('],
        'chat_widget': ['tawk.to', 'crisp.chat', 'intercom.io', 'zendesk', 'jivosite'],
        'booking': ['calendly', 'cal.com', 'simplybook', 'bookly'],
        'payment': ['stripe.com', 'paypal.com', 'yookassa', 'cloudpayments']
    };
    
    tech_stack = [];
    for (const [tech, signatures] of Object.entries(techSignatures)) {
        for (const sig of signatures) {
            if (allScripts.toLowerCase().includes(sig.toLowerCase())) {
                tech_stack.push(tech);
                break;
            }
        }
    }
    analysis.tech_stack = tech_stack;
    
    // Quality heuristics
    let score = 5;
    
    // Positive factors
    if (analysis.has_ssl) score += 1;
    if (analysis.mobile_friendly) score += 1;
    if (document.querySelector('h1')) score += 1;
    if (document.querySelectorAll('img').length > 0) score += 1;
    if (document.querySelector('a[href^="tel:"]') || document.querySelector('a[href^="mailto:"]')) score += 1;
    if (document.querySelector('form')) score += 1;
    if (document.querySelector('[class*="map"], [id*="map"]')) score += 1;
    if (tech_stack.includes('wordpress') || tech_stack.includes('webflow') || tech_stack.includes('framer')) score += 1;
    
    // Negative factors
    if (document.querySelectorAll('img').length === 0) score -= 2;
    if (!document.querySelector('h1')) score -= 1;
    if (document.querySelector('[class*="under-construction"], [class*="coming-soon"]')) score -= 3;
    if (document.body.textContent.length < 500) score -= 2;
    if (!analysis.has_ssl) score -= 2;
    if (!analysis.mobile_friendly) score -= 2;
    
    analysis.quality_score = Math.max(0, Math.min(10, score));
    
    // Issues
    if (!analysis.has_ssl) analysis.issues.push('No SSL');
    if (!analysis.mobile_friendly) analysis.issues.push('No viewport meta');
    if (document.body.textContent.length < 500) analysis.issues.push('Thin content');
    if (!document.querySelector('h1')) analysis.issues.push('Missing H1');
    if (!document.querySelector('a[href^="tel:"]')) analysis.issues.push('No click-to-call');
    if (!document.querySelector('form')) analysis.issues.push('No contact form');
    
    return analysis;
    """)
    
    return analysis


def enrich_business_with_website(biz: LocalBiz) -> LocalBiz:
    """Enrich business data with website analysis."""
    if biz.website:
        analysis = analyze_website_quality(biz.website)
        biz.website_quality_score = analysis.get('quality_score')
        biz.website_tech = analysis.get('tech_stack', [])
        biz.has_website = True
        biz.raw_data['website_analysis'] = analysis
    return biz


def scan_area_for_leads(query: str, max_results: int = 50, analyze_websites: bool = True) -> List[LocalBiz]:
    """
    Complete pipeline: scan maps -> enrich with website analysis -> filter for leads.
    
    Returns businesses that need landing pages (no website or bad website).
    """
    print(f"Scanning Google Maps for: {query}")
    businesses = scan_google_maps(query, max_results=max_results)
    print(f"Found {len(businesses)} businesses")
    
    if analyze_websites:
        print("Analyzing websites...")
        for i, biz in enumerate(businesses):
            if biz.website:
                print(f"  {i+1}/{len(businesses)}: {biz.name} - {biz.website}")
                enrich_business_with_website(biz)
            else:
                print(f"  {i+1}/{len(businesses)}: {biz.name} - NO WEBSITE")
    
    # Filter for leads
    leads = [b for b in businesses if b.needs_landing_page]
    print(f"Found {len(leads)} leads needing landing pages")
    
    return leads


# Example queries for different markets
QUERIES = {
    "kiev_salons": "салон красоты Позняки Киев",
    "kiev_dental": "стоматология Позняки Киев",
    "kiev_fitness": "фитнес клуб Позняки Киев",
    "budva_restaurants": "restaurants in Budva Montenegro",
    "budva_hotels": "hotels in Budva Montenegro",
    "budva_salons": "beauty salon in Budva Montenegro",
    "budva_clinics": "clinic in Budva Montenegro",
    "belgrade_salons": "салон красоти Београд",
    "belgrade_dental": "стоматология Београд",
}


if __name__ == "__main__":
    # Test with Kiev salons
    leads = scan_area_for_leads(
        query="салон красоты Позняки Киев",
        max_results=20,
        analyze_websites=True
    )
    
    for lead in leads:
        print(f"\n{lead.name}")
        print(f"  Phone: {lead.phone}")
        print(f"  Address: {lead.address}")
        print(f"  Website: {lead.website or 'NONE'}")
        print(f"  Rating: {lead.rating} ({lead.review_count} reviews)")
        print(f"  Quality: {lead.website_quality_score}/10")
        print(f"  Tech: {lead.website_tech}")
        print(f"  NEEDS LP: {lead.needs_landing_page}")