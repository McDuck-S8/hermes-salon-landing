# CPA Network Scraping Patterns

Patterns for scraping major CPA networks using BrowserOS MCP.

## AdCombo (`https://www.adcombo.com/offers`)

### Authentication
- Login page: `https://www.adcombo.com/login`
- After login, session cookie persists
- If session expires, redirect to login

### Offer Listing Page Structure
```
https://www.adcombo.com/offers
- GEO filter: select#geo_filter (or .geo-filter)
- Vertical filter: select#vertical_filter (or .vertical-filter)
- Search: input#offer_search
- Offer cards: .offer-card, .offer-row, [data-offer-id]
```

### Offer Card Selectors
```javascript
// Common patterns (verify with snapshot)
{
  id: c.dataset.offerId || c.querySelector('[data-offer-id]')?.dataset.offerId,
  name: c.querySelector('.offer-name, .offer-title, h3, h4')?.textContent?.trim(),
  payout: c.querySelector('.payout, .price, [data-payout]')?.textContent?.trim(),
  cap: c.querySelector('.cap, .daily-cap, [data-cap]')?.textContent?.trim(),
  flow: c.querySelector('.flow, .conversion-flow, [data-flow]')?.textContent?.trim(),
  lander: c.querySelector('a.lander, a[href*="land"], a[href*="preview"]')?.href,
  geo: c.querySelector('.geo, .country, [data-geo]')?.textContent?.trim(),
  vertical: c.querySelector('.vertical, .category, [data-vertical]')?.textContent?.trim()
}
```

### Filtering for India Gambling/PWA/Dating
```python
# 1. GEO filter -> India (IN)
# 2. Vertical filter -> Gambling/Sports/PWA/Install/Dating
# 3. Payout filter -> $3+ (if available)
# 4. Cap filter -> $1000+/day (if available)
```

### Pagination
- "Load more" button: `.load-more, .show-more, button:has-text("Load")`
- Or infinite scroll: `window.scrollTo(0, document.body.scrollHeight)`

---

## CPAlead (`https://www.cpalead.com/offers`)

### Marketplace Structure
```
https://www.cpalead.com/offers
- Category tabs: CPA, CPI, CPS
- GEO filter: select[name="country"]
- Vertical: select[name="vertical"]
- Sort: payout, conversion rate, EPC
```

### Offer Card
```javascript
{
  id: c.dataset.offerId,
  name: c.querySelector('.offer-title, .offer-name')?.textContent,
  payout: c.querySelector('.payout, .offer-payout')?.textContent,
  cap: c.querySelector('.cap, .daily-cap')?.textContent,
  lander: c.querySelector('.lander-link, a[href*="track"]')?.href,
  preview: c.querySelector('.preview-link, a[href*="preview"]')?.href
}
```

---

## Alfaleads (`https://alfaleads.com/offers`)

### Structure
```
- Login required
- Offers page with filters
- API available for partners (if approved)
```

---

## MaxBounty (`https://www.maxbounty.com/offers`)

### Structure
```
- Requires account approval
- Offers page with advanced filters
- Good for high-ticket India offers
```

---

## CPATrend (`https://cpatrend.com/offers`)

### Structure
```
- Newer network, growing India vertical
- Clean offer cards
- API access on request
```

---

## Generic Scraping Function (Reusable)

```python
async def scrape_cpa_network(network: str, geo: str = "IN", verticals: list = None, min_payout: float = 3.0):
    """
    Scrape offers from a CPA network.
    Returns: list[dict] with normalized fields
    """
    configs = {
        "adcombo": {
            "url": "https://www.adcombo.com/offers",
            "geo_filter": "#geo_filter",
            "vertical_filter": "#vertical_filter",
            "offer_selector": ".offer-card, .offer-row",
            "login_url": "https://www.adcombo.com/login"
        },
        "cpalead": {
            "url": "https://www.cpalead.com/offers",
            "geo_filter": "select[name='country']",
            "vertical_filter": "select[name='vertical']",
            "offer_selector": ".offer-item, .offer-card",
            "login_url": "https://www.cpalead.com/login"
        }
    }
    
    cfg = configs.get(network.lower())
    if not cfg:
        raise ValueError(f"Unknown network: {network}")
    
    # Navigate, filter, extract
    page = await mcp__browseros__new_page(url=cfg["url"])
    await mcp__browseros__wait(page=page, for="time", value=3000)
    
    # Handle login if needed
    if "login" in await mcp__browseros__extract_content(page=page, format="text"):
        # Alert user or use stored session
        pass
    
    # Apply filters
    await mcp__browseros__click(page=page, ref=ref_geo_filter)
    await mcp__browseros__click(page=page, ref=ref_geo_india)
    if verticals:
        for v in verticals:
            await mcp__browseros__click(page=page, ref=ref_vertical_dropdown)
            await mcp__browseros__click(page=page, ref=ref_vertical_option(v))
    
    await mcp__browseros__wait(page=page, for="time", value=2000)
    
    # Extract
    offers = await mcp__browseros__evaluate_script(page=page, script=f"""
      // Use config-specific selectors
    """)
    
    await mcp__browseros__close_page(page=page)
    return offers
```

---

## Rate Limiting & Stealth

| Network | Limits | Stealth |
|---|---|---|
| AdCombo | Moderate | Rotate user-agent, add delays |
| CPAlead | Strict | Use residential proxy |
| Alfaleads | Moderate | Standard |
| MaxBounty | Strict | Proxy required |
| CPATrend | Light | Standard |

---

## Output Normalization

All networks → unified schema:
```json
{
  "offer_id": "string",
  "network": "adcombo|cpalead|alfaleads|maxbounty|cpatrend",
  "name": "string",
  "vertical": "gambling|pwa|install|dating|nutra|sweepstakes|finance",
  "geo": "IN",
  "payout_usd": 4.50,
  "cap_daily_usd": 5000,
  "flow": "CPI|CPL|CPS|CPA|SOI|DOI",
  "lander_url": "https://...",
  "preview_url": "https://...",
  "restrictions": ["no_email", "no_social", "cloaking_required"],
  "creative_guidelines": "no_misleading, no_celebrity",
  "approval_difficulty": "easy|medium|hard",
  "scraped_at": "2026-07-22T...",
  "confidence": 0.85
}
```