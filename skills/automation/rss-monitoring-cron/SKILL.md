---
name: rss-monitoring-cron
description: "RSS/Atom feed monitoring cron job — fetches CPA, AI, and tech feeds, caches results, delivers digest. Includes cron path fix pattern."
tags: [cron, rss, monitoring, digest, automation]
platforms: [linux, macos, windows]
---

# RSS Monitoring Cron Job

## When to use
When setting up or fixing scheduled RSS feed monitoring that runs as a cron job and delivers a digest of notable articles from CPA/affiliate, AI, and tech feeds.

## The Cron Path Bug (Critical Fix)

**Symptom:** Cron job fails with `Script not found: D:\\Portable_Soft\\hermes\\scripts\\scripts\\rss_monitor.py` (double `scripts/` in path)

**Root Cause:** The cron runner (`hermes cron run` or scheduler) executes from the Hermes root directory (`D:/Portable_Soft/hermes`), but some job definitions or path resolvers prepend `scripts/` again, creating `scripts/scripts/rss_monitor.py`.

**Fix Applied in jobs.json:**
```json
{
  "script": "scripts/rss_monitor.py"
}
```
NOT `scripts/scripts/rss_monitor.py`. The runner already prefixes `scripts/`.

**Verification:** After fix, run manually:
```bash
cd D:/Portable_Soft/hermes
python scripts/rss_monitor.py
```
Should output: `[rss_monitor] Fetching partnerkin... OK: 10 entries` etc.

---

## Dependency & Environment Pitfall (2026-07-18) — RESOLVED

**Symptom:** `ModuleNotFoundError: No module named 'feedparser'` when cron runs the script.

**Root Cause:** The Hermes venv (`D:/Portable_Soft/hermes/hermes-agent/.venv`) was missing `feedparser`, but system Python (`D:/Program Files/Python311/`) had it pre-installed.

**Fix Applied:** Run with system Python explicitly. Updated cron job `script` field to use full path:
```json
{
  "script": "D:/Program Files/Python311/python.exe scripts/rss_monitor.py"
}
```

**Verification:** Manual run succeeded:
```bash
cd D:/Portable_Soft/hermes
"D:/Program Files/Python311/python.exe" scripts/rss_monitor.py
# Output: 5 feeds processed, 55 entries, 37 notable, ~57s
```

**Prevention:** When cron jobs fail with import errors, check which Python the cron runner uses vs. where dependencies are installed. The cron scheduler runs from the gateway process context. Explicit Python path in `script` field avoids venv mismatch.

---

## Session 2026-07-23: SSL Timeout Issues & Correct Venv Path

**New Symptom (2026-07-23):** Script runs but times out on SSL-heavy feeds (Reddit RSS, AffiliateFix, Partnerkin scrape) with `SSLEOFError` / `UNEXPECTED_EOF_WHILE_READING`. Default `REQUEST_TIMEOUT=30` insufficient for slow/flaky HTTPS endpoints.

**Root Cause:** Some feeds (especially Reddit RSS, some CPA forums) have slow SSL handshakes or drop connections mid-stream. The script processes feeds sequentially with a single 30s timeout for the entire request.

**Mitigations Applied:**
1. **Correct Python executable for this environment:** The working venv is at `D:/Portable_Soft/hermes/.venv/Scripts/python.exe` (NOT `hermes-agent/.venv`). Use this path for cron jobs in this profile.
2. **Dependencies installed in correct venv:** `uv pip install feedparser requests beautifulsoup4 python-dateutil lxml` in the project venv.
3. **Per-feed timeout handling needed:** The script should set per-feed timeouts and skip failing feeds gracefully rather than timing out the entire run.

**Working Manual Run (2026-07-23):**
```bash
cd D:/Portable_Soft/hermes
.venv/Scripts/python.exe scripts/rss_monitor.py
# Partially succeeded — Partnerkin, AffiliateFix failed SSL; Reddit feeds timed out; cached data available
```

**Cache Locations (verified):**
- RSS Monitor cache: `cache/rss_monitor/latest.json` (timestamp + entries per feed)
- YouTube/Tech digest cache: `rss_digest_latest.json` (AI/tech feeds from VentureBeat, MIT Tech Review, OpenAI, Google)

**Recommended Script Improvements (for next cron update):**
- Add per-feed timeout (e.g., 15s per feed, not 30s total)
- Add retry logic with exponential backoff for SSL errors
- Continue on feed failure — log error, skip to next feed
- Add `--max-runtime` flag to bound total execution time

## Feed Configuration

### Current Feed List (updated 2026-07-19)

Defined in `scripts/rss_monitor.py` — `FEEDS` list:

| Feed ID | URL | Topic | Status |
|---------|-----|-------|--------|
| `partnerkin` | https://partnerkin.com/rss | cpa-news | ✅ Homepage scrape |
| `affiliatefix` | https://www.affiliatefix.com/forums/-/index.rss | cpa-news | ✅ RSS 2.0 |
| `reddit_affiliatemarketing` | r/affiliatemarketing | cpa-news | ✅ |
| `reddit_passive_income` | r/passive_income | cpa-news | ⚠️ rate limited |
| `reddit_crypto` | r/CryptoCurrency | crypto | ✅ |
| `reddit_entrepreneur` | r/Entrepreneur | business | ⚠️ rate limited |
| `reddit_ppc` | r/PPC | cpa-news | ⚠️ rate limited |
| `reddit_adtech` | r/adtech | cpa-news | ⚠️ rate limited |
| `reddit_growthhacking` | r/growthhacking | cpa-news | ✅ |
| `reddit_digital_marketing` | r/digital_marketing | cpa-news | ⚠️ rate limited |
| `reddit_seo` | r/SEO | cpa-news | ⚠️ rate limited |
| `reddit_sportsbetting` | r/sportsbetting | gambling | ✅ NEW |
| `reddit_beermoney` | r/beermoney | side-income | ✅ NEW |
| `reddit_workonline` | r/workonline | side-income | ✅ NEW |
| `reddit_juststart` | r/juststart | affiliate-seo | ✅ NEW |
| `reddit_sidehustle` | r/sidehustle | side-income | ✅ NEW |

### Removed Feeds (2026-07-19 — garbage for CPA context)
- `openai_blog` — AI research, not CPA-relevant
- `anthropic_rsshub` — AI research, proxy-dependent
- `hackernews` — tech news, not CPA-relevant

## Output

- Cache: `cache/rss_monitor/latest.json` (timestamp + entries per feed)
- Each entry: `title`, `url`, `published`, `summary` (500 chars)
- YouTube cache: `cache/youtube_watch/latest.json` (timestamp + channels with videos)
- YouTube entries now include `description` (2000 chars) and `tags`
- Pipeline script: `scripts/knowledge_pipeline.py` (runs RSS→YT→Filter→KC)
- Pipeline cron: `fbf81e5c8be1` every 2h

## Partnerkin Special Handling

RSS feed returns 404/empty. Script scrapes homepage:
1. Fetches `https://partnerkin.com`
2. Extracts article links from `/blog/`, `/tribuna/`, `/stati/`, `/kejsy/`, `/intervyu/`
3. Falls back to `alt` text of images containing keywords
4. Fetches each article page for date + first paragraph description
5. Keyword mapping: беттинг/гембл/слот/казино → gambling, кейс → case, нутра/лендинг → nutra, SEO terms → seo, etc.

## Session 2026-07-18 Run Summary (this cron execution — 15:33 UTC)

**Original `rss_monitor.py` executed successfully** with system Python (`D:/Program Files/Python311/python.exe`).

- **Feeds processed:** 9 (Partnerkin, AffiliateFix, Reddit×4, OpenAI, Anthropic RSSHub, HN)
- **Total entries fetched:** 57 (10 + 7 + 10 + 0 + 10 + 0 + 8 + 2 + 10)
- **Notable articles:** 57 (all entries by topic: CPA/AI/Crypto/Tech)
- **Duration:** ~57s
- **Cache updated:** `cache/rss_monitor/latest.json`
- **Digest delivered:** Local output (57 notable articles printed)

**Key insight:** The Hermes venv lacks `feedparser` but system Python has it. Cron job should either:
1. Use system Python explicitly: `script: "D:/Program Files/Python311/python.exe scripts/rss_monitor.py"`
2. Or `pip install feedparser requests beautifulsoup4 python-dateutil lxml` in the venv

**New signals from this run:**
- Reddit feeds work but hit aggressive rate limits (429 on r/passive_income, 0 entries on r/Entrepreneur)
- Partnerkin homepage scrape fails on SSL handshake (EOF) — needs timeout/retry
- AffiliateFix forum RSS times out at 30s — needs longer timeout
- OpenAI Blog feed returns 1039 entries — client-side 7-day filter is critical

## Notable Article Patterns (from 2026-07-15 run)

**CPA / Affiliate (AffiliateFix):**
- LATAM geo diversification (Colombia, Peru, Chile vs Brazil/Mexico)
- Email marketing: value-first, clean opt-in lists, segmentation
- Casino CPA offers — direct affiliate manager contacts (Telegram)
- Multi-account management: separate ad accounts per vertical, dedicated test accounts
- IP ban reduction: proxy rotation strategies that actually work
- AI content vs revenue debate
- Crypto automation demand

**AI (OpenAI Blog):**
- Agentic era investment management: useful work per dollar
- ChatGPT Work for data science (root-cause briefs, KPI memos, dashboards)
- ChatGPT Work for sales (pipeline briefs, forecast reviews, stalled-deal diagnosis)
- Deutsche Telekom AI-native transformation
- GPT-5.6 in Microsoft 365 Copilot
- GPT-5.6: more intelligence/token, better $/performance
- ChatGPT Work as autonomous agent across apps/files

**AI (Anthropic):**
- Claude for Teachers: free premium for US K-12 educators + curricula mapped to 50 state standards
- $10M to Canadian AI research (Toronto, Montreal, Alberta — historic neural net/RL hubs)
- Physical AI: UST partnership for fab stress-testing, assembly-line fault detection
- Alberta government: 466M lines scanned in 20hrs with Claude Code, vulns fixed
- Claude Sonnet 5: most agentic Sonnet yet (plans, browser, terminal, autonomous)
- Fable 5 redeployed after US export controls lifted

**Tech (Hacker News):**
- Grepathy: Claude made unauthorized decision (pre-created Clerk users), transcripts auto-deleted → solution: distill transcripts to markdown decisions committed with code
- Telegram data center deep dive
- AI voice fraud: 3-second cloning defeats all defenses
- Windows GDID: persistent device ID documented in FBI case (cannot disable)
- SpaceX bonds down 10% → approaching junk status

## Cron Job Definition

### Active: knowledge-pipeline-rss-yt-kc (2026-07-19)

```json
{
  "job_id": "fbf81e5c8be1",
  "name": "knowledge-pipeline-rss-yt-kc",
  "script": "knowledge_pipeline.py",
  "schedule": "every 2h",
  "deliver": "local"
}
```

### Legacy: rss-monitor (pre-pipeline)

```json
{
  "id": "fb297032a852",
  "name": "rss-monitor",
  "script": "scripts/rss_monitor.py",
  "schedule": { "kind": "interval", "minutes": 240 },
  "deliver": "local"
}
```

---

## Reference Files

- `references/feed-sources-2026-07-18.md` — Working/stale feed inventory, new script (`fetch_rss.py`), notable articles from this run
- `references/feed-sources-2026-07-18b.md` — Original `rss_monitor.py` feed list results (Partnerkin, AffiliateFix, OpenAI, Anthropic, HN) — 30 notable articles fetched
- `references/cache-format-notes.md` — Cache format migration details
- `references/monitoring-sources.md` — Additional monitoring source notes
- `references/ssl-timeout-pattern-2026-07-23.md` — SSL timeout pattern, per-feed timeout/retries fix plan, correct venv path, cache fallback strategy
- `references/pipeline-python-env-fix-2026-07-23.md` — Pipeline Python environment fix (knowledge_pipeline.py uses wrong venv)
- `references/profile-mismatch-2026-07-24.md` — **Critical: This skill's pipeline exists in a DIFFERENT Hermes profile. Current profile (AI OFM Tribute) lacks all scripts, cron jobs, and cache dirs documented here.**

### Knowledge Cube Ingestion Pipeline (Updated 2026-07-19, session 2026-07-23)

Unified pipeline: `scripts/knowledge_pipeline.py` runs every 2h via cron.

```
knowledge_pipeline.py (cron: every 2h)
  ├── rss_monitor.py → cache/rss_monitor/latest.json (15 feeds)
  ├── youtube_watch.py → cache/youtube_watch/latest.json (5 channels, with descriptions)
  └── filter.py --test-rss → kc_entries via kc_rag.upsert() (3-stage filter)
```

**Cron job:** `fbf81e5c8be1` — `knowledge-pipeline-rss-yt-kc`, every 2h, deliver=local.

**Key:** Filter writes to `kc_entries` (OKF-Lite table) via `kc_rag.upsert()`, NOT to `experiences`. Query `kc_entries` for external source counts.

**YouTube channels (5):** easy_traff, partnerkin, icpsquad, traffic_hunter, webvork. Descriptions fetched (no `--flat-playlist`).

**Result:** External KC: 155/445 = 34.8% (target 30% ✅).

---

### Pipeline Python Environment Fix (Session 2026-07-23)

**Problem:** `knowledge_pipeline.py` uses `.venv/Scripts/python.exe` (project venv) which lacks `feedparser`. The RSS Monitor step times out (180s) because imports fail silently in the venv context.

```python
# knowledge_pipeline.py line 14 - CURRENT (broken):
PYTHON = str(HERMES / ".venv" / "Scripts" / "python.exe")
```

**Working Python executables for this environment:**
| Python Path | Has feedparser? | Notes |
|-------------|-----------------|-------|
| `D:/Program Files/Python311/python.exe` | ✅ Yes | System Python - RECOMMENDED for cron |
| `D:/Portable_Soft/hermes/.venv/Scripts/python.exe` | ❌ No (until `uv pip install feedparser...`) | Project venv |
| `D:/Portable_Soft/hermes/hermes-agent/.venv/Scripts/python.exe` | ❌ No | Hermes agent venv (wrong profile) |

**Fix for cron job `fbf81e5c8be1`:** Update `script` field to use system Python explicitly:
```json
{
  "script": "D:/Program Files/Python311/python.exe scripts/knowledge_pipeline.py"
}
```

**Alternative:** Install deps in project venv:
```bash
cd D:/Portable_Soft/hermes
uv pip install feedparser requests beautifulsoup4 python-dateutil lxml
```

**Verification (2026-07-23 manual run with system Python):**
```bash
cd D:/Portable_Soft/hermes
"D:/Program Files/Python311/python.exe" scripts/knowledge_pipeline.py
# Result: RSS=OK (~38s), YT=OK, Filter=OK (9/30 passed)
```
### Reddit Feed Status

| Feed | Status | Notes |
|------|--------|-------|
| r/affiliatemarketing | ✅ Working | 13/13 entries (2026-07-23), high-signal CPA |
| r/passive_income | ❌ Rate limited | 429 errors (2026-07-18, 2026-07-23) |
| r/CryptoCurrency | ❌ Rate limited | 429 errors (2026-07-23) |
| r/Entrepreneur | ❌ Rate limited | 429 errors (2026-07-23) |
| r/PPC | ❌ Rate limited | 429 errors (2026-07-23) |
| r/adtech | ❌ Rate limited | 429 errors (2026-07-23) |
| r/growthhacking | ❌ Rate limited | 429 errors (2026-07-23) |
| r/digital_marketing | ❌ Rate limited | 429 errors (2026-07-23) |
| r/SEO | ❌ Rate limited | 429 errors (2026-07-23) |
| r/sportsbetting | ❌ Rate limited | 429 errors (2026-07-23) |
| r/beermoney | ❌ Rate limited | 429 errors (2026-07-23) |
| r/workonline | ❌ Rate limited | 429 errors (2026-07-23) |
| r/juststart | ❌ Rate limited | 429 errors (2026-07-23) |
| r/sidehustle | ❌ Rate limited | 429 errors (2026-07-23) |

**Confirmed pattern (2026-07-23):** All 13 Reddit feeds returned 429 Too Many Requests. Only r/affiliatemarketing works intermittently (possibly due to request ordering/delays). Reddit public RSS is aggressively rate-limited globally.

**Recommendation:** Reddit rate-limiting is aggressive and consistent. For production, use authenticated API (praw) or `reddit-rss-proxy`. Current RSS approach returns 0 entries for 13/14 feeds. Consider removing non-working feeds or adding 2-3s delays + custom User-Agent rotation.

---

## Session 2026-07-24: Disk Space + Proxy Blockers — System Python Only Path

**Trigger:** Cron job execution failed with `ModuleNotFoundError: No module named 'feedparser'`. Manual runs also failed.

**Root Causes (compound):**
1. **C: drive 100% full** — uv cache at `C:\\Users\\Asus\\AppData\\Local\\uv\\cache\\` = 319GB/319GB. Prevents:
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

**Working Configuration (validated 2026-07-24):**
| Python Path | Has feedparser? | Works? | Notes |
|-------------|-----------------|--------|-------|
| `D:/Program Files/Python311/python.exe` | ✅ Yes | ✅ **Only working option** | System Python - use for ALL cron jobs |
| `D:/Portable_Soft/hermes/.venv/Scripts/python.exe` | ❌ No | ❌ Disk full + proxy | Project venv |
| `D:/Portable_Soft/hermes/hermes-agent/.venv/Scripts/python.exe` | ❌ No | ❌ Disk full + proxy | Hermes agent venv (wrong profile) |
| New venv (`uv venv`) | N/A | ❌ Disk full | Cannot create |

**Cron Job Fix Required:**
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

**Previous Cache Still Available:**
- `cache/rss_monitor/latest.json` — Last successful RSS run (2026-07-23 partial)
- `rss_digest_latest.json` — Root-level AI/tech digest (VentureBeat, MIT, OpenAI, Google)

**Mitigation for Future Runs:**
1. **Free C: drive space:** `uv cache clean` or delete `C:\\Users\\Asus\\AppData\\Local\\uv\\cache\\` (requires admin/uv not running)
2. **Fix proxy:** Configure proxy bypass for PyPI or use `--no-proxy` env var
3. **Pin system Python:** All cron `script` fields must use `D:/Program Files/Python311/python.exe` until (1) and (2) resolved
4. **Consider removing Reddit feeds:** 13/14 consistently return 429; only adds latency

---

## Session 2026-07-26: Cron Model Drift + Web Search Fallback + SSL Timeout Confirmation

**Trigger:** Scheduled cron job failed with `ModuleNotFoundError: No module named 'feedparser'`. Upon investigation:
1. **Model drift in cron job** — The cron job definition specified `model: "nemotron-3-ultra-free"` with `provider: "opencode_zen"`, but the current Hermes profile uses `deepseek-v4-flash-free`. The job was blocked waiting for model resolution.
2. **SSL timeouts persist** — Reddit feeds (all 13), AffiliateFix, Partnerkin scrape all fail with `SSLEOFError: UNEXPECTED_EOF_WHILE_READING` or read timeouts (30s). System Python has `feedparser` but network layer fails.
3. **Cache still valuable** — `cache/rss_monitor/latest.json` from 2026-07-23 contained 57 entries across 5 working feeds (Partnerkin, AffiliateFix, Reddit-affiliatemarketing, CryptoCurrency, Entrepreneur). Used as primary data source.
4. **Web search supplementation** — When RSS feeds fail, `web_search_plus` with `provider: "auto"` and `mode: "research"` provided current AI/tech/CPA intelligence (Reuters AI, trycrush.ai, APMA, Affiverse, BuildFastWithAI, ZoneTechify).

**Key Learnings for Skill:**

### Pitfall: Cron Model Drift
Cron jobs that specify explicit `model`/`provider` fields become stale when the active profile changes models. The job executor waits for model resolution and fails silently or times out.

**Fix:** Remove explicit `model`/`provider` from cron jobs that run scripts (not LLM agents). Scripts don't need model assignment. Or use `model: null, provider: null` to inherit profile default.

### Pattern: Web Search Fallback When RSS Fails
When network-layer failures (SSL, proxy, rate limits) block RSS feeds, supplement with targeted web searches:
```python
# Example fallback queries for CPA/AI/tech digest
web_search_plus(
    query="CPA affiliate marketing arbitrage 2026 AI strategies",
    provider="auto",
    mode="research",
    count=5
)
web_search_plus(
    query="artificial intelligence news July 2026 site:reuters.com",
    provider="auto",
    mode="research", 
    count=5
)
```
This produces actionable intelligence even when primary feeds are down.

### Verified Working Configuration (2026-07-26)
| Python Path | Has feedparser? | Works? | Notes |
|-------------|-----------------|--------|-------|
| `D:/Program Files/Python311/python.exe` | ✅ Yes | ⚠️ Partial | System Python - imports OK, but SSL timeouts on feeds |
| `D:/Portable_Soft/hermes/.venv/Scripts/python.exe` | ✅ Yes (after `uv pip install`) | ❌ Disk full | Project venv - deps installed but disk full |

**Feed Status Summary (2026-07-26):**
| Feed | Status | Notes |
|------|--------|-------|
| Partnerkin (scrape) | ❌ SSL EOF | Homepage HTTPS handshake fails |
| AffiliateFix | ❌ SSL EOF | Forum RSS SSL handshake fails |
| Reddit (all 13 feeds) | ❌ SSL EOF / Timeout | Aggressive rate limiting + SSL issues |
| Reddit r/CryptoCurrency | ✅ 24 entries | **Only Reddit feed working** - got 25 entries, 24 recent |

**Recommended Script Improvements (Priority):**
1. **Per-feed timeout + continue-on-error** — Each feed gets 15s max; failure logs error and continues
2. **Retry with backoff for SSL EOF** — 2 retries with 5s/10s delay before skipping
3. **Remove non-working Reddit feeds** — 13/14 consistently fail; keep only r/CryptoCurrency if it works
4. **Add AI/tech feed sources** — Reuters AI, VentureBeat AI, The Verge AI, MIT Tech Review, Google AI Blog
5. **Web search fallback integration** — If <3 feeds succeed, trigger web search for missing topics

### Pitfalls

### Shared Cache File (`cache/cpa_offers.json`)
2. **Partnerkin SSL timeout** — Homepage scrape fails on SSL handshake; increase timeout or use alternative source
3. **RSSHub dependency** — Anthropic feed uses rsshub.bestblogs.dev proxy; if down, feed fails
4. **Summary truncation** — 500 char limit on summaries; full text not stored
5. **Timezone handling** — Published dates kept as-is from feeds; no normalization to UTC
6. **Cache format migration** — Old cache format wrapped entries in `{"entries": [...]}`, new format stores list directly. Script handles both via type check in `load_cache()`.
### Python environment mismatch (2026-07-18) — Cron runner uses hermes venv (`D:/Portable_Soft/hermes/hermes-agent/.venv/Scripts/python.exe`) which lacks `feedparser`, but system Python (`D:/Program Files/Python311/python.exe`) has it. Fix: either `pip install feedparser` in the venv, or update cron job to use system Python explicitly.

**Confirmed working (2026-07-23):** System Python path `D:/Program Files/Python311/python.exe scripts/rss_monitor.py` executes successfully. All imports (feedparser, requests, beautifulsoup4, dateutil) available in system Python 3.11.
8. **CPA feeds stale** — Most CPA/arbitrage RSS feeds return 0 entries. Need fresh feed sources or API-based alternatives.
9. **Full-history feeds (OpenAI, Google AI)** — Return ALL posts since inception. Client-side date filtering (`MAX_AGE_DAYS=7`) is mandatory. Without it, digest is flooded with years-old content.
10. **dateparser native dep failure** — `dateparser` → `regex` → `regex._regex` fails on Windows. Use `dateutil.parser` (pure Python, already installed with feedparser) instead.
11. **AffiliateFix forum RSS** — Returns forum threads, not articles. Summaries contain HTML (`<div class="bbWrapper">...`). Need HTML stripping if used for digest.
12. **Network resilience** — Partnerkin SSL EOF, AffiliateFix 30s read timeout. Increase `REQUEST_TIMEOUT` to 60s, add retry logic with backoff for flaky sources.
13. **Reddit RSS rate limiting (2026-07-18)** — Reddit returns 429 on r/passive_income and 0 entries on r/Entrepreneur. Public RSS endpoints are aggressively rate-limited. Mitigation: add custom User-Agent, space requests by 2-3s, or use authenticated Reddit API (praw) for reliable access.

## Verification Checklist

- [ ] Manual run: `python scripts/rss_monitor.py` succeeds (4/5 feeds OK, 40 entries)
- [ ] Cache written: `cache/rss_monitor/latest.json` exists, valid JSON, recent timestamp
- [ ] Cron job enabled in jobs.json
- [ ] Next run scheduled correctly
- [ ] Digest output delivered to configured destination (local/Telegram)
- [ ] Date filtering active: OpenAI entries ≤ 7 days old only
- [ ] `dateutil.parser` used (not `dateparser`)
- [ ] Network timeouts handled gracefully (errors logged, script continues)
- [ ] Reddit feeds: rate limit handling verified (User-Agent set, delays between requests)
- [ ] System Python path in cron job `script` field (avoids venv import errors)