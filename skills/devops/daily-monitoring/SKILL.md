---
name: daily-monitoring
description: Automated daily monitoring — RSS feeds, YouTube channels, aggregator, HTML digest. One-stop setup for multi-source data collection and daily briefing.
tags: [monitoring, rss, youtube, digest, cron, reporting]
---

# Daily Monitoring Pipeline

Automated monitoring of external sources (RSS feeds, YouTube channels) with scheduled collection and HTML daily digest.

## Architecture

```
hermes/
├── scripts/
│   ├── rss_monitor.py       # RSS/Atom feed parser (stdlib: urllib + xml.etree.ElementTree)
│   ├── youtube_watch.py     # YouTube channel checker (via yt-dlp --socket-timeout 10)
│   └── daily_digest.py      # Aggregator → digest.html (repo root), dashboard_data/, reports/
├── cache/
│   ├── rss_monitor/latest.json
│   └── youtube_watch/latest.json
├── digest.html               # Repo root: preview links work on GitHub Pages
├── reports/digest.html       # Archive
└── dashboard_data/digest.html # Served via HTTP on :8766
```

## Cron Jobs

| Job | Script | Schedule |
|-----|--------|----------|
| RSS Monitor | `scripts/rss_monitor.py` | Every 4h |
| YouTube Watch | `scripts/youtube_watch.py` | Every 6h |
| Daily Digest | `scripts/daily_digest.py` | Daily 08:00 |

## Setup

### 1. RSS Feeds (`scripts/rss_monitor.py`)

Edit `FEEDS` list in the script:

```python
FEEDS = [
    {"id": "partnerkin",    "url": "https://partnerkin.com/rss",           "topic": "cpa-news"},  # RSS dead − uses _scrape_partnerkin()
    {"id": "affiliatefix",  "url": "https://www.affiliatefix.com/forums/-/index.rss",  "topic": "cpa-news"},
    {"id": "openai_blog",   "url": "https://openai.com/blog/rss.xml",      "topic": "ai"},
    {"id": "anthropic_rsshub", "url": "https://rsshub.bestblogs.dev/anthropic/news", "topic": "ai"},
    {"id": "hackernews",    "url": "https://hnrss.org/frontpage?count=10", "topic": "tech"},
]
```

- Pure Python, no external dependencies (uses urllib + xml.etree.ElementTree + re)
- Timeout: 15s per feed, entries truncated to 10 per feed, summary to 500 chars
- Supports RSS 2.0 and Atom
- **Content:encoded** — feeds like Anthropic (via RSSHub) put the full article HTML in `<content:encoded>` rather than `<description>`. The parser checks `content:encoded` as fallback when `description` is empty
- **HTML stripping** — always strip tags + decode entities (`&amp;`→`&`, etc.) in the monitor, not in the digest, so cached data is clean
- **Partnerkin special handling** — the `/rss` feed stopped updating in Nov 2025, site still publishes daily. `fetch_feed()` redirects `partnerkin` to `_scrape_partnerkin()` which: scrapes homepage for article links → fetches each article page for date + description → returns max 15 entries. Article fetch has 10s timeout, failures produce title-only entries. Function lives at bottom of `rss_monitor.py` (imports: urllib, re, html.unescape)

### 2. YouTube Channels (`scripts/youtube_watch.py`)

Edit `CHANNELS` list:

```python
CHANNELS = [
    {"id": "easy_traff",  "url": "https://www.youtube.com/@easy_traff/videos",  "topic": "cpa-arbitrage"},
]
```

- Uses yt-dlp with `--flat-playlist --socket-timeout 10` to avoid hanging
- Fast: typically 1-3 seconds per channel

### 3. Daily Digest (`scripts/daily_digest.py`)

```bash
python scripts/daily_digest.py       # Generate HTML
python scripts/daily_digest.py --text # Terminal output
```

Digest saves to 3 locations:
- `digest.html` (repo root) — so preview links `projects/ai-ofm-tribute/content/sessions/*/preview.html` work from GitHub Pages
- `dashboard_data/digest.html` — for local HTTP server on port 8766
- `reports/digest.html` — historical archive

## Report Format Standard (MANDATORY)

Any digest/aggregation/brief delivered to the user MUST be HTML with:

1. **Categories** with clear headings (CPA, AI, Tech, etc.)
2. **1-2 sentence descriptions** under each link — so the user knows what it's about without clicking
3. **All links clickable** (target="_blank")
4. **Dark theme**, readable typography
5. **Saved to repo root** (for GitHub Pages), `dashboard_data/` (HTTP on 8766), and `reports/` (archive)

**Forbidden**: raw link dumps without descriptions, plain-title lists, unformatted terminal output.

## References

- `references/rss-sources.md` — Verified RSS feed URLs, quirks (Anthropic full HTML, Partnerkin RSS dead→scrape, AffiliateFix descriptions), date parsing notes, and YouTube channel status

## Pitfalls

### General
- **yt-dlp channels** — not all YouTube channels have a `videos` tab. If the channel fails, check if the URL format is correct or drop it
- **RSS timeouts** — some feeds are slow; the script has 15s timeout, failed feeds are reported with error message, not fatal
- **HTTP server** — the dashboard server serves from `dashboard_data/`, not project root. HTML files must be saved there to be accessible at `http://localhost:8766/`
- **Windows shell** — always use `python` not `python3` in scripts (cron.sh fix: `python3` → `python`)
- **HTML descriptions** — RSS summaries often contain HTML tags (<article>, <div class="...">); strip them with regex before displaying. Some feeds (Anthropic via RSSHub) embed full article HTML in <content:encoded> instead of <description> — the monitor must check both fields. Strip in the monitor, not the digest, so cached data stays clean
- **Empty descriptions** — some RSS feeds (e.g. AffiliateFix `/forums/-/index.rss`) return entries with no `<description>` at all. Either fetch the URL content (slow, 3-5s per URL) or skip those entries. Fetch-and-cache once if the user demands them
- **Partnerkin dead RSS** — the `/rss` feed stopped updating Nov 2025. `fetch_feed()` redirects `partnerkin` to `_scrape_partnerkin()` which scrapes the homepage for article links and fetches each page. This means Partnerkin is slower (1 HTTP for homepage + up to 15 per-article requests) and depends on homepage HTML structure. If the site redesigns, the scraper breaks. Monitor the entry count: if Partnerkin returns 0 entries, the scraper needs updating

### Digest Content Quality (6 mandatory checks)
The digest MUST pass these checks before delivery:

1. **Date filter** — remove entries older than the current month. Parse RSS `published` date (multiple formats: RFC 2822, ISO 8601, `%Y-%m-%d`). Keep entries with no date (can't prove they're stale). Use `datetime.strptime` with a format list. **EXCEPTION**: CPA/Arbitrage entries are exempt from date filtering — even old Partnerkin articles (2022-2023) are valuable and must be kept
2. **Empty descriptions** — if description is empty after HTML stripping, skip the entry (non-CPA). For CPA entries, try fetching the URL to extract a description before giving up. AffiliateFix entries have descriptions now (the monitor fetches them), but verify
3. **HTML stripping** — `re.sub(r'<[^>]+>', '', text)` then decode HTML entities (`&amp;`→`&`, `&lt;`→`<`, etc.). Anthropic feed (via RSSHub) puts full `<article>` blocks in `<content:encoded>`. Strip in the monitor, cache clean text
4. **Session/image counting** — AI OFM sessions may use legacy formats. Never assume `success_count` exists: fall back to `len(images)`. Sessions with images but no `manifest.json` exist — count jpg/png files in the directory. Skip sessions where `success_count=0` (all image generations failed). Show sessions without manifests with `style="?"`, `model="?"`, and a red note "нет манифеста"
5. **Preview links** — preview URLs must be relative to the REPO ROOT (not the HTTP server root). Use `projects/ai-ofm-tribute/content/sessions/{dir.name}/preview.html`. This works on GitHub Pages at `https://USER.github.io/REPO/projects/ai-ofm/...` and locally when opening `digest.html` as a file. Do NOT use `/previews/` paths (they only work from the HTTP server on port 8766)
6. **AI content filter** — the AI section must only contain tools/earning-relevant items. Use a whitelist regex AND a blocklist:
   - Keep: `GPT|Claude Sonnet|model|API|SDK|tool|code|agent|autonomous|deploy|launch|release|upgrade|earn|profit|invest|business|enterprise|pricing|benchmark|performance|Fable|jailbreak|bug bounty`
   - Block: `teacher|Bernanke|Trust|reflect|buddy|reflection|government|national security|LGBTQ|pride|Deutsche Telekom|rewiring|telecommunications|Getting started|partner for your|ambitious work|How .* teams use|hard questions`
   - An item matching the blocklist is excluded regardless of whitelist match
7. **Tech entertainment filter** — the Tech section must only contain useful/technical articles. Block entertainment: `Jurassic Park|Super Mario|LeMario|Vancouver PD|Quick Escape|Probably check on your smart|book review|retro gaming`. Keep: security, exploits, dev tools, architecture, AI news, programming
8. **Content language** — AI (OpenAI, Anthropic) and Tech (HN) feeds are in English. CPA feeds (Partnerkin, AffiliateFix) are in Russian. The digest doesn't translate — output will be mixed. If full Russian is required, add a translation step (e.g. deep-translator or llm call) between fetch and display

### Partnerkin-Specific
- **RSS is dead** — the `/rss` feed stopped updating Nov 2025. Monitor uses `_scrape_partnerkin()` which fetches homepage + each article page. This requires ~16 HTTP requests total per run. Slower than RSS but necessary
- **Site structure dependency** — the scraper keys off homepage HTML patterns (href with `/blog/`/`/tribuna/`/`/kejsy/`/`/intervyu/`). A site redesign will break it. Monitor entry count: if Partnerkin returns 0 entries, inspect the site HTML and update regex patterns
- **Content language** — all Partnerkin articles are in Russian. No translation needed if the user is Russian-speaking
- **Date extraction** — Partnerkin pages don't have a consistent date format. The scraper tries `YYYY-MM-DD HH:MM` first, then `DD.MM.YYYY`. Some articles get empty dates — acceptable, the digest shows them regardless

### OFM-Specific
- **Legacy sessions** (1-2): have `images` array in manifest but no `success_count`. Count from `images` length. These sessions also have no JPG files on disk — only `preview.html` rendering broken image links
- **Sessions with images, no manifest**: some sessions (06, 11) exist as directories with JPG files but no `manifest.json`. Count files by globbing `*.jpg` + `*.png`
- **Failed sessions**: manifest exists with `success_count=0`. Skip entirely — all generations failed and user doesn't need to see zeros
