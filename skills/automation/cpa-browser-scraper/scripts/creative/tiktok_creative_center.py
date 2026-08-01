---
name: tiktok_creative_center_scanner
description: TikTok Creative Center scraper for creative intelligence
---

from dataclasses import dataclass
from typing import List, Dict, Any
import time

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


def scan_tiktok_creative_center(region: str = "IN", category: str = "gaming", 
                                max_results: int = 30) -> List[Creative]:
    """Scan TikTok Creative Center for trending creatives."""
    
    # TikTok Creative Center popular page
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
    const cards = document.querySelectorAll('[class*="CreativeCard"], [class*="creative-card"], [data-testid*="creative"], .creative-item');
    const creatives = [];
    
    cards.forEach((card, i) => {
        try {
            const hook = card.querySelector('[class*="title"], [class*="desc"], [class*="caption"], [class*="text"]')?.textContent?.trim() || '';
            const format = card.querySelector('video') ? 'video' : 'image';
            const cta = card.querySelector('[class*="cta"], [class*="button"], button, [class*="action"]')?.textContent?.trim() || '';
            
            const impressionsText = card.querySelector('[class*="impression"], [class*="view"], [class*="play"], [class*="stat"]')?.textContent || '';
            const impressionsEst = parseInt(impressionsText.replace(/[^0-9]/g, '')) || 0;
            
            const link = card.querySelector('a')?.href || '';
            
            const creativeId = `tt_${region}_${i}_${Date.now()}`;
            
            if (hook || link) {
                creatives.push({
                    creative_id: creativeId,
                    platform: 'tiktok_cc',
                    advertiser: 'TikTok Advertiser',
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
                advertiser=raw.get('advertiser', 'TikTok Advertiser'),
                hook=raw.get('hook', ''),
                format=raw.get('format', 'video'),
                cta=raw.get('cta', ''),
                lander_pattern=raw.get('lander_pattern', ''),
                impressions_est=int(raw.get('impressions_est', 0)),
                targeting_hints=raw.get('targeting_hints', ['geo:' + region]),
                source_url=raw.get('source_url', ''),
                scraped_at=datetime.now().isoformat()
            )
            creatives.append(creative)
        except Exception as e:
            continue
    
    return creatives


def scan_tiktok_by_keyword(keyword: str, region: str = "IN", max_results: int = 20) -> List[Creative]:
    """Search TikTok Creative Center by keyword."""
    
    # TikTok CC search
    from urllib.parse import quote
    url = f"https://ads.tiktok.com/creative-center/search?keyword={quote(keyword)}&region={region}"
    
    goto_url(url)
    wait_for_load()
    time.sleep(5)
    
    creatives = []
    scroll_count = 0
    max_scrolls = 10
    
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


if __name__ == "__main__":
    creatives = scan_tiktok_creative_center(region="IN", category="gaming", max_results=10)
    for c in creatives:
        print(f"Creative: {c.hook[:80]} | Format: {c.format} | CTA: {c.cta} | Impressions: {c.impressions_est}")