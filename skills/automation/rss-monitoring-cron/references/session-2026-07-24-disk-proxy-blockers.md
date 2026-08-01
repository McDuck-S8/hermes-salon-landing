# Session 2026-07-24: Disk Space + Proxy Blockers — System Python Only Path

## Trigger
Cron job execution failed with `ModuleNotFoundError: No module named 'feedparser'`. Manual runs also failed.

## Root Causes (Compound)
1. **C: drive 100% full** — uv cache at `C:\Users\Asus\AppData\Local\uv\cache\` = 319GB/319GB. Prevents:
   - `uv venv` creation (needs cache write)
   - `uv pip install` (needs cache write)
   - Any Python package installation via uv

2. **Proxy SSL handshake timeouts** — All pip install attempts (system Python, project venv, new venv) failed with:
   ```
   ProxyError('Cannot connect to proxy.', TimeoutError('_ssl.c:1011: The handshake operation timed out'))
   ```
   Network proxy configuration blocks PyPI access entirely.

3. **No dedicated RSS monitoring cron job** — `jobs.json` contains `knowledge-pipeline-rss-yt-kc` (every 2h) but no standalone `rss-monitor` job. The pipeline runs `knowledge_pipeline.py` which calls `rss_monitor.py` internally.

4. **Only System Python 3.11 works** — Has `feedparser`, `requests`, `beautifulsoup4`, `python-dateutil`, `lxml` pre-installed. All venv paths fail due to (1) and (2).

## Working Configuration (Validated 2026-07-24)

| Python Path | Has feedparser? | Works? | Notes |
|-------------|-----------------|--------|-------|
| `D:/Program Files/Python311/python.exe` | ✅ Yes | ✅ **Only working option** | System Python - use for ALL cron jobs |
| `D:/Portable_Soft/hermes/.venv/Scripts/python.exe` | ❌ No | ❌ Disk full + proxy | Project venv |
| `D:/Portable_Soft/hermes/hermes-agent/.venv/Scripts/python.exe` | ❌ No | ❌ Disk full + proxy | Hermes agent venv (wrong profile) |
| New venv (`uv venv`) | N/A | ❌ Disk full | Cannot create |

## Cron Job Fix Required
Update both cron jobs to use system Python explicitly:

```json
// knowledge-pipeline-rss-yt-kc (fbf81e5c8be1) - every 2h
{
  "script": "D:/Program Files/Python311/python.exe scripts/knowledge_pipeline.py"
}

// rss-monitor (if re-enabled) - every 4h
{
  "script": "D:/Program Files/Python311/python.exe scripts/rss_monitor.py"
}
```

## Previous Cache Still Available
- `cache/rss_monitor/latest.json` — Last successful RSS run (2026-07-23 partial)
- `rss_digest_latest.json` — Root-level AI/tech digest (VentureBeat, MIT, OpenAI, Google)

## Mitigation for Future Runs
1. **Free C: drive space:** `uv cache clean` or delete `C:\Users\Asus\AppData\Local\uv\cache\` (requires admin/uv not running)
2. **Fix proxy:** Configure proxy bypass for PyPI or use `--no-proxy` env var
3. **Pin system Python:** All cron `script` fields must use `D:/Program Files/Python311/python.exe` until (1) and (2) resolved
4. **Consider removing Reddit feeds:** 13/14 consistently return 429; only adds latency

## Script Analysis (rss_monitor.py)
- Well-structured, 378 lines
- 16 feeds configured (Partnerkin scrape + AffiliateFix RSS + 14 Reddit feeds)
- Keyword filtering for CPA terms (беттинг, гембл, слот, казино, кейс, нутра, лендинг, SEO, трафик, офер, CPA, ROI)
- 7-day recency filter (MAX_AGE_DAYS = 7)
- Cache at `cache/rss_monitor/latest.json`
- Partnerkin special handling (homepage scrape since RSS is dead)
- Digest output with notable article filtering

## Reddit Feed Status (Reconfirmed)
All 13 non-affiliatemarketing Reddit feeds return 429. Only r/affiliatemarketing works intermittently. Public RSS endpoints are aggressively rate-limited globally.

## File Locations
- Script: `/d/Portable_Soft/hermes/scripts/rss_monitor.py`
- Cache dir: `/d/Portable_Soft/hermes/cache/rss_monitor/`
- Cron jobs: `/d/Portable_Soft/hermes/cron/jobs.json`
- Last digest: `/d/Portable_Soft/hermes/rss_digest_latest.json`