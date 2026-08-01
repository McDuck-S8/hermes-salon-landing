"""
Creative Intelligence Scanner for FB Ad Library and TikTok Creative Center.
Uses browser-harness to scrape live ad data.
"""
import sys
sys.path.insert(0, '/d/Portable_Soft/hermes/browser-harness/src')

from browser_harness.helpers import *
from scripts.models import Creative
from datetime import datetime
from typing import List, Dict, Any
import time
import json


class CreativeScanner:
    """Scans FB Ad Library and TikTok Creative Center for creative intelligence."""
    
    def scan_fb_library(self, query: str = "cricket betting India", 
                        country: str = "IN", 
                        ad_type: str = "all",
                        max_results: int = 50) -> List[Creative]:
        """Scan Facebook Ad Library for creatives."""
        
        # Build FB Library URL
        base_url = "https://www.facebook.com/ads/library/"
        params = {
            "active_status": "all" if ad_type == "all" else ad_type,
            "ad_type": "all",
            "country": country,
            "q": query,
            "sort_data[direction]": "desc",
            "sort_data[mode]": "relevancy_monthly_grouped"
        }
        url = f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        
        print(f"Navigating to FB Ad Library: {url}")
        goto_url(url)
        wait_for_load()
        time.sleep(5)
        
        # Scroll and extract
        creatives = self._extract_fb_creatives(max_results)
        return creatives
    
    def _extract_fb_creatives(self, max_results: int) -> List[Creative]:
        """Extract creative data from FB Ad Library page."""
        
        extraction_js = f"""
        const creatives = [];
        const seen = new Set();
        
        // Scroll to load more
        window.scrollTo(0, document.body.scrollHeight);
        
        // Find ad cards
        const adCards = document.querySelectorAll('[data-ad-id], [class*="ad-card"], [class*="AdCard"], [role="article"], [class*="ad-creative"]');
        
        adCards.forEach(card => {{
            try {{
                // Creative ID
                const creativeId = card.getAttribute('data-ad-id') || card.getAttribute('data-creative-id') || 
                    `fb_${{Date.now()}}_${{Math.random().toString(36).substr(2,9)}}`;
                
                if (seen.has(creativeId)) return;
                seen.add(creativeId);
                
                // Hook/Headline
                let hook = "";
                const hookSelectors = [
                    '[class*="headline"]', '[class*="primary-text"]', '[class*="ad-title"]',
                    'h1', 'h2', 'h3', '[data-testid="ad-title"]', '[class*="body"]'
                ];
                for (const sel of hookSelectors) {{
                    const el = card.querySelector(sel);
                    if (el && el.textContent?.trim()) {{
                        hook = el.textContent.trim();
                        break;
                    }}
                }}
                
                // Format (video/image/carousel)
                let format = "image";
                if (card.querySelector('video')) format = "video";
                else if (card.querySelector('[class*="carousel"], [class*="gallery"]')) format = "carousel";
                
                // CTA
                let cta = "";
                const ctaSelectors = ['[class*="cta"]', '[class*="button"]', '[class*="action"]', 'button', 'a[role="button"]'];
                for (const sel of ctaSelectors) {{
                    const el = card.querySelector(sel);
                    if (el && el.textContent?.trim()) {{
                        cta = el.textContent.trim();
                        break;
                    }}
                }}
                
                // Lander pattern (URL in link)
                let landerPattern = "";
                const link = card.querySelector('a[href]');
                if (link) landerPattern = link.href;
                
                // Impressions estimate
                let impressionsEst = 0;
                const impressionSelectors = ['[class*="impression"]', '[class*="reach"]', '[class*="view"]'];
                for (const sel of impressionSelectors) {{
                    const el = card.querySelector(sel);
                    if (el) {{
                        const text = el.textContent || '';
                        const match = text.match(/([\\d,.]+)\\s*[KM]?/);
                        if (match) {{
                            const val = parseFloat(match[1].replace(/,/g, ''));
                            if (text.includes('K')) impressionsEst = val * 1000;
                            else if (text.includes('M')) impressionsEst = val * 1000000;
                            else impressionsEst = val;
                        }}
                        break;
                    }}
                }}
                
                // Strategy detection
                let strategy = "studio";
                const text = card.textContent?.toLowerCase() || "";
                if (text.includes('ugc') || text.includes('user generated') || 
                    text.includes('selfie') || text.includes('phone')) strategy = "ugc";
                else if (text.includes('native') || text.includes('article')) strategy = "native";
                else if (text.includes('review') || text.includes('testimonial')) strategy = "testimonial";
                else if (text.includes('demo') || text.includes('tutorial')) strategy = "demo";
                
                // Targeting hints
                const targetingHints = [];
                const fullText = card.textContent?.toLowerCase() || "";
                if (fullText.includes('india') || fullText.includes('indian')) targetingHints.push('geo:IN');
                if (fullText.includes('cricket') || fullText.includes('ipl')) targetingHints.push('interest:cricket');
                if (fullText.includes('betting') || fullText.includes('bet')) targetingHints.push('interest:betting');
                if (fullText.includes('bonus') || fullText.includes('welcome')) targetingHints.push('offer:bonus');
                if (fullText.includes('pwa') || fullText.includes('install')) targetingHints.push('type:pwa_install');
                
                // Source URL
                const sourceUrl = window.location.href;
                
                if (hook || card.querySelector('img, video')) {{
                    creatives.push({{
                        creative_id: creativeId,
                        platform: "fb_library",
                        hook: hook,
                        format: format,
                        cta: cta,
                        lander_pattern: landerPattern,
                        impressions_est: impressionsEst,
                        strategy: strategy,
                        targeting_hints: targetingHints,
                        source_url: sourceUrl
                    }});
                }}
            }} catch (e) {{
                console.log('Error:', e);
            }}
        }});
        
        return creatives;
        """
        
        raw_creatives = js(extraction_js)
        return self._parse_creatives(raw_creatives, "fb_library")
    
    def scan_tiktok_cc(self, region: str = "IN", category: str = "gaming",
                       max_results: int = 30) -> List[Creative]:
        """Scan TikTok Creative Center."""
        
        url = f"https://ads.tiktok.com/creative-center?region={region}&category={category}"
        print(f"Navigating to TikTok Creative Center: {url}")
        goto_url(url)
        wait_for_load()
        time.sleep(5)
        
        creatives = self._extract_tiktok_creatives(max_results)
        return creatives
    
    def _extract_tiktok_creatives(self, max_results: int) -> List[Creative]:
        """Extract creative data from TikTok Creative Center."""
        
        extraction_js = f"""
        const creatives = [];
        const seen = new Set();
        
        // Scroll to load
        window.scrollTo(0, document.body.scrollHeight);
        
        // Find creative cards
        const cards = document.querySelectorAll('[class*="CreativeCard"], [class*="creative-card"], [data-creative-id], [class*="video-card"]');
        
        cards.forEach(card => {{
            try {{
                const creativeId = card.getAttribute('data-creative-id') || 
                    card.getAttribute('data-id') || `tt_${{Date.now()}}_${{Math.random().toString(36).substr(2,9)}}`;
                
                if (seen.has(creativeId)) return;
                seen.add(creativeId);
                
                // Hook
                let hook = "";
                const hookSelectors = ['[class*="title"]', '[class*="desc"]', '[class*="text"]', 'h3', 'h4'];
                for (const sel of hookSelectors) {{
                    const el = card.querySelector(sel);
                    if (el && el.textContent?.trim()) {{
                        hook = el.textContent.trim();
                        break;
                    }}
                }}
                
                // Format (always video for TikTok)
                const format = "video";
                
                // CTA
                let cta = "";
                const ctaSelectors = ['[class*="cta"]', '[class*="button"]', '[class*="action"]', 'button'];
                for (const sel of ctaSelectors) {{
                    const el = card.querySelector(sel);
                    if (el && el.textContent?.trim()) {{
                        cta = el.textContent.trim();
                        break;
                    }}
                }}
                
                // Lander pattern
                let landerPattern = "";
                const link = card.querySelector('a[href]');
                if (link) landerPattern = link.href;
                
                // Impressions
                let impressionsEst = 0;
                const text = card.textContent || "";
                const impMatch = text.match(/([\\d,.]+)\\s*[KM]?\\s*(views|impressions|показов)/i);
                if (impMatch) {{
                    const val = parseFloat(impMatch[1].replace(/,/g, ''));
                    if (text.includes('M') || text.includes('млн')) impressionsEst = val * 1000000;
                    else if (text.includes('K') || text.includes('тыс')) impressionsEst = val * 1000;
                    else impressionsEst = val;
                }}
                
                // Strategy
                let strategy = "studio";
                const fullText = text.toLowerCase();
                if (fullText.includes('ugc') || fullText.includes('selfie') || fullText.includes('phone')) strategy = "ugc";
                else if (fullText.includes('demo') || fullText.includes('tutorial')) strategy = "demo";
                else if (fullText.includes('review')) strategy = "testimonial";
                else if (fullText.includes('native')) strategy = "native";
                
                // Targeting hints
                const targetingHints = [];
                if (fullText.includes('india') || fullText.includes('индия')) targetingHints.push('geo:IN');
                if (fullText.includes('cricket') || fullText.includes('крикет')) targetingHints.push('interest:cricket');
                if (fullText.includes('betting') || fullText.includes('ставк')) targetingHints.push('interest:betting');
                if (fullText.includes('install') || fullText.includes('install')) targetingHints.push('type:app_install');
                
                creatives.push({{
                    creative_id: creativeId,
                    platform: "tiktok_cc",
                    hook: hook,
                    format: format,
                    cta: cta,
                    lander_pattern: landerPattern,
                    impressions_est: impressionsEst,
                    strategy: strategy,
                    targeting_hints: targetingHints,
                    source_url: window.location.href
                }});
            }} catch (e) {{
                console.log('Error:', e);
            }}
        }});
        
        return creatives;
        """
        
        raw_creatives = js(extraction_js)
        return self._parse_creatives(raw_creatives, "tiktok_cc")
    
    def _parse_creatives(self, raw_creatives: List[Dict], platform: str) -> List[Creative]:
        """Parse raw creative data into Creative objects."""
        creatives = []
        for raw in raw_creatives:
            try:
                creative = Creative(
                    creative_id=raw.get('creative_id', ''),
                    platform=platform,
                    hook=raw.get('hook', ''),
                    format=raw.get('format', 'image'),
                    cta=raw.get('cta', ''),
                    lander_pattern=raw.get('lander_pattern', ''),
                    impressions_est=raw.get('impressions_est', 0),
                    strategy=raw.get('strategy', 'studio'),
                    targeting_hints=raw.get('targeting_hints', []),
                    source_url=raw.get('source_url', ''),
                    scraped_at=datetime.now(),
                    freshness_score=0.9
                )
                creatives.append(creative)
            except Exception as e:
                continue
        return creatives
    
    def scan_competitor_landers(self, urls: List[str]) -> List[Dict]:
        """Analyze competitor landing pages for structure, hooks, tech stack."""
        reports = []
        for url in urls:
            try:
                goto_url(url)
                wait_for_load()
                time.sleep(3)
                
                report = js("""
                    const report = {
                        url: window.location.href,
                        hook: '',
                        structure: {},
                        tech_stack: [],
                        cta_patterns: [],
                        forms: [],
                        scripts: [],
                        meta: {}
                    };
                    
                    // Hook (h1, hero text)
                    const h1 = document.querySelector('h1');
                    if (h1) report.hook = h1.textContent.trim();
                    
                    // Structure
                    report.structure = {
                        has_prelander: !!document.querySelector('[class*="preland"], [class*="pre-land"]'),
                        has_quiz: !!document.querySelector('[class*="quiz"], [class*="survey"]'),
                        has_video: !!document.querySelector('video'),
                        has_timer: !!document.querySelector('[class*="timer"], [class*="countdown"]'),
                        has_popup: !!document.querySelector('[class*="popup"], [class*="modal"]'),
                        steps: document.querySelectorAll('[class*="step"], [class*="question"]').length
                    };
                    
                    // Tech stack
                    const scripts = Array.from(document.scripts).map(s => s.src).filter(Boolean);
                    report.scripts = scripts.slice(0, 20);
                    
                    // Detect tracker
                    if (scripts.some(s => s.includes('keitaro'))) report.tech_stack.push('keitaro');
                    if (scripts.some(s => s.includes('binom'))) report.tech_stack.push('binom');
                    if (scripts.some(s => s.includes('voluum'))) report.tech_stack.push('voluum');
                    if (scripts.some(s => s.includes('thrive'))) report.tech_stack.push('thrive');
                    if (scripts.some(s => s.includes('wp-') || s.includes('wordpress'))) report.tech_stack.push('wordpress');
                    if (scripts.some(s => s.includes('elementor'))) report.tech_stack.push('elementor');
                    if (scripts.some(s => s.includes('react'))) report.tech_stack.push('react');
                    if (scripts.some(s => s.includes('vue'))) report.tech_stack.push('vue');
                    
                    // CTA patterns
                    const buttons = Array.from(document.querySelectorAll('button, a[role="button"], input[type="submit"], .btn, .button'));
                    report.cta_patterns = buttons.map(b => b.textContent?.trim()).filter(Boolean).slice(0, 10);
                    
                    // Forms
                    const forms = Array.from(document.forms);
                    report.forms = forms.map(f => ({
                        action: f.action,
                        method: f.method,
                        fields: Array.from(f.elements).map(e => ({name: e.name, type: e.type}))
                    }));
                    
                    // Meta tags
                    const metas = document.querySelectorAll('meta');
                    metas.forEach(m => {
                        if (m.getAttribute('property') || m.getAttribute('name')) {
                            report.meta[m.getAttribute('property') || m.getAttribute('name')] = m.getAttribute('content');
                        }
                    });
                    
                    // Tracking pixels
                    const pixels = [];
                    if (document.body.innerHTML.includes('fbq(')) pixels.push('facebook_pixel');
                    if (document.body.innerHTML.includes('ttq.')) pixels.push('tiktok_pixel');
                    if (document.body.innerHTML.includes('gtag(')) pixels.push('google_analytics');
                    if (document.body.innerHTML.includes('yaCounter')) pixels.push('yandex_metrica');
                    report.tech_stack.push(...pixels);
                    
                    return report;
                """)
                reports.append(report)
            except Exception as e:
                reports.append({"url": url, "error": str(e)})
        
        return reports


if __name__ == "__main__":
    scanner = CreativeScanner()
    
    # Test FB Library
    print("Scanning FB Ad Library...")
    creatives = scanner.scan_fb_library("cricket betting India", "IN", max_results=20)
    print(f"Found {len(creatives)} creatives")
    for c in creatives[:5]:
        print(f"  {c.hook[:60]}... | {c.format} | {c.cta} | {c.strategy}")