# Creative Radar Browser Automation Patterns

## Purpose
Reference for multi-agent researcher workers dispatched to scrape FB Ad Library, TikTok Creative Center, and CPA network dashboards for creative intelligence.

## Prerequisites
- BrowserOS MCP running on `http://localhost:9003/mcp` (verify: `curl http://localhost:9003/mcp` → 200 OK)
- `browser-automation` skill loaded
- Worker brief includes: `tools_required: ["browser-automation"]`, `mcp_servers: ["browseros"]`

---

## FB Ad Library Scraping

### Target URLs
- `https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=RU&q=<keyword>`
- `https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=RU&media_type=all`

### Navigation Pattern
```python
# 1. Navigate to search page
await browser.nav(page_id).goto(f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country={geo}&q={keyword}")

# 2. Wait for results to load (JS rendered)
await browser.wait(page_id, for_="selector", value="[data-testid='ad-library-card']", timeout=15000)

# 3. Scroll to load more (infinite scroll)
for _ in range(3):
    await browser.input(page_id).scroll("down", amount=5)
    await asyncio.sleep(2)

# 4. Extract ad cards
snapshot = await browser.observe(page_id).snapshot()
# Parse cards from snapshot refs
```

### Data to Extract per Ad
| Field | Selector | Notes |
|-------|----------|-------|
| Ad ID | `[data-testid='ad-library-card']` | Unique identifier |
| Creative image/video | `img[src*='fbcdn']`, `video` | Download via BrowserOS |
| Headline | `[data-testid='ad-headline']` | Main hook |
| Primary text | `[data-testid='ad-body']` | Body copy |
| CTA button | `[data-testid='ad-cta-button']` | "Learn More", "Install", etc. |
| Advertiser | `[data-testid='ad-advertiser']` | Page name |
| Started running | `[data-testid='ad-start-date']` | Approximate launch date |
| Platforms | `[data-testid='ad-platforms']` | FB, IG, Messenger, Audience Network |

### Rate Limiting
- Scroll delay: 2-3s between scrolls
- Page delay: 5-10s between different searches
- Rotate queries to avoid fingerprinting

---

## TikTok Creative Center Scraping

### Target URLs
- `https://ads.tiktok.com/creative-center?region=RU&industry=<vertical>`
- `https://ads.tiktok.com/creative-center/inspiration/popular?region=RU`

### Navigation Pattern
```python
# Requires login for full access - use authenticated session cookies
await browser.nav(page_id).goto("https://ads.tiktok.com/creative-center?region=RU&industry=gaming")
await browser.wait(page_id, for_="selector", value=".CreativeCard", timeout=20000)
```

### Data to Extract
| Field | Notes |
|-------|-------|
| Video thumbnail | Download for visual analysis |
| Hook (first 3s) | Critical for CTR |
| Caption/description | Text overlay strategy |
| Music/sound | Trending audio = higher reach |
| Hashtags | Niche targeting signals |
| Duration | 15-30s optimal for ads |
| Likes/shares/comments | Engagement proxy |

---

## CPA Network Dashboard Scraping

### Networks & Patterns
| Network | Dashboard URL | Auth | Key Data |
|---------|---------------|------|----------|
| AdCombo | `https://adcombo.com/offers` | Cookie-based | Offer list, payouts, caps, landers |
| CPAlead | `https://cpalead.com/offers` | Cookie-based | Content locking offers, EPC |
| Alfaleads | `https://alfaleads.com/offers` | Cookie-based | Nutra/gaming, exclusive offers |
| MaxBounty | `https://maxbounty.com/affiliates/offers` | Cookie-based | High-payout CPA, approval rates |

### Generic Scraping Pattern
```python
# 1. Set auth cookies (from user's logged-in session)
await browser.cdp(page_id, "Network.setCookie", {
    "name": "session_id", "value": cookie_value, "domain": ".network.com", "path": "/"
})

# 2. Navigate to offers page
await browser.nav(page_id).goto("https://network.com/offers?vertical=gaming&geo=RU")
await browser.wait(page_id, for_="selector", value=".offer-row, .offer-card", timeout=15000)

# 3. Extract offer cards
snapshot = await browser.observe(page_id).snapshot()
# Parse: offer_id, name, vertical, geo, payout, conversion_type, approval_rate, EPC, CR, restrictions, landing_url
```

---

## Worker Brief Template (for delegate_task)

```json
{
  "goal": "Scrape FB Ad Library for gaming CPI creatives in RU. Extract top 20 ads by engagement signals.",
  "context": {
    "geo": "RU",
    "vertical": "gaming",
    "traffic_source": "facebook",
    "competitor_domains": ["raid-shadow-legends.com", "plarium.com"]
  },
  "role": "leaf",
  "tools_required": ["browser-automation"],
  "mcp_servers": ["browseros"],
  "browser_patterns": ["creative-intel-scraping"],
  "acceptance": [
    "20+ ad creatives with images/videos downloaded",
    "Headline, body, CTA, advertiser for each",
    "Engagement signals (likes, comments, running time)",
    "Creative format breakdown: video vs image vs carousel"
  ]
}
```

---

## BrowserOS MCP Commands Reference

| Command | Purpose |
|---------|---------|
| `browser.pages.newPage(url)` | Open new page |
| `browser.observe(pageId).snapshot()` | Get accessibility tree with refs |
| `browser.observe(pageId).diff()` | See what changed after action |
| `browser.input(pageId).scroll("down", amount=5)` | Scroll page |
| `browser.input(pageId).click(ref)` | Click element |
| `browser.cdp(pageId, "Network.setCookie", {...})` | Set auth cookies |
| `browser.cdp(pageId, "Page.captureScreenshot", {...})` | Screenshot |
| `browser.pages.close(pageId)` | Clean up |

---

## Common Pitfalls & Fixes

| Issue | Fix |
|-------|-----|
| "Selector not found" | Wait longer, use `wait` with selector, page may not be fully rendered |
| Login wall | Pre-set cookies via CDP, or navigate to login first |
| Rate limited (429) | Add delays, rotate user agents, use residential proxies |
| Infinite scroll stops | Check for "Load more" button, click instead of scroll |
| Video won't play | Use `cdp` to capture network request for video URL, download directly |
| CAPTCHA | Can't bypass reliably — skip and log, try different IP/proxy next run |

---

## Output Format (Worker Return)

```json
{
  "source": "facebook_ads_library",
  "geo": "RU",
  "vertical": "gaming",
  "scraped_at": "2026-07-23T00:15:00Z",
  "creatives": [
    {
      "ad_id": "123456789",
      "advertiser": "Raid Shadow Legends",
      "headline": "Get 50,000 Silver Free!",
      "body": "Install now and claim your legendary champion...",
      "cta": "Install",
      "media_type": "video",
      "media_url": "https://video.fbcdn.net/...",
      "platforms": ["facebook", "instagram"],
      "started_running": "2026-07-01",
      "engagement_signals": {"likes": 12000, "comments": 340, "shares": 890}
    }
  ],
  "summary": {
    "total_ads": 20,
    "video_ratio": 0.7,
    "top_hooks": ["Free silver", "Legendary champion", "No grind"],
    "dominant_format": "gameplay + reward"
  }
}
```

---

## Standardized Output Schema (for cross-source normalization)

```json
{
  "source": "facebook_ads_library | tiktok_creative_center | cpa_network_dashboard",
  "query": {"vertical": "gaming", "geo": "RU", "keywords": ["raid", "shadow", "legends"]},
  "scraped_at": "2026-07-23T00:15:00Z",
  "creatives": [
    {
      "creative_id": "fb_123456789",
      "platform": "facebook",
      "format": "image | video | carousel",
      "media_urls": ["https://scontent.xx.fbcdn.net/..."],
      "headline": "Install & Get 50K Silver!",
      "primary_text": "Join millions of players...",
      "cta": "Install Now",
      "landing_url": "https://raid-shadow-legends.com/ru?utm_source=fb",
      "impressions_range": "100K-500K",
      "first_seen": "2026-07-01",
      "last_seen": "2026-07-22",
      "language": "ru",
      "screenshot_path": "/cache/creative_radar/screenshots/fb_123456789.png"
    }
  ],
  "metadata": {
    "total_found": 47,
    "extracted": 32,
    "errors": [],
    "accounts_used": ["account_1", "account_2"]
  }
}
```

---

## Screenshot Capture (for verification)

```python
# After extraction, capture screenshot of each creative card
for i, creative in enumerate(creatives):
    await browser.cdp(page, "Page.captureScreenshot", {
        "format": "png",
        "clip": {"x": creative.x, "y": creative.y, "width": 500, "height": 600},
        "captureBeyondViewport": false
    })
    # Save to cache/creative_radar/screenshots/
```

---

## Integration with Multi-Agent Researcher

```python
# In orchestrator (always-on-agent):
tasks = [
    {
        "goal": "Extract FB Ad Library creatives for gaming CPI in RU - Raid Shadow Legends competitors",
        "context": {"source": "facebook_ads_library", "vertical": "gaming", "geo": "RU", "keywords": ["raid", "shadow", "legends", "rpg", "fantasy"]},
        "tools_required": ["browser-automation", "mcp-browseros"],
        "role": "leaf"
    },
    {
        "goal": "Extract TikTok Creative Center creatives for finance RU - credit cards, microloans",
        "context": {"source": "tiktok_creative_center", "vertical": "finance", "geo": "RU", "keywords": ["кредит", "займ", "карта", "кэшбэк"]},
        "tools_required": ["browser-automation", "mcp-browseros"],
        "role": "leaf"
    }
]
results = await delegate_task(tasks=tasks, timeout=300)
```

---

## Pre-Dispatch Checklist (Orchestrator)

- [ ] BrowserOS MCP running: `curl http://localhost:9003/mcp` → 200 OK
- [ ] `browser-automation` skill available
- [ ] Worker brief includes `tools_required: ["browser-automation"]`
- [ ] Timeout set to 300s (not default 600s)
- [ ] Acceptance criteria include visual verification (screenshots)
- [ ] Account cookies/credentials available in secure store