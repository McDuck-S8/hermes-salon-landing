# Pipeline Python Environment Fix (2026-07-23)

## Problem

The `knowledge_pipeline.py` cron job (`fbf81e5c8be1` — `knowledge-pipeline-rss-yt-kc`, every 2h) was failing on the RSS Monitor step with a 180s timeout.

**Root cause:** The pipeline script uses the project venv Python (`.venv/Scripts/python.exe`) which lacks `feedparser` and other dependencies. The RSS monitor step would hang/timeout because imports failed silently in the subprocess context.

```python
# knowledge_pipeline.py line 14 - PROBLEMATIC:
PYTHON = str(HERMES / ".venv" / "Scripts" / "python.exe")
```

## Working Python Executables (2026-07-23)

| Python Path | Has feedparser? | Notes |
|-------------|-----------------|-------|
| `D:/Program Files/Python311/python.exe` | ✅ Yes | System Python — **RECOMMENDED for cron** |
| `D:/Portable_Soft/hermes/.venv/Scripts/python.exe` | ❌ No (until deps installed) | Project venv |
| `D:/Portable_Soft/hermes/hermes-agent/.venv/Scripts/python.exe` | ❌ No | Hermes agent venv (wrong profile) |

## Fix Options

### Option 1: Use System Python in Cron Job (RECOMMENDED)

Update cron job `fbf81e5c8be1` `script` field:
```json
{
  "script": "D:/Program Files/Python311/python.exe scripts/knowledge_pipeline.py"
}
```

### Option 2: Install Dependencies in Project Venv

```bash
cd D:/Portable_Soft/hermes
uv pip install feedparser requests beautifulsoup4 python-dateutil lxml
# yt-dlp is separate binary, install via: uv pip install yt-dlp
```

Then verify:
```bash
.venv/Scripts/python.exe -c "import feedparser; print('ok')"
```

### Option 3: Fix knowledge_pipeline.py to Use System Python

Change line 14 in `knowledge_pipeline.py`:
```python
# FROM:
PYTHON = str(HERMES / ".venv" / "Scripts" / "python.exe")
# TO:
PYTHON = r"D:/Program Files/Python311/python.exe"
```

## Verification (2026-07-23 Manual Run with System Python)

```bash
cd D:/Portable_Soft/hermes
"D:/Program Files/Python311/python.exe" scripts/knowledge_pipeline.py
```

**Output:**
```
=== PIPELINE START 2026-07-23T11:38:52.978128 ===
==================================================
[11:38:52] Running: RSS Monitor
==================================================
  [INFO] 11:38:52 — === RSS Monitor starting ===
  [INFO] 11:38:52 — Fetching partnerkin (cpa-news)…
  [INFO] 11:38:55 — Partnerkin: found 31 article links
  [INFO] 11:39:23 —   OK: 15 entries, 15 recent (last 7 days)
  [INFO] 11:39:23 — Fetching affiliatefix (cpa-news)…
  [INFO] 11:39:24 —   OK: 20 entries, 20 recent (last 7 days)
  [INFO] 11:39:24 — Fetching reddit_affiliatemarketing (cpa-news)…
  [INFO] 11:39:25 —   OK: 25 entries, 12 recent (last 7 days)
  [INFO] 11:39:25 — Fetching reddit_passive_income (cpa-news)…
  [ERROR] 11:39:26 — RSS fetch failed for https://www.reddit.com/r/passive_income/.rss: 429 Client Error: Too Many Requests
  [INFO] 11:39:26 —   OK: 0 entries, 0 recent (last 7 days)
  ... (all other Reddit feeds: 429 rate limited)
  [rss_monitor] Notable articles (30):
  ...
  [INFO] 11:39:26 — === RSS Monitor done in 37.9s ===
==================================================
[11:39:26] Running: YouTube Watch
==================================================
  [youtube_watch] Checking easy_traff...
    OK: 5 videos
  [youtube_watch] Checking partnerkin...
    OK: 5 videos
  [youtube_watch] Checking icpsquad...
    OK: 5 videos
  [youtube_watch] Checking traffic_hunter...
    ERROR: ERROR: [youtube:tab] @TrafficHunter: This channel does not have a videos tab
  [youtube_watch] Checking webvork...
    ERROR: ERROR: [youtube:tab] @webvork: This channel does not have a videos tab

  Done: 3/5 channels OK, 2 errors, 15 total videos
==================================================
[11:40:26] Running: Knowledge Filter
==================================================
    ❌ REJECTED at stage 1 (HS:50 AA:0 SP:0)
    🔍 Filtering: Is there a demand for open source affiliate software?... (reddit_affiliatemarketing)
    ❌ REJECTED at stage 1 (HS:50 AA:0 SP:0)
    🔍 Filtering: It's Only Me Or Everyone Finding Drop In ConVersion Rate Wit... (reddit_affiliatemarketing)
    ❌ REJECTED at stage 1 (HS:50 AA:0 SP:0)
    === SUMMARY ===
    Total: 30 | Passed: 9 | Rejected: 21
==================================================
PIPELINE DONE: RSS=OK YT=OK Filter=OK
==================================================
```

**Key metrics:**
- RSS Monitor: ~38s (was timing out at 180s with broken venv)
- YouTube Watch: ~30s (3/5 channels working)
- Knowledge Filter: 30 items → 9 passed → written to KC
- Total pipeline: ~2 minutes

## Cron Job Configuration

**Job ID:** `fbf81e5c8be1`  
**Name:** `knowledge-pipeline-rss-yt-kc`  
**Schedule:** Every 2 hours  
**Current script field (BROKEN):** `knowledge_pipeline.py` (uses project venv Python)  
**Fixed script field:** `D:/Program Files/Python311/python.exe scripts/knowledge_pipeline.py`

## Related Files

- `scripts/knowledge_pipeline.py` — Main pipeline script (line 14 needs fix)
- `scripts/rss_monitor.py` — RSS monitor (requires feedparser)
- `scripts/youtube_watch.py` — YouTube monitor (uses yt-dlp binary, Python env irrelevant)
- `skills/automation/knowledge-filter/scripts/filter.py` — Knowledge filter
- `cache/rss_monitor/latest.json` — RSS cache
- `cache/youtube_watch/latest.json` — YouTube cache