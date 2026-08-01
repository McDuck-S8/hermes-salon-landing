# Path Prefix Bug Fix (2026-07-28)

## Issue
Cron jobs with `script: "scripts/script_name.py"` failed because the cron runner prepends `HERMES_HOME/scripts/`, resulting in `scripts/scripts/script_name.py`.

## Root Cause
The cron scheduler (`cron/scheduler.py:_run_job_script()`) already prepends `HERMES_HOME/scripts/` to the script path. Jobs must specify the filename ONLY.

## Affected Jobs (This Session)
- `youtube-watch` (was `"scripts/youtube_watch.py"`)
- `rss-monitor` (was `"scripts/rss_monitor.py"`)
- `daily-digest` (was `"scripts/daily_digest.py"`)
- `pinterest-auto-pinner` (was `"scripts/pinterest_image_gen.py --all --count 1"`)
- `telegram-channel-poster` (was `"scripts/telegram_poster.py cycle"`)

## Fix Applied
Remove `scripts/` prefix from job's `script` field:
```json
// BAD:
"script": "scripts/youtube_watch.py"

// GOOD:
"script": "youtube_watch.py"
```

## Prevention
When creating cron jobs via `cronjob(action='create', script=...)`, pass the script filename ONLY (no directory prefix).