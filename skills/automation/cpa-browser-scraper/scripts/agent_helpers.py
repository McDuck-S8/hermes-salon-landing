# CPA Browser Scraper - Helper functions for browser-harness
# Add these to browser-harness/agent-workspace/agent_helpers.py

import time
from browser_harness.helpers import *


# ============================================================
# CPA NETWORK HELPERS
# ============================================================

def scan_adcombo_offers(geo="IN", vertical="gambling", max_pages=3):
    """Navigate to AdCombo offers page, filter by geo/vertical, extract offer cards."""
    goto_url(f"https://www.adcombo.com/offers?geo={geo}&vertical={vertical}")
    wait_for_load()
    time.sleep(3)
    
    extraction_js = """
    const cards = document.querySelectorAll('[class*="offer-card"], [class*="offer-item"], .offer, [data-offer-id]');
    const offers = [];
    
    cards.forEach(card => {
        try {
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
        } catch (e) {}
    });
    
    return offers;
    """
    
    return js(extraction_js)


def scan_cpalead_offers(geo="IN", vertical="gaming", max_pages=3):
    """Scan CPAlead marketplace for offers."""
    goto_url(f"https://www.cpalead.com/offers?geo={geo}&category={vertical}")
    wait_for_load()
    time.sleep(3)
    
    extraction_js = """
    const cards = document.querySelectorAll('[class*="offer"], [class*="campaign"], .offer-card, .campaign-item, tr[class*="offer"]');
    const offers = [];
    
    cards.forEach(card => {
        try {
            const name = card.querySelector('[class*="name"], [class*="title"], .offer-name, .campaign-name')?.textContent?.trim() || '';
            const payoutText = card.querySelector('[class*="payout"], [class*="earning"], [class*="rate"]')?.textContent || '';
            const payout = parseFloat(payoutText.replace(/[^0-9.]/g, '')) || 0;
            
            const flow = card.querySelector('[class*="type"], [class*="conversion"]')?.textContent?.trim() || 'CPA';
            
            const capText = card.querySelector('[class*="cap"], [class*="limit"]')?.textContent || '';
            const cap = parseInt(capText.replace(/[^0-9]/g, '')) || 0;
            
            const landerLink = card.querySelector('a[href*="lander"], a[href*="preview"], a[href*="tracking"]')?.href || '';
            
            const offerId = card.getAttribute('data-offer-id') || card.getAttribute('data-id') || `cpalead_${Date.now()}_${Math.random().toString(36).substr(2,9)}`;
            
            const restrictions = [];
            const restText = card.textContent?.toLowerCase() || '';
            if (restText.includes('preland') || restText.includes('pre-land')) restrictions.push('prelander_required');
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
    
    return js(extraction_js)


# ============================================================
# CREATIVE INTELLIGENCE HELPERS
# ============================================================

def scan_fb_ad_library(query="cricket betting", country="IN", max_results=50):
    """Search FB Ad Library, scroll, extract creative cards."""
    from urllib.parse import urlencode
    base_url = "https://www.facebook.com/ads/library/"
    params = {
        "active_status": "active",
        "ad_type": "all",
        "country": country,
        "q": query,
        "media_type": "all"
    }
    url = f"{base_url}?{urlencode(params)}"
    
    goto_url(url)
    wait_for_load()
    time.sleep(5)
    
    creatives = []
    scroll_count = 0
    max_scrolls = 20
    
    while len(creatives) < max_results and scroll_count < max_scrolls:
        page_creatives = _extract_fb_ad_cards()
        for c in page_creatives:
            if len(creatives) >= max_results:
                break
            if not any(existing['creative_id'] == c['creative_id'] for existing in creatives):
                creatives.append(c)
        
        js("window.scrollBy(0, 3000)")
        time.sleep(2)
        scroll_count += 1
    
    return creatives[:max_results]


def _extract_fb_ad_cards():
    extraction_js = """
    const cards = document.querySelectorAll('[data-testid="ad-card"], .x1n2onr6, [class*="ad-card"], [role="article"]');
    const creatives = [];
    
    cards.forEach((card, i) => {
        try {
            const advertiser = card.querySelector('[class*="advertiser"], [class*="sponsor"], [data-testid="advertiser-name"]')?.textContent?.trim() || '';
            const creativeText = card.querySelector('[class*="creative"], [class*="ad-text"], [data-testid="ad-creative"]')?.textContent?.trim() || '';
            const hook = creativeText.substring(0, 200);
            
            let format = 'image';
            if (card.querySelector('video')) format = 'video';
            else if (card.querySelector('[class*="carousel"], [class*="gallery"]')) format = 'carousel';
            
            const ctaBtn = card.querySelector('button, [role="button"]');
            const cta = ctaBtn?.textContent?.trim() || '';
            
            const link = card.querySelector('a[href*="facebook.com"], a[href*="instagram.com"], a[href*="click"]')?.href || '';
            
            const impressionsText = card.querySelector('[class*="impression"], [class*="reach"]')?.textContent || '';
            const impressionsEst = parseInt(impressionsText.replace(/[^0-9]/g, '')) || 0.
            
            const targetingHints = [];
            const targetingText = card.textContent?.toLowerCase() || '';
            if (targetingText.includes('age')) targetingHints.push('age_targeting');
            if (targetingText.includes('location') || targetingText.includes('country')) targetingHints.push('geo_targeting');
            if (targetingText.includes('interest')) targetingHints.push('interest_targeting');
            
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
        } catch (e) {}
    });
    
    return creatives;
    """
    
    return js(extraction_js)


def scan_tiktok_creative_center(region="IN", category="gaming", max_results=30):
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
            if not any(existing['creative_id'] == c['creative_id'] for existing in creatives):
                creatives.append(c)
        
        js("window.scrollBy(0, 3000)")
        time.sleep(2)
        scroll_count += 1
    
    return creatives[:max_results]


def _extract_tiktok_creatives(region):
    extraction_js = """
    const cards = document.querySelectorAll('[class*="CreativeCard"], [class*="creative-card"], [data-testid*="creative"], .creative-item');
    const creatives = [];
    
    cards.forEach((card, i) => {
        try {
            const hook = card.querySelector('[class*="title"], [class*="desc"], [class*="caption"], [class*="text"]')?.textContent?.trim() || '';
            const format = card.querySelector('video') ? 'video' : 'image';
            const cta = card.querySelector('[class*="cta"], [class*="button"], button, [class*="action"]')?.textContent?.trim() || '';
            
            const impressionsText = card.querySelector('[class*="impression"], [class*="view"], [class*="play"], [class*="stat"]')?.textContent || '';
            const impressionsEst = parseInt(impressionsText.replace(/[^0-9]/g, '')) || 0.
            
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
    
    return js(extraction_js)


# ============================================================
# COMPETITOR ANALYSIS HELPERS
# ============================================================

def analyze_competitor_lander(url):
    """Deep analysis of a competitor landing page."""
    goto_url(url)
    wait_for_load()
    time.sleep(3)
    
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
    
    return report_data


# ============================================================
# GOOGLE MAPS LOCAL BUSINESS HELPERS
# ============================================================

def scan_google_maps(query, max_results=50, lang="ru"):
    """Scan Google Maps for local businesses."""
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
        
        for biz in page_businesses:
            if len(businesses) >= max_results:
                break
            if not any(existing['name'] == biz['name'] and existing['address'] == biz['address'] for existing in businesses):
                businesses.append(biz)
        
        prev_count = len(businesses)
        
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


def _extract_maps_cards():
    extraction_js = """
    const cards = document.querySelectorAll('[role="article"], [class*="Nv2PK"], [class*="THOPZb"], [jsaction*="pane"]');
    const businesses = [];
    
    cards.forEach((card, i) => {
        try {
            const nameEl = card.querySelector('[class*="fontHeadlineSmall"], [class*="qBF1Pd"], h3, [aria-label]');
            const name = nameEl?.textContent?.trim() || nameEl?.getAttribute('aria-label') || '';
            
            const addrEl = card.querySelector('[class*="fontBodyMedium"], [class*="W4Efsd"], [data-value="address"]');
            const address = addrEl?.textContent?.trim() || '';
            
            const phoneEl = card.querySelector('[data-value="phone"], [class*="UsdlK"], a[href^="tel:"]');
            const phone = phoneEl?.textContent?.trim() || phoneEl?.getAttribute('href')?.replace('tel:', '') || '';
            
            const ratingEl = card.querySelector('[role="img"][aria-label*="star"], [class*="MW4etd"], [class*="F7nice"]');
            let rating = 0.0;
            if (ratingEl) {
                const ratingText = ratingEl.getAttribute('aria-label') || ratingEl.textContent || '';
                const match = ratingText.match(/([0-9.]+)/);
                if (match) rating = parseFloat(match[1]);
            }
            
            const reviewsEl = card.querySelector('[class*="UY7F9"], [aria-label*="review"]');
            let reviewCount = 0;
            if (reviewsEl) {
                const revText = reviewsEl.textContent || reviewsEl.getAttribute('aria-label') || '';
                const match = revText.match(/([0-9,]+)/);
                if (match) reviewCount = parseInt(match[1].replace(',', ''));
            }
            
            const catEl = card.querySelector('[class*="W4Efsd"]:not([data-value="address"])');
            const categories = catEl?.textContent?.trim().split('·').map(c => c.trim()) || [];
            
            const websiteEl = card.querySelector('a[href^="http"]:not([href*="google.com"])');
            const website = websiteEl?.href || '';
            
            if (name && name.length > 2) {
                businesses.push({
                    name: name,
                    phone: phone,
                    address: address,
                    website: website,
                    rating: rating,
                    review_count: reviewCount,
                    categories: categories,
                    has_website: !!website,
                    source_url: window.location.href
                });
            }
        } catch (e) {}
    });
    
    return businesses;
    """
    
    return js(extraction_js)


# ============================================================
# QUICK SCAN FUNCTIONS (one-liners for common tasks)
# ============================================================

def quick_scan_offers(geo="IN", vertical="gambling"):
    """Quick scan: AdCombo + CPAlead offers for geo/vertical."""
    adcombo = scan_adcombo_offers(geo=geo, vertical=vertical, max_pages=2)
    cpalead = scan_cpalead_offers(geo=geo, vertical=vertical, max_pages=2)
    return adcombo + cpalead


def quick_scan_creatives(query="cricket betting", country="IN"):
    """Quick scan: FB Library + TikTok CC creatives."""
    fb = scan_fb_ad_library(query=query, country=country, max_results=20)
    tt = scan_tiktok_creative_center(region=country, category="gaming", max_results=15)
    return fb + tt


def quick_scan_local(query, max_results=30):
    """Quick scan Google Maps for leads."""
    return scan_google_maps(query, max_results=max_results)


# Example usage in browser-harness:
# browser-harness <<'PY'
# from agent_helpers import *
# 
# # Quick offer scan
# offers = quick_scan_offers(geo="IN", vertical="gambling")
# for o in offers:
#     print(f"{o['name']} | ${o['payout']} | Cap: {o['cap_daily']}/day")
# 
# # Quick creative scan
# creatives = quick_scan_creatives("cricket betting", "IN")
# for c in creatives:
#     print(f"[{c['platform']}] {c['advertiser']}: {c['hook'][:80]}")
# 
# # Quick local leads
# leads = quick_scan_local("салон красоты Позняки Киев", max_results=20)
# for b in leads:
#     if not b['website']:
#         print(f"LEAD: {b['name']} | {b['phone']} | {b['address']}")
# PY