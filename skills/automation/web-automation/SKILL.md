---
name: web-automation
description: "Browser automation for web interfaces using Playwright + Ghost-surfer. Anti-detect, proxy support (v2rayN), selectors config for GitHub, GitLab, YouTube, Dzen, VC.ru."
trigger: "When user asks to automate web tasks: create repo, upload file, publish article, upload video, scrape data, login, interact with UI."
usage: web-automation
argument-hint: "[craft|execute|scrape|test] [target_site] [action]"
allowed-tools:
  - Bash(npx playwright *)
  - Bash(python scripts/web_automation.py *)
  - Read(*)
  - Write(*)
  - Glob(*)
---

# Web Automation — Browser Automation Skill

Playwright-based browser automation with Ghost-surfer anti-detect integration, v2rayN proxy support, and site-specific selector configs.

## Architecture

```
web-automation/
├── SKILL.md                    # This file
├── scripts/
│   ├── web_automation.py      # Main engine: browser init, actions, logging
│   ├── config_loader.py       # Site config loader
├── configs/                   # Site-specific selectors & steps
│   ├── github.json
│   ├── gitlab.json
│   ├── youtube.json
│   ├── dzen.json
│   ├── vc_ru.json
│   ├── ozon.json              # Ozon marketplace config
│   ├── wb.json                # Wildberries marketplace config
├── references/
    ├── site_structure.md      # General principles
    └── marketplace-limitations.md  # Ozon/WB anti-bot protection analysis
```

## Quick Start

```bash
# Test: create GitHub repo (requires auth)
python scripts/web_automation.py --site github --action create_repo --params '{"name":"test-repo","private":false}'

# Scrape: get article from VC.ru
python scripts/web_automation.py --site vc_ru --action scrape_article --params '{"url":"https://vc.ru/..."}'

# Marketplace: search products on Ozon
python scripts/web_automation.py --site ozon --action search_products --params '{"query":"светодиодные лампы","limit":20,"sort":"price"}'

# Marketplace: get product details from Wildberries
python scripts/web_automation.py --site wb --action get_product_details --params '{"url":"https://www.wildberries.ru/catalog/12345678/detail.aspx"}'

# Test browser launch
python scripts/web_automation.py --test-browser
```

## Core Engine: web_automation.py

### Browser Initialization
```python
from web_automation import BrowserAutomation

async with BrowserAutomation(proxy="socks5://127.0.0.1:10806") as bot:
    await bot.goto("https://github.com")
    await bot.click('button[data-testid="new-repo"]')
    await bot.fill('input[name="repository[name]"]', "my-repo")
    await bot.click('button[type="submit"]')
```

### Available Actions
| Action | Description |
|--------|-------------|
| `goto(url)` | Navigate to URL |
| `click(selector)` | Click element |
| `fill(selector, value)` | Fill input |
| `type(selector, text)` | Type with delay |
| `select(selector, value)` | Select dropdown |
| `wait(selector, timeout)` | Wait for element |
| `screenshot(path)` | Take screenshot |
| `scroll(direction)` | Scroll page |
| `evaluate(js)` | Execute JS |
| `cookies()` | Get/set cookies |
| `storage_state(path)` | Save auth state |

### Marketplace Methods
| Method | Description |
|--------|-------------|
| `search_and_extract(query, site, limit, sort, min_price, max_price, pages)` | Search products and extract structured data |
| `get_product_details(url)` | Get detailed product information |
| `get_reviews(url, limit)` | Get reviews for a product |
| `_send_to_knowledge_cube(query, site, products)` | Send products to Knowledge Cube |

### Proxy & Anti-Detect
```python
BrowserAutomation(
    proxy="socks5://127.0.0.1:10806",  # v2rayN
    headless=False,
    ghost_surfer=True,  # Use Ghost-surfer if available
    stealth=True,       # Playwright stealth mode fallback
    user_agent="custom",  # Random UA
)
```

## Config Loader

```python
from config_loader import load_site_config

config = load_site_config("github")
selector = config["selectors"]["new_repo_button"]
steps = config["steps"]["create_repo"]
```

## Site Configs

Each site config in `configs/*.json`:
```json
{
  "base_url": "https://github.com",
  "login_required": true,
  "auth_type": "cookie",
  "selectors": { "new_repo_button": "..." },
  "steps": {
    "create_repo": [
      { "action": "goto", "url": "/new" },
      { "action": "fill", "selector": "...", "param": "name" },
      { "action": "click", "selector": "..." }
    ]
  }
}
```

## Supported Sites

| Site | Config | Actions |
|------|--------|---------|
| GitHub | `github.json` | create_repo, create_issue, create_pr, upload_file, release |
| GitLab | `gitlab.json` | create_project, merge_request, pipeline |
| YouTube | `youtube.json` | upload_video, edit_metadata, schedule |
| Dzen | `dzen.json` | publish_article, edit_post |
| VC.ru | `vc_ru.json` | publish_article, comment |
| **Ozon** | `ozon.json` | search_products, extract_product_list, get_product_details, get_reviews, filter_by_price, sort_by_price_asc |
| **Wildberries** | `wb.json` | search_products, extract_product_list, get_product_details, get_reviews, filter_by_price, sort_by_price_asc |

## Marketplace Automation (Ozon & Wildberries)

### Config Structure
Each marketplace config includes:
- **selectors** — CSS/XPath selectors for product cards, prices, ratings, reviews, characteristics
- **steps** — Pre-defined action sequences (search, filter, sort, extract, pagination)
- **evaluation_scripts** — JavaScript executed in browser context for data extraction

### Ozon (`configs/ozon.json`)
- **Base URL**: `https://www.ozon.ru`
- **Search**: `/search/?text={query}&sort=price`
- **Actions**: search_products, extract_product_list, get_product_details, get_reviews, filter_by_price, sort_by_price_asc
- **Evaluation scripts**: extractProductList, extractProductDetails, extractReviews
- **Extracted fields**: title, price, old_price, rating, reviews_count, link, image, characteristics, availability, seller, brand, article, images

### Wildberries (`configs/wb.json`)
- **Base URL**: `https://www.wildberries.ru`
- **Search**: `/catalog/0/search.aspx?search={query}&sort=price`
- **Actions**: search_products, extract_product_list, get_product_details, get_reviews, filter_by_price, sort_by_price_asc
- **Evaluation scripts**: extractProductList, extractProductDetails, extractReviews
- **Extracted fields**: title, brand, price, old_price, rating, reviews_count, link, image, characteristics, availability, seller, brand, article, sizes, colors, images

### Marketplace Methods (added to BrowserAutomation)

| Method | Description |
|--------|-------------|
| `search_and_extract(query, site='ozon', limit=20, sort='price', min_price=0, max_price=1000000, pages=3)` | Search products with price sorting, price filtering, pagination |
| `get_product_details(url)` | Extract full product details including characteristics, reviews, availability |
| `get_reviews(url, limit=5)` | Extract up to 5 reviews with rating, text, date |
| `_send_to_knowledge_cube(query, site, products)` | Auto-send extracted products to Knowledge Cube |

### Usage Example
```python
async with BrowserAutomation(proxy="socks5://127.0.0.1:10806") as bot:
    # Search Ozon for diapers with price filter
    results = await bot.search_and_extract(
        query="памперсы трусики размер по талии от 60 см 30 шт",
        site="ozon",
        limit=10,
        sort="price",
        min_price=100,
        max_price=5000,
        pages=2
    )
    
    # Get detailed product info
    for product in results[:3]:
        details = await bot.get_product_details(product["link"])
        print(f"{details['title']}: {details['price']} RUB, Rating: {details['rating']}")
        print(f"Characteristics: {details.get('characteristics', {})}")
        print(f"Availability: {details.get('availability')}")
```

### Marketplace Config Structure
```json
{
  "base_url": "https://www.ozon.ru",
  "search_url": "/search/?text={query}&sort=price",
  "selectors": { "product_cards": "...", "product_price": "..." },
  "steps": {
    "search_products": [{ "action": "goto", "url": "/search/?text={query}&sort=price" }, ...],
    "extract_product_list": [{ "action": "evaluate", "script": "extractProductList" }]
  },
  "evaluation_scripts": {
    "extractProductList": "() => { ... }",
    "extractProductDetails": "() => { ... }",
    "extractReviews": "() => { ... }"
  }
}
```

## Ghost-surfer Integration

```python
# Auto-detect Ghost-surfer
from web_automation import detect_ghost_surfer

if detect_ghost_surfer():
    # Use Ghost-surfer browser
    browser = await launch_ghost_surfer(proxy="socks5://127.0.0.1:10806")
else:
    # Fallback: Playwright stealth
    browser = await launch_playwright_stealth(proxy="socks5://127.0.0.1:10806")
```

## Anti-Detect Features

| Feature | Playwright | Ghost-surfer |
|---------|------------|--------------|
| Canvas fingerprint | ✅ | ✅ |
| WebGL fingerprint | ✅ | ✅ |
| Audio fingerprint | ✅ | ✅ |
| Font enumeration | ✅ | ✅ |
| Navigator props | ✅ | ✅ |
| Proxy rotation | ✅ | ✅ |
| Behavior simulation | ✅ | ✅ |

## Browser Launch in Geo-Restricted Regions (Russia)

### Problem
Playwright CDN (cdn.playwright.dev) is geo-blocked in Russia (403 Access Denied), preventing automatic Chromium download.

### Solutions

#### 1. Use System Edge/Chrome via Channel Parameter
```python
# Use installed Edge/Chrome via channel parameter
self.browser = await self.playwright.chromium.launch(
    headless=self.config.headless,
    args=launch_args,
    channel="msedge",  # or "chrome" for Chrome
    # executable_path="D:\\Program Files (x86)\\Microsoft\\Edge Dev\\Application\\msedge.exe",  # explicit path
)
```

**Found on system:**
- Edge Dev: `D:\Program Files (x86)\Microsoft\Edge Dev\Application\msedge.exe`
- Chrome: Not installed by default

#### 2. Use System Browser via Executable Path
```python
self.browser = await self.playwright.chromium.launch(
    headless=self.config.headless,
    args=launch_args,
    executable_path="D:\\Program Files (x86)\\Microsoft\\Edge Dev\\Application\\msedge.exe",
)
```

#### 3. HTTP Fallback via v2rayN Proxy (No Browser Needed)
Since Ozon/WB have mobile APIs, use `httpx` through v2rayN proxy:
```python
import httpx

async with httpx.AsyncClient(proxy="socks5://127.0.0.1:10806") as client:
    # Call Ozon/WB search APIs directly
    response = await client.get("https://www.ozon.ru/api/composer-api.bx/page/json/v2", params={
        "url": f"/search/?text={query}&sort=price"
    })
```

### Browser Configuration for Geo-Restricted Regions

```python
config = BrowserConfig(
    headless=False,           # Visible browser for debugging
    proxy="socks5://127.0.0.1:10806",  # v2rayN proxy
    ghost_surfer=False,       # Ghost-surfer may also have CDN issues
    # Use system Edge via channel
    # channel="msedge",        # Uncomment if Edge installed
)
```

### Verified Working Setup (Russia)
- **v2rayN proxy**: ✅ Working (socks5://127.0.0.1:10806)
- **Edge Dev**: ✅ Found at `D:\Program Files (x86)\Microsoft\Edge Dev\Application\msedge.exe`
- **Playwright + Edge channel**: ✅ Works without CDN download
- **v2rayN proxy**: ✅ Working for HTTP fallback

## Logging

```python
# All actions logged to JSONL
{"timestamp": "2026-07-31T10:00:00", "action": "click", "selector": "...", "success": true, "duration_ms": 150}
```

## Verification

```bash
# Verify skill
python scripts/subagent_verifier.py .claude/skills/web-automation/SKILL.md --strict

# Compliance check
python scripts/compliance_checker.py --check
```

## Core Mental Models

1. **Selector-first** — All interactions via config, never hardcoded
2. **Config-driven** — New sites = new JSON, no code changes
3. **Auth isolation** — Per-site cookie storage, no cross-contamination
4. **Graceful degradation** — Ghost-surfer → Playwright stealth → basic Playwright
5. **Observability** — Every action logged, retryable, auditable

## Key Frameworks & Decision Rules

| Framework | Purpose | When to Apply |
|-----------|---------|---------------|
| **Selector-first** | All interactions via config, never hardcoded | Every interaction |
| **Config-driven** | New sites = new JSON, no code changes | New site / action |
| **Auth isolation** | Per-site cookie storage, no cross-contamination | Every site |
| **Graceful degradation** | Ghost-surfer → Playwright stealth → basic Playwright | Browser init |
| **Observability** | Every action logged, retryable, auditable | Every action |

## Topic Index

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Core Engine](#core-engine-web_automationpy)
- [Config Loader](#config-loader)
- [Site Configs](#site-configs)
- [Supported Sites](#supported-sites)
- [Ghost-surfer Integration](#ghost-surfer-integration)
- [Anti-Detect Features](#anti-detect-features)
- [Logging](#logging)
- [Verification](#verification)
- [Core Mental Models](#core-mental-models)
- [Key Frameworks & Decision Rules](#key-frameworks--decision-rules)

## Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Hardcode selectors | Use config JSON |
| Share cookies across sites | Per-site storage |
| Ignore proxy failures | Retry with fallback |
| Skip wait states | Wait for selectors |
| Single browser instance | Context per task |

---

## References

- [Site Structure Principles](references/site_structure.md)
- [Marketplace Scraping Limitations — Ozon & Wildberries](references/marketplace-limitations.md)
- [Browser Launch Workaround for Geo-Restricted Regions](references/browser-launch-workaround.md)

---

**Version**: 1.1  
**Created**: 2026-07-31  
**Updated**: 2026-08-01  
**Author**: Hermes Agent