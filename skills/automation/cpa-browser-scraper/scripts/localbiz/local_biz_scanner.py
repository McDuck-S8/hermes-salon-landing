"""
Google Maps Local Business Scanner
Scans Google Maps for local businesses (salons, restaurants, clinics, etc.)
using browser-harness CDP connection to YOUR Chrome.
"""

import sys
import time
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "browser-harness" / "src"))

from browser_harness.helpers import *


@dataclass
class LocalBusiness:
    business_id: str
    name: str
    phone: str
    address: str
    website: str
    rating: float
    review_count: int
    categories: List[str]
    has_website: bool
    website_tech: List[str]
    photos_count: int
    coordinates: Dict[str, float]
    place_id: str
    scraped_at: str
    # Sales Machine fields
    country: str = ""
    city: str = ""
    language: str = "ru"
    niche: str = "beauty"  # beauty, restaurant, hotel, auto, clinic
    website_status: str = "none"  # none, bad, good
    contact_email: str = ""
    social_media: Dict[str, str] = None
    
    def __post_init__(self):
        if self.social_media is None:
            self.social_media = {}


class LocalBizScanner:
    """Scans Google Maps for local businesses in target area."""
    
    def __init__(self):
        self.businesses = []
    
    def scan_area(self, query: str, max_results: int = 50, 
                  country: str = "", city: str = "", language: str = "ru") -> List[Dict]:
        """Scan Google Maps for businesses matching query."""
        
        # Build search URL
        search_query = query.replace(" ", "+")
        url = f"https://www.google.com/maps/search/{search_query}"
        print(f"Scanning: {url}")
        
        goto_url(url)
        wait_for_load()
        time.sleep(3)
        
        # Scroll to load results
        for i in range(8):
            scroll("down", 5)
            time.sleep(1)
        
        # Extract business cards
        raw_bizs = js(self._get_extraction_js())
        businesses = self._parse_businesses(raw_bizs, country, city, language)
        
        # Limit results
        businesses = businesses[:max_results]
        
        # Enrich each business (optional - visit their place page)
        for biz in businesses:
            self._enrich_business(biz)
        
        self.businesses.extend(businesses)
        return businesses
    
    def _get_extraction_js(self) -> str:
        return """
        const businesses = [];
        const seen = new Set();
        
        // Google Maps business cards
        const cards = document.querySelectorAll('[role="article"], [data-result-index], [class*="Nv2PK"], [class*="THOPZb"], [jsaction*="pane"]');
        
        cards.forEach(card => {
            try {
                // Get unique identifier
                const placeId = card.getAttribute('data-place-id') || 
                    card.getAttribute('data-result-index') || 
                    `biz_${Date.now()}_${Math.random().toString(36).substr(2,9)}`;
                
                if (seen.has(placeId)) return;
                seen.add(placeId);
                
                const biz = {
                    name: "",
                    phone: "",
                    address: "",
                    website: "",
                    rating: 0,
                    review_count: 0,
                    categories: [],
                    photos_count: 0,
                    coordinates: {lat: 0, lng: 0},
                    place_id: placeId
                };
                
                // Name
                const nameSelectors = ['[class*="fontHeadlineLarge"]', '[class*="fontHeadlineMedium"]', 'h1', '[role="heading"]', '[class*="title"]'];
                for (const sel of nameSelectors) {
                    const el = card.querySelector(sel);
                    if (el && el.textContent?.trim()) {
                        biz.name = el.textContent.trim();
                        break;
                    }
                }
                
                // Rating
                const ratingEl = card.querySelector('[role="img"][aria-label*="star"], [class*="rating"], [aria-label*="star"]');
                if (ratingEl) {
                    const label = ratingEl.getAttribute('aria-label') || ratingEl.textContent || '';
                    const match = label.match(/([\\d.]+)/);
                    if (match) biz.rating = parseFloat(match[1]);
                }
                
                // Review count
                const reviewEl = card.querySelector('[aria-label*="review"], [class*="review"]');
                if (reviewEl) {
                    const text = reviewEl.textContent || '';
                    const match = text.match(/([\\d,]+)/);
                    if (match) biz.review_count = parseInt(match[1].replace(/,/g, ''));
                }
                
                // Address
                const addrSelectors = ['[class*="address"]', '[data-value="address"]', '[class*="location"]'];
                for (const sel of addrSelectors) {
                    const el = card.querySelector(sel);
                    if (el && el.textContent?.trim()) {
                        biz.address = el.textContent.trim();
                        break;
                    }
                }
                
                // Phone
                const phoneEl = card.querySelector('[data-value="phone"], [href^="tel:"], [class*="phone"]');
                if (phoneEl) {
                    biz.phone = phoneEl.textContent?.trim() || phoneEl.getAttribute('href')?.replace('tel:', '') || '';
                }
                
                // Website
                const siteEl = card.querySelector('[href^="http"]:not([href*="google"]):not([href*="maps"])');
                if (siteEl) biz.website = siteEl.href;
                
                // Categories
                const catEl = card.querySelector('[class*="category"], [class*="type"]');
                if (catEl) {
                    biz.categories = catEl.textContent.split('·').map(s => s.trim()).filter(Boolean);
                }
                
                // Place ID / link
                const linkEl = card.querySelector('a[href*="/maps/place/"]');
                if (linkEl) {
                    const href = linkEl.href;
                    const match = href.match(/place\\/([^\\/]+)/);
                    if (match) biz.place_id = match[1];
                }
                
                // Coordinates from link
                const coordLink = card.querySelector('a[href*="@"]');
                if (coordLink) {
                    const match = coordLink.href.match(/@([-\\d.]+),([-\\d.]+)/);
                    if (match) {
                        biz.coordinates = {lat: parseFloat(match[1]), lng: parseFloat(match[2])};
                    }
                }
                
                if (biz.name) businesses.push(biz);
            } catch (e) {
                console.log('Error:', e);
            }
        });
        
        return businesses;
        """
    
    def _parse_businesses(self, raw_bizs: List[Dict], country: str, city: str, language: str) -> List[LocalBusiness]:
        """Parse raw businesses into LocalBusiness objects."""
        businesses = []
        for raw in raw_bizs:
            try:
                biz = LocalBusiness(
                    business_id=raw.get('place_id', f"biz_{len(self.businesses)}"),
                    name=raw.get('name', ''),
                    phone=raw.get('phone', ''),
                    address=raw.get('address', ''),
                    website=raw.get('website', ''),
                    rating=raw.get('rating', 0),
                    review_count=raw.get('review_count', 0),
                    categories=raw.get('categories', []),
                    has_website=bool(raw.get('website')),
                    website_tech=[],
                    photos_count=0,
                    coordinates=raw.get('coordinates', {}),
                    place_id=raw.get('place_id', ''),
                    scraped_at=datetime.now().isoformat(),
                    country=country,
                    city=city,
                    language=language,
                    niche=self._detect_niche(raw.get('categories', [])),
                    website_status="none"
                )
                
                if biz.has_website:
                    biz.website_status = "unknown"  # Will be updated by enrich
                
                businesses.append(biz)
            except Exception as e:
                continue
        return businesses
    
    def _detect_niche(self, categories: List[str]) -> str:
        """Detect business niche from categories."""
        cat_text = " ".join(categories).lower()
        if any(k in cat_text for k in ['salon', 'beauty', 'hair', 'nail', 'spa', 'cosmet']):
            return "beauty"
        if any(k in cat_text for k in ['restaurant', 'cafe', 'food', 'pizza', 'burger', 'sushi']):
            return "restaurant"
        if any(k in cat_text for k in ['hotel', 'hostel', 'apartment', 'resort']):
            return "hotel"
        if any(k in cat_text for k in ['auto', 'car', 'repair', 'service', 'mechanic']):
            return "auto"
        if any(k in cat_text for k in ['clinic', 'dental', 'medical', 'doctor', 'health']):
            return "clinic"
        return "other"
    
    def _enrich_business(self, biz: LocalBusiness):
        """Visit business place page to get more details (website, email, social)."""
        if not biz.place_id:
            return
        
        try:
            # Go to place page
            place_url = f"https://www.google.com/maps/place/?q=place_id:{biz.place_id}"
            goto_url(place_url)
            wait_for_load()
            time.sleep(2)
            
            # Extract more details
            enrichment = js("""
                const data = {
                    website: "",
                    email: "",
                    phone: "",
                    social: {},
                    photos: 0,
                    hours: {}
                };
                
                // Website
                const siteBtn = document.querySelector('[data-item-id="authority"], [data-item-id="website"], a[href^="http"]:not([href*="google"]):not([href*="maps"])');
                if (siteBtn) data.website = siteBtn.href || siteBtn.textContent.trim();
                
                // Phone
                const phoneBtn = document.querySelector('[data-item-id="phone"], [href^="tel:"]');
                if (phoneBtn) data.phone = phoneBtn.href?.replace('tel:', '') || phoneBtn.textContent?.trim();
                
                // Email (rare on Maps but check)
                const pageText = document.body.textContent;
                const emailMatch = pageText.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-z]{2,}/);
                if (emailMatch) data.email = emailMatch[0];
                
                // Social media
                const socialLinks = document.querySelectorAll('a[href*="facebook"], a[href*="instagram"], a[href*="vk"], a[href*="telegram"], a[href*="whatsapp"]');
                socialLinks.forEach(a => {
                    const href = a.href;
                    if (href.includes('facebook')) data.social.facebook = href;
                    else if (href.includes('instagram')) data.social.instagram = href;
                    else if (href.includes('vk.com')) data.social.vk = href;
                    else if (href.includes('telegram')) data.social.telegram = href;
                    else if (href.includes('whatsapp')) data.social.whatsapp = href;
                });
                
                // Photos count
                const photoBtn = document.querySelector('[data-item-id="photos"], [aria-label*="photo"]');
                if (photoBtn) {
                    const text = photoBtn.textContent || '';
                    const match = text.match(/(\\d+)/);
                    if (match) data.photos = parseInt(match[1]);
                }
                
                // Opening hours
                const hoursSection = document.querySelector('[data-item-id="hours"], [class*="hours"]');
                if (hoursSection) data.hours = hoursSection.textContent.trim();
                
                return data;
            """)
            
            if enrichment.get('website'):
                biz.website = enrichment['website']
                biz.has_website = True
                biz.website_status = "unknown"
            
            if enrichment.get('email'):
                biz.contact_email = enrichment['email']
            
            if enrichment.get('phone'):
                biz.phone = enrichment['phone']
            
            biz.social_media = enrichment.get('social', {})
            biz.photos_count = enrichment.get('photos', 0)
            
        except Exception as e:
            pass
    
    def assess_website_quality(self, biz: LocalBusiness):
        """Visit website and assess quality/tech stack."""
        if not biz.website:
            biz.website_status = "none"
            return
        
        try:
            goto_url(biz.website)
            wait_for_load()
            time.sleep(2)
            
            tech = js("""
                const tech = [];
                
                // CMS detection
                if (document.querySelector('meta[name="generator"][content*="WordPress"]')) tech.push('wordpress');
                if (document.querySelector('script[src*="wp-content"], link[href*="wp-content"]')) tech.push('wordpress');
                if (document.querySelector('meta[name="generator"][content*="Joomla"]')) tech.push('joomla');
                if (document.querySelector('script[src*="drupal"]')) tech.push('drupal');
                
                // Builders
                if (document.querySelector('script[src*="elementor"], link[href*="elementor"]')) tech.push('elementor');
                if (document.querySelector('script[src*="wix"], link[href*="wix"]')) tech.push('wix');
                if (document.querySelector('script[src*="tilda"], link[href*="tilda"]')) tech.push('tilda');
                if (document.querySelector('[data-w-webflow]')) tech.push('webflow');
                if (document.querySelector('script[src*="framer"]')) tech.push('framer');
                
                // Frameworks
                if (window.React || document.querySelector('[data-reactroot]')) tech.push('react');
                if (window.Vue || document.querySelector('[data-v-]')) tech.push('vue');
                if (window.angular) tech.push('angular');
                
                // Analytics/Tracking
                if (window.fbq) tech.push('facebook_pixel');
                if (window.ttq) tech.push('tiktok_pixel');
                if (window.gtag || window.ga) tech.push('google_analytics');
                if (window.yaCounter || window.Ya) tech.push('yandex_metrica');
                
                // Mobile friendly
                const viewport = document.querySelector('meta[name="viewport"]');
                const mobile_friendly = !!viewport && viewport.content.includes('width=device-width');
                
                // Page speed hint
                const loadTime = performance.now();
                
                return {tech, mobile_friendly, load_time: loadTime};
            """)
            
            biz.website_tech = tech.get('tech', [])
            biz.mobile_friendly = tech.get('mobile_friendly', False)
            
            # Assess quality
            if len(tech.get('tech', [])) > 2 or tech.get('mobile_friendly'):
                biz.website_status = "good"
            elif tech.get('tech'):
                biz.website_status = "bad"
            else:
                biz.website_status = "unknown"
                
        except Exception as e:
            biz.website_status = "error"
    
    def save_businesses(self, filepath: str):
        """Save businesses to JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([asdict(b) for b in self.businesses], f, ensure_ascii=False, indent=2)
    
    def get_stats(self) -> Dict:
        """Get statistics about scanned businesses."""
        total = len(self.businesses)
        if total == 0:
            return {}
        
        with_site = sum(1 for b in self.businesses if b.has_website)
        good_sites = sum(1 for b in self.businesses if b.website_status == "good")
        bad_sites = sum(1 for b in self.businesses if b.website_status == "bad")
        no_site = total - with_site
        
        by_niche = {}
        for b in self.businesses:
            by_niche[b.niche] = by_niche.get(b.niche, 0) + 1
        
        return {
            "total": total,
            "with_website": with_site,
            "no_website": no_site,
            "good_website": good_sites,
            "bad_website": bad_sites,
            "website_penetration": round(with_site / total * 100, 1),
            "by_niche": by_niche
        }


if __name__ == "__main__":
    scanner = LocalBizScanner()
    
    # Scan beauty salons in Budva, Montenegro
    print("Scanning beauty salons in Budva, Montenegro...")
    businesses = scanner.scan_area(
        query="салон красоты Будва Черногория",
        max_results=30,
        country="ME",
        city="Budva",
        language="ru"
    )
    
    print(f"Found {len(businesses)} businesses")
    
    # Enrich and assess websites
    for biz in businesses:
        if biz.has_website:
            scanner.assess_website_quality(biz)
    
    # Save
    scanner.save_businesses("budva_beauty_salons.json")
    
    # Stats
    stats = scanner.get_stats()
    print(f"Stats: {stats}")