---
name: fb_ad_library_scanner
description: Facebook Ad Library scraper for creative intelligence
---

from dataclasses import dataclass
from typing import List, Dict, Any
import time
import json

from browser_harness.helpers import *


@dataclass
class Creative:
    creative_id: str
    platform: str
    advertiser: str
    hook: str
    format: str
    cta: str
    lander_pattern: str
    impressions_est: int
    targeting_hints: List[str]
    source_url: str
    scraped_at: str


def scan_fb_ad_library(query: str = "cricket betting", country: str = "IN", 
                       ad_type: str = "all", active_status: str = "active",
                       max_results: int = 50) -> List[Creative]:
    """Scan Facebook Ad Library for creatives."""
    
    # Build FB Ad Library URL
    base_url = "https://www.facebook.com/ads/library/"
    params = {
        "active_status": active_status,
        "ad_type": ad_type,
        "country": country,
        "q": query,
        "media_type": "all"
    }
    
    from urllib.parse import urlencode
    url = f"{base_url}?{urlencode(params)}"
    
    goto_url(url)
    wait_for_load()
    time.sleep(5)  # FB takes time to load
    
    creatives = []
    scroll_count = 0
    max_scrolls = 20
    
    while len(creatives) < max_results and scroll_count < max_scrolls:
        # Extract visible ad cards
        page_creatives = _extract_fb_ad_cards()
        for c in page_creatives:
            if len(creatives) >= max_results:
                break
            # Deduplicate by creative_id
            if not any(existing.creative_id == c.creative_id for existing in creatives):
                creatives.append(c)
        
        # Scroll down
        js("window.scrollBy(0, 3000)")
        time.sleep(2)
        scroll_count += 1
    
    return creatives[:max_results]


def _extract_fb_ad_cards() -> List[Creative]:
    """Extract creative data from FB Ad Library cards."""
    
    extraction_js = """
    const cards = document.querySelectorAll('[data-testid="ad-card"], .x1n2onr6, [class*="ad-card"], [role="article"]');
    const creatives = [];
    
    cards.forEach((card, i) => {
        try {
            // Advertiser name
            const advertiser = card.querySelector('[class*="advertiser"], [class*="sponsor"], [data-testid="advertiser-name"]')?.textContent?.trim() || '';
            
            // Ad creative content
            const creativeText = card.querySelector('[class*="creative"], [class*="ad-text"], [data-testid="ad-creative"]')?.textContent?.trim() || '';
            const hook = creativeText.substring(0, 200);
            
            // Format detection
            let format = 'image';
            if (card.querySelector('video')) format = 'video';
            else if (card.querySelector('[class*="carousel"], [class*="gallery"]')) format = 'carousel';
            
            // CTA button
            const ctaBtn = card.querySelector('button, [role="button"]');
            const cta = ctaBtn?.textContent?.trim() || '';
            
            // Lander link
            const link = card.querySelector('a[href*="facebook.com"], a[href*="instagram.com"], a[href*="click"]')?.href || '';
            
            // Impressions (if visible)
            const impressionsText = card.querySelector('[class*="impression"], [class*="reach"]')?.textContent || '';
            const impressionsEst = parseInt(impressionsText.replace(/[^0-9]/g, '')) || 0;
            
            // Targeting hints
            const targetingHints = [];
            const targetingText = card.textContent?.toLowerCase() || '';
            if (targetingText.includes('age')) targetingHints.push('age_targeting');
            if (targetingText.includes('location') || targetingText.includes('country')) targetingHints.push('geo_targeting');
            if (targetingText.includes('interest')) targetingHints.push('interest_targeting');
            
            // Generate creative ID
            const creativeId = `fb_${advertiser.replace(/\\s+/g, '_')}_${i}_${Date.now()}`;
            
            if (advertiser || hook) {
                creatives.push({
                    creative_id: creativeId,
                    platform: 'fb_library',
                    advertiser: advertiser,
                    hook: hook,
                    format: format,
                    cta: cta,
                    lander_pattern: link,
                    impressions_est: impressionsEst,
                    targeting_hints: targetingHints,
                    source_url: window.location.href
                });
            }
        } catch (e) {
            console.log('Error extracting card:', e);
        }
    });
    
    return creatives;
    """
    
    raw_creatives = js(extraction_js)
    
    from datetime import datetime
    creatives = []
    for raw in raw_creatives:
        try:
            creative = Creative(
                creative_id=raw.get('creative_id', ''),
                platform=raw.get('platform', 'fb_library'),
                advertiser=raw.get('advertiser', ''),
                hook=raw.get('hook', ''),
                format=raw.get('format', 'image'),
                cta=raw.get('cta', ''),
                lander_pattern=raw.get('lander_pattern', ''),
                impressions_est=int(raw.get('impressions_est', 0)),
                targeting_hints=raw.get('targeting_hints', []),
                source_url=raw.get('source_url', ''),
                scraped_at=datetime.now().isoformat()
            )
            creatives.append(creative)
        except Exception as e:
            continue
    
    return creatives


def scan_tiktok_creative_center(region: str = "IN", category: str = "gaming", 
                                max_results: int = 30) -> List[Creative]:
    """Scan TikTok Creative Center for trending creatives."""
    
    url = f"https://ads.tiktok.com/creative-center/inspiration/popular?region={region}&category={category}"
    
    goto_url(url)
    wait_for_load()
    time.sleep(5)
    
    creatives = []
    scroll_count = 0
    max_scrolls = 15
    
    while len(creatives) < max_results and scroll_count < max_scrolls:
        page_creatives = _extract_tiktok_creatives(region)
        for c in page_creatives:
            if len(creatives) >= max_results:
                break
            if not any(existing.creative_id == c.creative_id for existing in creatives):
                creatives.append(c)
        
        js("window.scrollBy(0, 3000)")
        time.sleep(2)
        scroll_count += 1
    
    return creatives[:max_results]


def _extract_tiktok_creatives(region: str) -> List[Creative]:
    extraction_js = """
    const cards = document.querySelectorAll('[class*="CreativeCard"], [class*="creative-card"], [data-testid*="creative"]');
    const creatives = [];
    
    cards.forEach((card, i) => {
        try {
            const hook = card.querySelector('[class*="title"], [class*="desc"], [class*="caption"]')?.textContent?.trim() || '';
            const format = card.querySelector('video') ? 'video' : 'image';
            const cta = card.querySelector('[class*="cta"], [class*="button"], button')?.textContent?.trim() || '';
            
            const impressionsText = card.querySelector('[class*="impression"], [class*="view"], [class*="play"]')?.textContent || '';
            const impressionsEst = parseInt(impressionsText.replace(/[^0-9]/g, '')) || 0;
            
            const link = card.querySelector('a')?.href || '';
            
            const creativeId = `tt_${region}_${i}_${Date.now()}`;
            
            if (hook || link) {
                creatives.push({
                    creative_id: creativeId,
                    platform: 'tiktok_cc',
                    advertiser: 'Unknown',
                    hook: hook,
                    format: format,
                    cta: cta,
                    lander_pattern: link,
                    impressions_est: impressionsEst,
                    targeting_hints: ['geo:' + region],
                    source_url: window.location.href
                });
            }
        } catch (e) {}
    });
    
    return creatives;
    """
    
    raw_creatives = js(extraction_js)
    
    from datetime import datetime
    creatives = []
    for raw in raw_creatives:
        try:
            creative = Creative(
                creative_id=raw.get('creative_id', ''),
                platform=raw.get('platform', 'tiktok_cc'),
                advertiser=raw.get('advertiser', ''),
                hook=raw.get('hook', ''),
                format=raw.get('format', 'video'),
                cta=raw.get('cta', ''),
                lander_pattern=raw.get('lander_pattern', ''),
                impressions_est=int(raw.get('impressions_est', 0)),
                targeting_hints=raw.get('targeting_hints', []),
                source_url=raw.get('source_url', ''),
                scraped_at=datetime.now().isoformat()
            )
            creatives.append(creative)
        except Exception as e:
            continue
    
    return creatives


if __name__ == "__main__":
    # Test FB
    creatives = scan_fb_ad_library(query="cricket betting", country="IN", max_results=10)
    for c in creatives:
        print(f"Creative: {c.advertiser} | Hook: {c.hook[:80]} | Format: {c.format} | CTA: {c.cta}")