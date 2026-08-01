# Multi-Agent Researcher — Worker Timeout Fix (2026-07-22)

## Problem

Workers dispatched via `delegate_task` for web research (FB Ad Library, TikTok Creative Center, CPA network dashboards) **timed out after 600s** with only 18-24 API calls completed.

**Root cause**: Workers used `web_search` + `web_extract` which:
1. Cannot access authenticated areas (network dashboards)
2. Cannot scrape JS-heavy SPAs (FB Library, TikTok CC)
3. Hit rate limits on public search APIs
4. No visual verification of extracted data

## Solution: BrowserOS MCP Integration

Give workers real browser automation tools via `browser-automation` skill (wraps BrowserOS MCP).

### Updated Worker Brief Template

```markdown
GOAL: Research top 10 NEW CPA offers for India (gambling/PWA/dating)
CONTEXT:
  - Networks: AdCombo, CPAlead, MaxBounty, CPATrend, Alfaleads
  - Geo: IN
  - Verticals: gambling/sports betting, PWA installs, dating
  - Min payout: $3+, Min cap: $1k/day
  - BrowserOS MCP available at http://127.0.0.1:9003/mcp
ACCEPTANCE:
  - JSON array with 10 offers
  - Each: offer_id, network, vertical, payout, flow, cap, geo, lander_url, restrictions, creatives_allowed, approval_difficulty, source_url, confidence_score
  - Screenshots of offer pages saved
FORMAT: JSON
TOOLS_ALLOWED: browser-automation (navigate_page, click_element, take_snapshot, evaluate_script, take_screenshot), web_search (fallback only)
```

### Browser Automation Patterns for CPA Research

#### 1. AdCombo Offer Scraping
```python
# Navigate to offers page (requires login - use saved session)
await navigate_page("https://adcombo.com/offers")
# Filter: Geo=IN, Vertical=Gambling/Dating
await click_element("select[name='geo'] option[value='IN']")
await click_element("select[name='vertical'] option[value='gambling']")
# Extract offer cards
offers = await evaluate_script("""
  return Array.from(document.querySelectorAll('.offer-card')).map(card => ({
    id: card.dataset.offerId,
    name: card.querySelector('.offer-name').textContent,
    payout: card.querySelector('.payout').textContent,
    cap: card.querySelector('.cap').textContent,
    flow: card.querySelector('.flow').textContent,
    landerUrl: card.querySelector('.lander-link').href
  }))
""")
```

#### 2. FB Ad Library Creative Scraping
```python
await navigate_page("https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=IN&q=cricket%20betting")
# Scroll to load more
for _ in range(5):
    await evaluate_script("window.scrollTo(0, document.body.scrollHeight)")
    await asyncio.sleep(2)
# Extract ad cards
creatives = await evaluate_script("""
  return Array.from(document.querySelectorAll('[data-testid="ad-card"]')).map(card => ({
    hook: card.querySelector('.ad-primary-text')?.textContent,
    format: card.querySelector('.ad-format')?.textContent,
    cta: card.querySelector('.ad-cta')?.textContent,
    landerUrl: card.querySelector('a[href*="l.php"]')?.href,
    impressions: card.querySelector('.impressions')?.textContent
  }))
""")
```

#### 3. TikTok Creative Center
```python
await navigate_page("https://ads.tiktok.com/creative-center?region=IN&category=gaming")
# Similar extraction pattern
```

## Expected Improvement

| Metric | Before (web_search) | After (BrowserOS MCP) |
|---|---|---|
| Success rate | ~10% (timeouts) | ~90% |
| Authenticated data | No | Yes (saved sessions) |
| JS-rendered content | No | Yes |
| Visual verification | No | Screenshots |
| Time per worker | 600s (timeout) | 60-120s |

## Deployment

1. BrowserOS running with MCP enabled (port 9003)
2. `browser-automation` skill loaded (wraps BrowserOS MCP)
3. Workers get `tools_exposed: [navigate_page, click_element, take_snapshot, evaluate_script, take_screenshot, new_hidden_page]`
4. Session persistence via BrowserOS profile (cookies, localStorage saved)