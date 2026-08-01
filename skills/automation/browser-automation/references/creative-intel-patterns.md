# Creative Intelligence Patterns — FB Library + TikTok CC

Scraping patterns for ad creative analysis using BrowserOS/BrowserClaw.

---

## Facebook Ad Library (`https://www.facebook.com/ads/library/`)

### URL Patterns
```
https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=IN&media_type=all&q=cricket%20betting
https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=IN&media_type=all&q=pwa%20install
https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=IN&media_type=all&q=dating%20app
```

### Parameters
| Param | Values | Description |
|---|---|---|
| `country` | `IN`, `US`, `DE`, etc. | Target country |
| `active_status` | `all`, `active`, `inactive` | Ad status |
| `ad_type` | `all`, `political`, `issue`, `housing`, `employment`, `credit` | Ad category |
| `media_type` | `all`, `image`, `video`, `meme` | Creative format |
| `q` | URL-encoded query | Search term |
| `search_type` | `keyword`, `advertiser` | Search mode |

---

## FB Library Scraping Flow

```python
async def scrape_fb_library(query: str, country: str = "IN", max_ads: int = 50):
    """Scrape FB Ad Library for given query."""
    
    url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&media_type=all&q={quote(query)}"
    
    page = await mcp__browseros__new_page(url=url)
    await mcp__browseros__wait(page=page, for="time", value=5000)  # Initial load
    
    # Handle cookie consent if present
    snapshot = await mcp__browseros__take_enhanced_snapshot(page=page)
    # Find "Accept all" or "Allow all" button
    # ref = find_ref(snapshot, "button:has-text('Allow')")
    # if ref: await mcp__browseros__click(page=page, ref=ref)
    
    ads = []
    last_height = 0
    
    while len(ads) < max_ads:
        # Scroll to bottom
        await mcp__browseros__evaluate_script(page=page, script="window.scrollTo(0, document.body.scrollHeight)")
        await mcp__browseros__wait(page=page, for="time", value=2000)
        
        # Extract ad cards
        new_ads = await mcp__browseros__evaluate_script(page=page, script="""
          return Array.from(document.querySelectorAll('[data-testid="ad-card"], .ad-card, [role="article"]')).map(card => {
            const getText = (sel) => card.querySelector(sel)?.textContent?.trim() || '';
            const getAttr = (sel, attr) => card.querySelector(sel)?.[attr] || '';
            
            return {
              advertiser: getText('[data-testid="advertiser-name"], .advertiser-name, [data-testid="page-name"]'),
              cta: getText('[data-testid="cta-button"], .cta-button, button'),
              headline: getText('[data-testid="ad-headline"], .ad-headline, h3'),
              body: getText('[data-testid="ad-body"], .ad-body, .ad-text'),
              creative_url: getAttr('img, video', 'src') || getAttr('[data-testid="ad-image"] img', 'src'),
              impressions: getText('[data-testid="impressions"], .impressions, .ad-impressions'),
              spend: getText('[data-testid="spend"], .spend'),
              lander_url: getAttr('a[href^="http"]', 'href'),
              library_id: card.dataset.adId || card.dataset.libraryId || card.id,
              scraped_at: new Date().toISOString()
            };
          }).filter(a => a.advertiser || a.headline || a.creative_url);
        """)
        
        ads.extend(new_ads)
        
        # Check if we've reached the end
        new_height = await mcp__browseros__evaluate_script(page=page, script="document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    await mcp__browseros__close_page(page=page)
    return ads[:max_ads]
```

---

## FB Ad Card Selectors (May 2026)

| Element | Selector Options |
|---|---|
| Ad Card Container | `[data-testid="ad-card"]`, `.ad-card`, `[role="article"]` |
| Advertiser Name | `[data-testid="advertiser-name"]`, `.advertiser-name`, `[data-testid="page-name"]` |
| Headline | `[data-testid="ad-headline"]`, `.ad-headline`, `h3` |
| Body Text | `[data-testid="ad-body"]`, `.ad-body`, `.ad-text` |
| CTA Button | `[data-testid="cta-button"]`, `.cta-button`, `button` |
| Creative (Image/Video) | `img`, `video`, `[data-testid="ad-image"] img` |
| Impressions | `[data-testid="impressions"]`, `.impressions` |
| Spend Range | `[data-testid="spend"]`, `.spend` |
| Landing Page Link | `a[href^="http"]` (first external link) |
| Library ID | `data-testid="ad-card"` → `data-library-id` or `data-ad-id` |

---

## TikTok Creative Center (`https://ads.tiktok.com/creative-center`)

### URL Patterns
```
https://ads.tiktok.com/creative-center/region/IN?category=gaming&period=7
https://ads.tiktok.com/creative-center/region/IN?category=apps&period=30
```

### Parameters
| Param | Values |
|---|---|
| `region` | `IN`, `US`, `ID`, `BR`, etc. |
| `category` | `gaming`, `apps`, `ecommerce`, `education`, `finance`, `all` |
| `period` | `7`, `30`, `90` (days) |

---

## TikTok CC Scraping Flow

```python
async def scrape_tiktok_cc(region: str = "IN", category: str = "gaming", period: int = 7, max_items: int = 50):
    """Scrape TikTok Creative Center top creatives."""
    
    url = f"https://ads.tiktok.com/creative-center/region/{region}?category={category}&period={period}"
    
    page = await mcp__browseros__new_page(url=url)
    await mcp__browseros__wait(page=page, for="time", value=5000)
    
    # Handle region/category selection if not in URL
    # ...
    
    creatives = []
    
    while len(creatives) < max_items:
        # Scroll
        await mcp__browseros__evaluate_script(page=page, script="window.scrollTo(0, document.body.scrollHeight)")
        await mcp__browseros__wait(page=page, for="time", value=2000)
        
        # Extract
        new_creatives = await mcp__browseros__evaluate_script(page=page, script="""
          return Array.from(document.querySelectorAll('.CreativeCard, .creative-card, [data-testid="creative-card"]')).map(card => {
            const getText = (sel) => card.querySelector(sel)?.textContent?.trim() || '';
            const getAttr = (sel, attr) => card.querySelector(sel)?.[attr] || '';
            
            return {
              video_url: getAttr('video', 'src') || getAttr('[data-video-url]', 'data-video-url'),
              thumbnail: getAttr('img', 'src'),
              title: getText('.title, .creative-title, h3'),
              advertiser: getText('.advertiser, .brand-name, [data-advertiser]'),
              cta: getText('.cta, .call-to-action, button'),
              impressions: getText('.impressions, .view-count, [data-impressions]'),
              likes: getText('.likes, .like-count'),
              comments: getText('.comments, .comment-count'),
              shares: getText('.shares, .share-count'),
              music: getText('.music, .sound-title'),
              hashtags: Array.from(card.querySelectorAll('.hashtag, .tag')).map(h => h.textContent.trim()),
              lander_url: getAttr('a[href^="http"]', 'href'),
              scraped_at: new Date().toISOString()
            };
          }).filter(c => c.video_url || c.thumbnail);
        """)
        
        creatives.extend(new_creatives)
        
        # Check end
        height = await mcp__browseros__evaluate_script(page=page, script="document.body.scrollHeight")
        if len(creatives) >= max_items or (await mcp__browseros__evaluate_script(page=page, script="document.body.scrollHeight")) == height:
            # Try one more scroll
            pass
    
    await mcp__browseros__close_page(page=page)
    return creatives[:max_items]
```

---

## TikTok Creative Card Selectors

| Element | Selector Options |
|---|---|
| Creative Card | `.CreativeCard`, `.creative-card`, `[data-testid="creative-card"]` |
| Video | `video`, `[data-video-url]` |
| Thumbnail | `img` (first in card) |
| Title | `.title`, `.creative-title`, `h3` |
| Advertiser | `.advertiser`, `.brand-name`, `[data-advertiser]` |
| CTA | `.cta`, `.call-to-action`, `button` |
| Impressions | `.impressions`, `.view-count`, `[data-impressions]` |
| Likes | `.likes`, `.like-count` |
| Music/Sound | `.music`, `.sound-title` |
| Hashtags | `.hashtag`, `.tag` |
| Landing Link | `a[href^="http"]` |

---

## Creative Analysis Schema

```json
{
  "creative_id": "fb_123456|tt_789012",
  "platform": "facebook|tiktok",
  "advertiser": "string",
  "hook": "first 3 seconds / headline",
  "angle": "emotional|rational|ugc|native|fear|greed|social_proof",
  "format": "video|image|carousel|story|reel",
  "cta": "Install Now / Learn More / Sign Up / Play Now",
  "creative_url": "https://...",
  "lander_url": "https://...",
  "impressions_est": 150000,
  "engagement_rate": 0.042,
  "targeting_signals": {
    "geo": "IN",
    "interests": ["cricket", "betting", "gaming"],
    "age": "18-35",
    "gender": "M"
  },
  "creative_elements": {
    "has_face": true,
    "has_text_overlay": true,
    "has_countdown": false,
    "has_social_proof": true,
    "language": "en-IN"
  },
  "scraped_at": "2026-07-22T...",
  "freshness_score": 0.9
}
```

---

## Competitive Analysis Queries (India Market)

### Gambling/Sports Betting
- FB: `cricket betting`, `IPL betting`, `sports betting India`, `casino India`
- TT: `gaming` category, filter by advertisers with "bet", "casino", "win"

### PWA Installs
- FB: `PWA install`, `progressive web app`, `add to homescreen`
- TT: `apps` category, look for "Install" CTA

### Dating
- FB: `dating app India`, `meet singles India`, `match dating`
- TT: `lifestyle` or `apps` category, dating advertisers

---

## Rate Limiting & Best Practices

| Platform | Limits | Mitigation |
|---|---|---|
| FB Library | ~100 requests/15min per IP | Residential proxy, rotate UA |
| TikTok CC | ~50 requests/15min | Same + longer delays |

### Delays
```python
# Between scrolls
await asyncio.sleep(random.uniform(1.5, 3.0))

# Between queries
await asyncio.sleep(random.uniform(5.0, 10.0))

# Per platform session
MAX_ADS_PER_SESSION = 100
SESSION_DURATION = 300  # 5 min
```

---

## Output Files

```python
# Save to Knowledge Cube
on_task_complete(
    content=f"Creative intel: {len(ads)} FB ads + {len(tiktoks)} TikTok creatives for India {vertical}",
    tags=["creative-intel", vertical, "india", platform],
    source="agent"
)
```

---

## Integration with Multi-Agent Researcher

**Worker Brief Template:**
```json
{
  "goal": "Scrape FB Library + TikTok CC for India cricket betting creatives",
  "tools_required": ["browser-automation", "mcp-browseros"],
  "mcp_servers": ["browseros"],
  "queries": ["cricket betting India", "IPL betting", "cricket PWA install"],
  "platforms": ["facebook", "tiktok"],
  "max_per_platform": 20,
  "acceptance": [
    "20+ FB ad cards with advertiser, creative, CTA, lander",
    "20+ TikTok creatives with video, engagement, advertiser",
    "All have source URLs and timestamps",
    "Saved to KC with tags: creative-intel, india, gambling"
  ]
}
```