---
name: competitor_landing_analyzer
description: Analyze competitor landing pages for CPA/arbitrage intelligence
---

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

from browser_harness.helpers import *


@dataclass
class CompetitorReport:
    """Competitor landing page analysis."""
    url: str
    hook: str
    structure: Dict[str, Any]  # {"prelander": True, "lander_type": "quiz", "steps": 3}
    tech_stack: List[str]
    cta_patterns: List[str]
    spend_signals: Dict[str, Any]  # {"fb_pixel": True, "ga": "G-XXXX", "tt_pixel": True}
    estimated_monthly_spend: Optional[float] = None
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())
    raw_data: Dict[str, Any] = field(default_factory=dict)


def analyze_competitor_lander(url: str) -> CompetitorReport:
    """Deep analysis of a competitor landing page."""
    
    goto_url(url)
    wait_for_load()
    time.sleep(3)
    
    # Extract all data via JS
    report_data = js("""
    const report = {
        url: window.location.href,
        hook: '',
        structure: {},
        tech_stack: [],
        cta_patterns: [],
        spend_signals: {}
    };
    
    // Hook - main headline
    const headlines = document.querySelectorAll('h1, h2, [class*="hero"], [class*="headline"]');
    headlines.forEach(h => {
        const text = h.textContent?.trim() || '';
        if (text.length > 20 && text.length < 200) {
            report.hook = text;
        }
    });
    
    // Structure analysis
    const hasPrelander = !!document.querySelector('[class*="preland"], [class*="pre-land"], [id*="preland"]');
    const forms = document.querySelectorAll('form');
    const steps = document.querySelectorAll('[class*="step"], [class*="question"], [class*="quiz"]');
    const popups = document.querySelectorAll('[class*="modal"], [class*="popup"], [class*="overlay"]');
    
    report.structure = {
        prelander: hasPrelander,
        forms_count: forms.length,
        quiz_steps: steps.length,
        popups: popups.length,
        has_exit_intent: !!document.querySelector('[class*="exit"]'),
        has_timer: !!document.querySelector('[class*="timer"], [class*="countdown"]'),
        cta_buttons: Array.from(document.querySelectorAll('button, [role="button"], a[class*="btn"]')).map(b => b.textContent?.trim()).filter(t => t)
    };
    
    // Tech stack detection
    const scripts = Array.from(document.querySelectorAll('script[src]')).map(s => s.src);
    const inlineScripts = Array.from(document.querySelectorAll('script:not([src])')).map(s => s.textContent).join(' ');
    const allScriptContent = scripts.join(' ') + ' ' + inlineScripts;
    
    const techSignatures = {
        'keitaro': ['keitaro', 'kclick'],
        'binom': ['binom', 'binomo'],
        'voluum': ['voluum', 'vluum'],
        'redtrack': ['redtrack', 'rt.js'],
        'thrive': ['thrivetracker', 'thrive'],
        'wordpress': ['wp-content', 'wp-includes', 'wordpress'],
        'elementor': ['elementor'],
        'clickfunnels': ['clickfunnels', 'cf-'],
        'kartra': ['kartra'],
        'googletagmanager': ['googletagmanager.com', 'gtm.js'],
        'facebook_pixel': ['connect.facebook.net', 'fbq('],
        'tiktok_pixel': ['analytics.tiktok.com', 'ttq.'],
        'google_analytics': ['google-analytics.com', 'ga(', 'gtag('],
        'google_ads': ['googleadservices.com', 'conversion_async'],
        'hotjar': ['hotjar.com', 'hj('],
        'clarity': ['clarity.ms', 'clarity('],
        'mixpanel': ['mixpanel.com', 'mixpanel.'],
        'amplitude': ['amplitude.com', 'amplitude.'],
        'segment': ['segment.com', 'analytics.js'],
        'cloudflare': ['cloudflare.com', '__cfduid'],
        'cloudflare_rocket': ['rocket-loader'],
        'recaptcha': ['recaptcha', 'grecaptcha'],
        'hcaptcha': ['hcaptcha'],
        'stripe': ['stripe.com', 'stripe.js'],
        'paypal': ['paypal.com', 'paypal-sdk'],
        'coinbase': ['coinbase.com', 'coinbase-commerce'],
        'nowpayments': ['nowpayments.io'],
        'coingate': ['coingate.com']
    };
    
    tech_stack = [];
    for (const [tech, signatures] of Object.entries(techSignatures)) {
        for (const sig of signatures) {
            if (allScriptContent.toLowerCase().includes(sig.toLowerCase())) {
                tech_stack.push(tech);
                break;
            }
        }
    }
    report.tech_stack = tech_stack;
    
    // CTA patterns
    const ctaButtons = document.querySelectorAll('button, [role="button"], a[class*="btn"], input[type="submit"]');
    report.cta_patterns = Array.from(ctaButtons)
        .map(b => b.textContent?.trim())
        .filter(t => t && t.length < 50)
        .slice(0, 10);
    
    // Spend signals
    const fbPixel = !!document.querySelector('script[src*="connect.facebook.net"]') || 
                    !!document.querySelector('img[src*="facebook.com/tr"]');
    const ttPixel = !!document.querySelector('script[src*="analytics.tiktok.com"]') ||
                    !!document.querySelector('img[src*="analytics.tiktok.com"]');
    const ga = !!document.querySelector('script[src*="google-analytics.com"]') ||
               !!document.querySelector('script[src*="googletagmanager.com"]') ||
               allScriptContent.includes('gtag(') || allScriptContent.includes('ga(');
    const fbCAPI = allScriptContent.includes('_fbq') || allScriptContent.includes('fbq(');
    
    report.spend_signals = {
        fb_pixel: fbPixel,
        fb_capi: fbCAPI,
        tiktok_pixel: ttPixel,
        google_analytics: ga,
        google_ads: allScriptContent.includes('googleadservices') || allScriptContent.includes('conversion_async'),
        hotjar: allScriptContent.includes('hotjar'),
        clarity: allScriptContent.includes('clarity.ms')
    };
    
    return report;
    """)
    
    from datetime import datetime
    
    report = CompetitorReport(
        url=report_data.get('url', url),
        hook=report_data.get('hook', ''),
        structure=report_data.get('structure', {}),
        tech_stack=report_data.get('tech_stack', []),
        cta_patterns=report_data.get('cta_patterns', []),
        spend_signals=report_data.get('spend_signals', {}),
        scraped_at=datetime.now().isoformat(),
        raw_data=report_data
    )
    
    return report


def analyze_multiple_landers(urls: List[str]) -> List[CompetitorReport]:
    """Analyze multiple competitor landers in sequence."""
    reports = []
    for url in urls:
        try:
            report = analyze_competitor_lander(url)
            reports.append(report)
        except Exception as e:
            print(f"Error analyzing {url}: {e}")
    return reports


def detect_lander_type(url: str) -> str:
    """Quick detection of lander type."""
    goto_url(url)
    wait_for_load()
    time.sleep(2)
    
    result = js("""
    const hasQuiz = !!document.querySelector('[class*="quiz"], [class*="question"], [class*="step"]');
    const hasVideo = !!document.querySelector('video');
    const hasForm = document.querySelectorAll('form').length > 0;
    const hasPopup = !!document.querySelector('[class*="modal"], [class*="popup"], [class*="overlay"]');
    const hasTimer = !!document.querySelector('[class*="timer"], [class*="countdown"]');
    const hasExit = !!document.querySelector('[class*="exit"]');
    const ctaCount = document.querySelectorAll('button, [role="button"], a[class*="btn"]').length;
    
    if (hasQuiz) return 'quiz_funnel';
    if (hasVideo && ctaCount > 2) return 'vsl_funnel';
    if (hasPopup) return 'popup_funnel';
    if (hasTimer || hasExit) return 'urgency_funnel';
    if (ctaCount > 3) return 'multi_cta';
    return 'simple_lander';
    """)
    
    return result


if __name__ == "__main__":
    # Test
    urls = [
        "https://example-competitor.com/lander",
    ]
    for url in urls:
        report = analyze_competitor_lander(url)
        print(f"URL: {report.url}")
        print(f"Hook: {report.hook[:100]}")
        print(f"Structure: {report.structure}")
        print(f"Tech: {report.tech_stack}")
        print(f"Spend signals: {report.spend_signals}")
        print("---")