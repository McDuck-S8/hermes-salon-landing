"""
Facebook Ad Library creative scanner using browser-harness.
"""
import sys
sys.path.insert(0, '/d/Portable_Soft/hermes/browser-harness/src')

from browser_harness.helpers import *
from scripts.models import Creative
from datetime import datetime
from typing import List, Dict, Any
import time


def scan_fb_ad_library(query: str = "cricket betting", country: str = "IN", ad_type: str = "all", max_results: int = 50) -> List[Creative]:
    """
    Scan Facebook Ad Library for creatives.
    
    URL format: https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=IN&q=cricket%20betting
    """
    creatives = []
    
    # Build FB Ad Library URL
    base_url = "https://www.facebook.com/ads/library/"
    params = {
        "active_status": "active",
        "ad_type": ad_type,
        "country": country.upper(),
        "q": query,
        "sort_data[direction]": "desc",
        "sort_data[mode]": "relevancy_monthly_grouped"
    }
    
    param_str = "&".join([f"{k}={v}" for k, v in params.items()])
    url = f"{base_url}?{param_str}"
    
    goto_url(url)
    wait_for_load()
    time.sleep(4)  # FB takes time to load
    
    # Scroll to load more ads
    for scroll in range(5):
        js("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    
    # Extract creatives
    creatives_data = _extract_fb_creatives(query, country)
    return creatives_data


def _extract_fb_creatives(query: str, country: str) -> List[Creative]:
    extraction_js = """
    // FB Ad Library uses complex structure, try multiple selectors
    const adCards = document.querySelectorAll(
        '[data-testid="ad-card"], ' +
        '[class*="ad-card"], ' +
        '[class*="AdLibrary"], ' +
        '[role="article"], ' +
        '._7jyg, ' +  // FB ad card class (changes frequently)
        '._8n_3, ' +
        '[data-pagelet*="AdLibrary"]'
    );
    
    const creatives = [];
    const seen = new Set();
    
    adCards.forEach(card => {
        try {
            // Try to find ad creative content
            const textContent = card.textContent || '';
            const html = card.innerHTML || '';
            
            // Hook/headline - usually in first few text nodes
            let hook = '';
            const textNodes = Array.from(card.querySelectorAll('span, div, p, h1, h2, h3, h4')).map(n => n.textContent?.trim()).filter(Boolean);
            if (textNodes.length > 0) {
                hook = textNodes.slice(0, 3).join(' | ').substring(0, 200);
            }
            
            // CTA button
            const ctaBtn = card.querySelector('button, [role="button"], a[role="button"]');
            const cta = ctaBtn?.textContent?.trim() || '';
            
            // Format detection
            let format = 'image';
            if (card.querySelector('video')) format = 'video';
            else if (card.querySelector('[class*="carousel"]')) format = 'carousel';
            
            // Landing page link
            const link = card.querySelector('a[href*="facebook.com"], a[href*="instagram.com"], a[href*="click"], a[href*="landing"]');
            const landerPattern = link?.href || '';
            
            // Impressions estimate (sometimes shown)
            let impressions = 0;
            const impText = card.textContent?.match(/(\\d[\\d,.]*)\\s*(views?|impressions?|показов?|просмотров?)/i);
            if (impText) {
                impressions = parseFloat(impText[1].replace(/[,.]/g, '')) * (impText[1].includes('K') ? 1000 : impText[1].includes('M') ? 1000000 : 1);
            }
            
            // Advertiser name
            const advertiser = card.querySelector('[class*="advertiser"], [class*="sponsor"], [class*="page-name"]')?.textContent?.trim() || '';
            
            // Creative ID
            const creativeId = `fb_${Date.now()}_${Math.random().toString(36).substr(2,9)}`;
            
            // Targeting hints (language, platform)
            const targetingHints = [];
            if (textContent.includes('Instagram')) targetingHints.push('Instagram');
            if (textContent.includes('Facebook')) targetingHints.push('Facebook');
            if (textContent.includes('Audience Network')) targetingHints.push('Audience Network');
            
            // Strategy detection
            let strategy = 'unknown';
            const lowerHook = hook.toLowerCase();
            if (lowerHook.includes('угс') || lowerHook.includes('ugc') || lowerHook.includes('реальный') || lowerHook.includes('real')) strategy = 'UGC';
            else if (lowerHook.includes('studio') || lowerHook.includes('профессионал') || lowerHook.includes('high quality')) strategy = 'studio';
            else if (lowerHook.includes('нативн') || lowerHook.includes('native')) strategy = 'native';
            
            if (hook && !seen.has(hook.substring(0, 50))) {
                seen.add(hook.substring(0, 50));
                creatives.push({
                    creative_id: creativeId,
                    platform: 'fb_library',
                    hook: hook,
                    format: format,
                    cta: cta,
                    lander_pattern: landerPattern,
                    impressions_est: Math.floor(impressions),
                    strategy: strategy,
                    targeting_hints: targetingHints,
                    advertiser: advertiser,
                    source_url: window.location.href
                });
            }
        } catch (e) {
            console.log('Error:', e);
        }
    });
    
    return creatives;
    """
    
    raw_creatives = js(extraction_js)
    
    creatives = []
    for raw in raw_creatives:
        try:
            creative = Creative(
                creative_id=raw.get('creative_id', ''),
                platform=raw.get('platform', 'fb_library'),
                hook=raw.get('hook', ''),
                format=raw.get('format', 'image'),
                cta=raw.get('cta', ''),
                lander_pattern=raw.get('lander_pattern', ''),
                impressions_est=int(raw.get('impressions_est', 0)),
                strategy=raw.get('strategy', 'unknown'),
                targeting_hints=raw.get('targeting_hints', []),
                source_url=raw.get('source_url', ''),
                freshness_score=1.0
            )
            creatives.append(creative)
        except Exception as e:
            continue
    
    return creatives


if __name__ == "__main__":
    creatives = scan_fb_ad_library(query="cricket betting", country="IN", max_results=20)
    for c in creatives:
        print(f"Creative: {c.hook[:80]} | Format: {c.format} | CTA: {c.cta} | Impressions: {c.impressions_est}")