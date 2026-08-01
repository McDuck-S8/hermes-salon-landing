---
name: youtube-channel-monitor
description: "YouTube channel monitoring via yt-dlp cron job — fetches latest videos from configured channels, caches results, detects new videos by comparing against previous snapshot. Includes cron path fix pattern and feed validation."
tags: [cron, youtube, monitoring, yt-dlp, automation, cpa-arbitrage]
platforms: [linux, macos, windows]
---

# YouTube Channel Monitor

## When to use
When setting up or fixing scheduled YouTube channel monitoring that runs as a cron job, fetches latest videos via yt-dlp, caches results, and reports new videos from CPA/arbitrage or other topic-specific channels.

## The Cron Path Bug (Critical Fix)

**Symptom:** Cron job fails with `Script not found: D:\\Portable_Soft\\hermes\\scripts\\scripts\\youtube_watch.py` (double `scripts/` in path)

**Root Cause:** The cron runner (`hermes cron run` or scheduler) executes from the Hermes root directory (`D:/Portable_Soft/hermes`), but some job definitions or path resolvers prepend `scripts/` again, creating `scripts/scripts/youtube_watch.py`.

**Fix Applied in jobs.json:**
```json
{
  "script": "scripts/youtube_watch.py"
}
```
NOT `scripts/scripts/youtube_watch.py`. The runner already prefixes `scripts/`.

**Verification:** After fix, run manually:
```bash
cd D:/Portable_Soft/hermes
python scripts/youtube_watch.py
```
Should output: `[youtube_watch] Checking easy_traff... OK: 5 videos` etc.

---

## Dependencies

- **yt-dlp** must be installed and in PATH:
  ```bash
  pip install yt-dlp
  # or on Windows with scoop/choco:
  scoop install yt-dlp
  ```

- Python 3.8+ with stdlib modules: `json`, `subprocess`, `datetime`, `pathlib`

---

## Script: `scripts/youtube_watch.py`

### Configuration (in-script)

```python
CHANNELS = [
    {"id": "easy_traff",      "url": "https://www.youtube.com/@YOSArun/videos",    "topic": "cpa-arbitrage"},
    {"id": "partnerkin",      "url": "https://www.youtube.com/@partnerkin/videos",     "topic": "cpa-affiliate"},
]
```

Add new channels by appending to this list with:
- `id`: unique short identifier (used as cache key)
- `url`: channel videos page URL (must end with `/videos`)
- `topic`: category tag for filtering/reporting

### Fetch Logic

1. Runs `yt-dlp --socket-timeout 10 --flat-playlist --dump-json --playlist-end 5 --no-warnings <channel_url>`
2. Parses JSON lines output (one video per line)
3. Extracts: `id`, `title`, `url`, `duration_string`, `timestamp`, `playlist_index`
4. Returns list of video dicts or error dict with `error` key

**Critical flags:**
- `--flat-playlist` — fetches only metadata (no formats/subtitles), essential for speed/reliability. Trade-off: `description`, `tags`, `timestamp` come back empty/null in flat mode. Video `id` and `title` are reliable for new-video detection.
- `--socket-timeout 10` — per-connection timeout
- Subprocess timeout: **90s** (script-level `timeout=90` in `subprocess.run`) — buffers against yt-dlp internal retries/stalls

### Cache Format

**Location:** `cache/youtube_watch/latest.json`

```json
{
  "timestamp": "2026-07-18T07:43:32.506021+00:00",
  "channels": {
    "easy_traff": {
      "url": "https://www.youtube.com/@YOSArun/videos",
      "topic": "cpa-arbitrage",
      "videos": [
        {
          "id": "QCURb_DkMwg",
          "title": "Video Title",
          "url": "https://youtube.com/watch?v=QCURb_DkMwg",
          "duration": "1:26:34",
          "uploaded": 1721234567,
          "playlist_index": 1
        }
      ]
    }
  }
}
```

### New Video Detection

To detect new videos since last run, compare `videos[0].id` (latest video) against previous cache's latest video ID. If different, new content exists.

---

## Cron Job Definition (jobs.json)

```json
{
  "id": "bac03cbb9537",
  "name": "youtube-watch",
  "prompt": "Run the YouTube channel monitor and report any new videos from CPA/arbitrage channels.",
  "script": "scripts/youtube_watch.py",
  "no_agent": false,
  "schedule": { "kind": "interval", "minutes": 360 },
  "deliver": "local",
  "enabled": true
}
```

- **Interval:** 360 minutes (6 hours) — balances freshness with API quota
- **Delivery:** `local` (output captured in `cron/output/<job_id>/`)
- **Agent mode:** `no_agent: false` — runs through agent for LLM summarization

---

## Output & Reporting

### Cron Output Location

`cron/output/<job_id>/<timestamp>.md` — contains agent-summarized report of new videos

### Manual Run Output

```
[youtube_watch] Checking easy_traff...
  OK: 5 videos
[youtube_watch] Checking partnerkin...
  OK: 5 videos

Done: 2/2 channels OK, 0 errors, 10 total videos
```

### Channel Status Codes

| Status | Meaning |
|--------|---------|
| `OK: N videos` | Successfully fetched N videos |
| `ERROR: <msg>` | yt-dlp failed (timeout, not found, channel unavailable) |

---

## Known Working Channels (validated 2026-07-23)

| Channel ID | URL | Topic | Videos Fetched | Status |
|------------|-----|-------|----------------|--------|
| `easy_traff` | https://www.youtube.com/@YOSArun/videos | cpa-arbitrage | 5 | ✅ Active |
| `partnerkin` | https://www.youtube.com/@partnerkin/videos | cpa-affiliate | 5 | ✅ Active |

## Broken / Irrelevant Channels (validated 2026-07-24)

| Channel ID | URL | Topic | Issue | Action |
|------------|-----|-------|-------|--------|
| `icpsquad` | https://www.youtube.com/@icpsquad/videos | crypto/ICP | All videos from 2023, not CPA/arbitrage | Remove from CHANNELS |
| `traffic_hunter` | https://www.youtube.com/@TrafficHunter/videos | cpa-arbitrage | "This channel does not have a videos tab" | Remove or fix URL |
| `webvork` | https://www.youtube.com/@webvork/videos | cpa-arbitrage | "This channel does not have a videos tab" | Remove or fix URL |

### Adding New Channels

1. Verify channel URL works: `yt-dlp --flat-playlist --playlist-end 1 --dump-json "https://www.youtube.com/@CHANNEL/videos"`
2. Add to `CHANNELS` list in `youtube_watch.py`
3. Test manual run: `python scripts/youtube_watch.py`
4. Verify cache updates at `cache/youtube_watch/latest.json`

---

## Pitfalls

1. **yt-dlp not in PATH** — Cron runner may use different shell/env. Fix: install globally or use full path in script (`/usr/local/bin/yt-dlp` or `D:\\\\Portable_Soft\\\\hermes\\\\.venv\\\\Scripts\\\\yt-dlp.exe`)

2. **Channel URL changes** — YouTube handles change; verify `/videos` endpoint returns data. Some channels use `/streams` or `/featured` instead.

3. **Rate limiting** — yt-dlp handles retries but aggressive polling (interval < 60m) may trigger IP blocks. Current 360m interval is safe.

4. **Private/deleted videos** — May appear in playlist but fail on detail fetch. Flat playlist mode avoids this.

5. **Missing upload timestamp** — Some videos return `null` for `timestamp`. Use `playlist_index` as proxy for recency (1 = newest).

6. **Double scripts/ path** — Always verify `script` field in jobs.json is `scripts/xxx.py` not `scripts/scripts/xxx.py`

7. **Cron job model drift (NEW 2026-07-24)** — The cron job `bac03cbb9537` fails with `RuntimeError: global inference config drifted since this job was created (model 'nemotron-3-ultra-free' -> 'deepseek-v4-flash-free'), and this job is unpinned`. The Hermes scheduler blocks inference calls when the global model config changes and the job doesn't have explicit `provider`/`model` pinned. **Fix:** Either pin the job explicitly in jobs.json with `"provider": "opencode_zen", "model": "nemotron-3-ultra-free"` (or desired model), or accept the new default. The script runs fine manually — only the agent summarization step fails in cron.

---

## Verification Checklist

- [ ] Manual run: `python scripts/youtube_watch.py` succeeds (all channels OK)
- [ ] Cache written: `cache/youtube_watch/latest.json` exists, valid JSON, recent timestamp
- [ ] Cron job enabled in jobs.json
- [ ] Next run scheduled correctly
- [ ] Output delivered to configured destination (local/Telegram)

---

## Reference Files

- `references/channel-directory.md` — Master list of monitored channels with metadata
- `references/yt-dlp-flags.md` — Documented yt-dlp flag combinations for different use cases
- `references/new-video-detection.md` — Algorithm for comparing cache snapshots