---
name: cpa-browser-scraper
description: >
  Browser automation scraper for CPA/arbitrage intelligence. Uses browser-harness
  (CDP) to scrape live data from CPA networks, affiliate forums, competitor landers,
  Google Maps local businesses, and ad libraries. Works with YOUR logged-in Chrome.
license: Apache-2.0
metadata:
  author: "Hermes Agent"
  version: "1.0.0"
  source: "Built on browser-use/browser-harness"
  requires_browser_harness: true
  requires_cdp: true
---

# CPA Browser Scraper

**Підключається до ТВОЄГО Chrome через CDP (порт 9222)** — бачить усі твої вкладки, логіни, кукі.
Не потрібно логінитися заново — ти вже залогінений в AdCombo, CPAlead, Telegram Web, Notion.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  browser-harness (CDP daemon)                               │
│  ├── Connects to YOUR Chrome via --remote-debugging-port=9222│
│  ├── Uses DevToolsActivePort for Chrome 147+ compatibility  │
│  └── Exposes helpers: goto_url, js, capture_screenshot, wait_for_load, page_info│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  cpa-browser-scraper (this skill)                           │
│  ├── Scraper modules (one per target)                       │
│  ├── Data models (Offer, Creative, Competitor, LocalBiz)    │
│  ├── Output: JSON → Knowledge Cube → Finance Core           │
│  └── Cron integration: daily/weekly scans                   │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# 1. Ensure Chrome is running with CDP:
#    chrome.exe --remote-debugging-port=9222 --user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data"

# 2. Start browser-harness daemon:
cd /d/Portable_Soft/hermes/browser-harness
python -m src.browser_harness.daemon

# 3. Test connection:
browser-harness <<<'print(page_info())'

# 4. Run scraper:
python -m skills.automation.cpa_browser_scraper scan_offers --network adcombo --geo IN
```

## Scraper Modules

### 1. CPA Network Offer Scanner
```python
from skills.automation.cpa_browser_scraper import CPAOfferScanner

scanner = CPAOfferScanner()
offers = scanner.scan_network(
    network="adcombo",      # adcombo, cpalead, alfaleads, cpatrend
    geo="IN",               # IN, BR, US, DE, etc.
    verticals=["gambling", "dating", "pwa_install", "nutra"],
    min_payout=3.0,
    min_cap=1000
)
# Returns: List[Offer] with payout, flow, cap, geo, lander_url, restrictions
```

### 2. Creative Intelligence (FB Library + TikTok CC)
```python
from skills.automation.cpa_browser_scraper import CreativeScanner

scanner = CreativeScanner()
creatives = scanner.scan_fb_library(
    query="cricket betting India",
    country="IN",
    ad_type="all",
    max_results=50
)
creatives = scanner.scan_tiktok_cc(
    region="IN",
    category="gaming",
    max_results=30
)
# Returns: List[Creative] with hook, format, CTA, lander_pattern, impressions_est
```

### 3. Competitor Landing Analyzer
```python
from skills.automation.cpa_browser_scraper import CompetitorAnalyzer

analyzer = CompetitorAnalyzer()
report = analyzer.analyze_lander("https://competitor-lander.com/preland")
# Returns: hook, structure, tech_stack, cta_patterns, estimated_spend_signals
```

### 4. Google Maps Local Business Scanner
```python
from skills.automation.cpa_browser_scraper import LocalBizScanner

scanner = LocalBizScanner()
bizs = scanner.scan_maps_scanner.scan_area(
    query="салон красоты позняки киев",
    max_results=50
)
# Returns: List[LocalBiz] with name, phone, address, website, rating, photos, website_tech
```

## Data Models

```python
@dataclass
class Offer:
    offer_id: str
    network: str
    name: str
    vertical: str
    geo: str
    payout: float
    flow: str           # "CPI", "CPL", "CPS", "SOI", "DOI"
    cap_daily: int
    lander_url: str
    restrictions: list  # ["no_incent", "adult_only", "prelander_required"]
    approval_difficulty: int  # 1-10
    source_url: str
    scraped_at: datetime

@dataclass
class Creative:
    creative_id: str
    platform: str       # "fb_library", "tiktok_cc"
    hook: str
    format: str         # "video", "image", "carousel"
    cta: str
    lander_pattern: str
    impressions_est: int
    targeting_hints: list
    source_url: str
    scraped_at: datetime

@dataclass
class CompetitorReport:
    url: str
    hook: str
    structure: dict     # {"prelander": True, "lander_type": "quiz", "steps": 3}
    tech_stack: list    # ["keitaro", "wp", "elementor"]
    cta_patterns: list
    spend_signals: dict # {"fb_pixel": True, "ga": "G-XXXX", "tt_pixel": True}
    scraped_at: datetime

@dataclass
class LocalBiz:
    name: str
    phone: str
    address: str
    website: str | None
    rating: float
    review_count: int
    photos: list[str]
    categories: list[str]
    website_tech: list[str] | None
    scraped_at: datetime
```

## Integration Points

| System | How |
|---|---|
| **Knowledge Cube** | `on_task_complete()` after each scan |
| **Finance Core** | Offer payouts → budget allocation |
| **Always-On Agent** | Cron jobs: daily offer scan, weekly creative scan |
| **Multi-Agent Researcher** | Sub-tasks for parallel network scanning |

## Cron Jobs (Deployed)

```bash
# Daily 07:00 - Scan top 5 networks for fresh offers
hermes cron create --schedule "0 7 * * *" \
  --prompt "Scan AdCombo, CPAlead, Alfaleads, CPATrend for IN/Geo IN/Geo BR/Geo DE gambling/dating/pwa offers. Min payout $3, min cap $1k/day. Output JSON to KC." \
  --skills "cpa-browser-scraper,finance-core" \
  --name "daily-offer-scan"

# Weekly Mon 09:00 - Creative intelligence
hermes cron create --schedule "0 9 * * 1" \
  --prompt "Scan FB Library + TikTok CC for top 20 creatives in IN cricket betting, BR dating, DE nutra. Analyze hooks, lander patterns, CTA. Output to KC." \
  --skills "cpa-browser-scraper" \
  --name "weekly-creative-scan"

# Daily 18:00 - Local biz scan for landing page clients
hermes cron create --schedule "0 18 * * *" \
  --prompt "Scan Google Maps for 'салон красоты Позняки', 'стоматология Позняки', 'фитнес Позняки' in Kiev. Extract businesses without websites or with bad sites. Output leads for landing page sales." \
  --skills "cpa-browser-scraper" \
  --name "daily-local-biz-scan"
```

## Helper Functions (in agent_helpers.py)

```python
# Add to browser-harness/agent-workspace/agent_helpers.py

def scan_adcombo_offers(geo="IN", vertical="gambling"):
    """Navigate to AdCombo offers page, filter by geo/vertical, extract offer cards."""
    goto_url(f"https://www.adcombo.com/offers?geo={geo}&vertical={vertical}")
    wait_for_load()
    # ... extract via js()
    return offers

def scan_fb_library(query, country="IN", max_results=50):
    """Search FB Ad Library, scroll, extract creative cards."""
    goto_url(f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={query}")
    wait_for_load()
    # ... scroll and extract
    return creatives

def scan_google_maps(query, max_results=50):
    """Search Google Maps, extract business cards."""
    goto_url(f"https://www.google.com/maps/search/{query}")
    wait_for_load()
    # ... scroll and extract
    return businesses
```

## Files

```
cpa-browser-scraper/
├── SKILL.md
├── cpa_scraper/
│   ├── __init__.py
│   ├── models.py          # Offer, Creative, CompetitorReport, LocalBiz
│   ├── networks/
│   │   ├── adcombo.py
│   │   ├── cpalead.py
│   │   ├── alfaleads.py
│   │   └── cpatrend.py
│   ├── creative_scanner.py
│   ├── competitor_analyzer.py
│   ├── maps_scanner.py
│   └── main.py            # CLI entry point
├── agent_helpers.py       # Add to browser-harness/agent-workspace/
└── tests/
    └── test_scrapers.py
```