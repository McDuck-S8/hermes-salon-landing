# SSL Timeout Pattern — RSS Monitor (2026-07-23)

## Problem
RSS monitor script (`scripts/rss_monitor.py`) times out on SSL-heavy feeds:
- Reddit RSS feeds (r/affiliatemarketing, r/passive_income, etc.)
- AffiliateFix RSS
- Partnerkin homepage scrape (HTTPS)

**Error:** `SSLEOFError: [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol`

**Root cause:** Slow SSL handshakes + connection drops mid-stream on some endpoints. Single `REQUEST_TIMEOUT=30` applies to entire request; no per-feed timeout, no retry logic.

---

## Environment Facts (2026-07-23)

| Item | Value |
|------|-------|
| Hermes root | `D:/Portable_Soft/hermes` |
| **Working venv** | `D:/Portable_Soft/hermes/.venv/Scripts/python.exe` |
| Broken venv (old) | `D:/Portable_Soft/hermes/hermes-agent/.venv` |
| System Python (has feedparser) | `D:/Program Files/Python311/python.exe` |
| RSS monitor script | `scripts/rss_monitor.py` |
| Cache file | `cache/rss_monitor/latest.json` |
| Tech digest cache | `rss_digest_latest.json` |

---

## Dependency Installation (Correct Venv)

```bash
cd D:/Portable_Soft/hermes
uv pip install feedparser requests beautifulsoup4 python-dateutil lxml
# Installs in .venv (project venv, NOT hermes-agent/.venv)
```

**Verification:**
```bash
.venv/Scripts/python.exe -c "import feedparser; print('ok')"
```

---

## Manual Run That Worked (Partial)

```bash
cd D:/Portable_Soft/hermes
.venv/Scripts/python.exe scripts/rss_monitor.py
```

**Output:**
- Partnerkin: SSL error → 0 entries
- AffiliateFix: SSL error → 0 entries
- Reddit feeds: timeout after 60s (script timeout, not request timeout)
- Cache files: contain last successful run (2026-07-19)

---

## Recommended Script Fixes (For Next Cron Update)

### 1. Per-Feed Timeout
```python
# Current: single REQUEST_TIMEOUT = 30 for all
# Fix: per-feed timeout dict
FEED_TIMEOUTS = {
    "partnerkin": 20,      # homepage scrape
    "affiliatefix": 15,    # RSS
    "reddit_*": 10,        # Reddit RSS — aggressive timeout
    "default": 30,
}
```

### 2. Retry with Backoff for SSL Errors
```python
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def make_session():
    session = requests.Session()
    retry = Retry(
        total=2,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session
```

### 3. Continue on Feed Failure (Graceful Degradation)
```python
def fetch_all_feeds() -> dict[str, list]:
    results = {}
    for feed in FEEDS:
        try:
            entries = fetch_feed(feed)
            results[feed["id"]] = entries
        except Exception as e:
            log(f"Feed {feed['id']} failed: {e}", "WARN")
            results[feed["id"]] = []  # Empty list, not crash
    return results
```

### 4. Add Max Runtime Guard
```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Max runtime exceeded")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(120)  # 2 min hard limit for entire script
```

---

## Cron Job Configuration Fix

**Current (broken path prefix):**
```json
{ "script": "scripts/rss_monitor.py" }
```

**Fixed (no scripts/ prefix — runner prepends it):**
```json
{ "script": "rss_monitor.py" }
```

**Python path (use project venv):**
```json
{ "script": ".venv/Scripts/python.exe scripts/rss_monitor.py" }
```

---

## Cache as Fallback

When live fetch fails, cached data at `cache/rss_monitor/latest.json` (updated 2026-07-19) contains:
- 10 Partnerkin articles (scraped homepage)
- 10 AffiliateFix threads
- 10 Reddit r/affiliatemarketing posts
- 10 Reddit r/passive_income posts
- Plus crypto, entrepreneur, PPC, adtech, growthhacking, digital_marketing, SEO, sportsbetting, beermoney, workonline, juststart, sidehustle

**Digest generator should read cache when live fetch returns empty.**

---
## Related

- `devops/cron-maintenance` skill — cron path prefix fix, dead job detection
- `automation/rss-monitoring-cron` skill — main skill for this cron job
- `cache/rss_monitor/latest.json` — last successful run data
- `references/pipeline-python-env-fix-2026-07-23.md` — Pipeline Python environment fix (knowledge_pipeline.py uses wrong venv)