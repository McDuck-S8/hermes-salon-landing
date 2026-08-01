"""
TikTok Creative Center scanner using browser-harness.
"""
import sys
sys.path.insert(0, '/d/Portable_Soft/hermes/browser-harness/src')

from browser_harness.helpers import *
from scripts.models import Creative
from datetime import datetime
from typing import List, Dict, Any
import time


def scan_tiktok_creative_center(region: str = "IN", category: str = "gaming", max_results: int = 30) -> List[Creative]:
    """
    Scan TikTok Creative Center for top creatives.
    
    URL: https://ads.tiktok.com/creative-center?region=IN&category=gaming
    """
    creatives = []
    
    # TikTok Creative Center URL
    base_url = "https://ads.tiktok.com/creative-center"
    params = f"?region={region.upper()}&category={category}"
    url = f"{base_url}{params}"
    
    goto_url(url)
    wait_for_load()
    time.sleep(4)  # TikTok takes time to load
    
    # Scroll to load more
    for scroll in range(5):
        js("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    
    # Extract creatives
    creatives_data = _extract_tiktok_creatives(region, category)
    return creatives_data


def _extract_tiktok_creatives(region: str, category: str) -> List[Creative]:
    extraction_js = """
    // TikTok Creative Center cards
    const cards = document.querySelectorAll(
        '[class*="creative"], ' +
        '[class*="video-card"], ' +
        '[class*="ad-card"], ' +
        '[data-testid*="creative"], ' +
        '.creative-item, ' +
        '[class*="CreativeCard"]'
    );
    
    const creatives = [];
    const seen = new Set();
    
    cards.forEach(card => {
        try {
            // Video element
            const video = card.querySelector('video');
            const videoUrl = video?.src || video?.querySelector('source')?.src || '';
            
            // Thumbnail
            const img = card.querySelector('img');
            const thumbnail = img?.src || '';
            
            // Title/Hook
            const titleEl = card.querySelector('[class*="title"], [class*="hook"], h3, h4, [class*="name"]');
            const hook = titleEl?.textContent?.trim() || card.textContent?.trim().substring(0, 200) || '';
            
            // CTA
            const ctaEl = card.querySelector('[class*="cta"], [class*="button"], button, a[class*="btn"]');
            const cta = ctaEl?.textContent?.trim() || '';
            
            // Impressions/Views
            let impressions = 0;
            const stats = card.querySelector('[class*="stat"], [class*="view"], [class*="impression"]');
            if (stats) {
                const statText = stats.textContent || '';
                const match = statText.match(/(\\d[\\d,.]*)\\s*(K|M|k|m)?/);
                if (match) {
                    impressions = parseFloat(match[1].replace(/,/g, '')) * 
                        (match[2]?.toUpperCase() === 'M' ? 1000000 : match[2]?.toUpperCase() === 'K' ? 1000 : 1);
                }
            }
            
            // Landing page pattern (sometimes shown)
            const link = card.querySelector('a[href]');
            const landerPattern = link?.href || '';
            
            // Strategy detection
            let strategy = 'unknown';
            const lowerHook = hook.toLowerCase();
            if (lowerHook.includes('ugc') || lowerHook.includes('user generated') || 
                lowerHook.includes('real') || lowerHook.includes('authentic')) {
                strategy = 'UGC';
            } else if (lowerHook.includes('studio') || lowerHook.includes('professional') ||
                       lowerHook.includes('high quality') || lowerHook.includes('cinematic')) {
                strategy = 'studio';
            } else if (lowerHook.includes('native') || lowerHook.includes('organic') ||
                       lowerHook.includes('story') || lowerHook.includes('vlog')) {
                strategy = 'native';
            }
            
            // Targeting hints
            const targetingHints = [];
            if (hook.toLowerCase().includes('india') || hook.toLowerCase().includes('indian')) targetingHints.push('India geo');
            if (hook.toLowerCase().includes('cricket') || hook.toLowerCase().includes('ipl')) targetingHints.push('cricket');
            if (hook.toLowerCase().includes('bet') || hook.toLowerCase().includes('casino')) targetingHints.push('gambling');
            
            const creativeId = `tt_${Date.now()}_${Math.random().toString(36).substr(2,9)}`;
            
            if (hook && !seen.has(hook.substring(0, 50))) {
                seen.add(hook.substring(0, 50));
                creatives.push({
                    creative_id: creativeId,
                    platform: 'tiktok_cc',
                    hook: hook,
                    format: videoUrl ? 'video' : 'image',
                    cta: cta,
                    lander_pattern: landerPattern,
                    impressions_est: Math.floor(impressions),
                    strategy: strategy,
                    targeting_hints: targetingHints,
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
                platform=raw.get('platform', 'tiktok_cc'),
                hook=raw.get('hook', ''),
                format=raw.get('format', 'video'),
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
    creatives = scan_tiktok_creative_center(region="IN", category="gaming", max_results=20)
    for c in creatives:
        print(f"Creative: {c.hook[:80]} | Format: {c.format} | Strategy: {c.strategy} | Impressions: {c.impressions_est}")