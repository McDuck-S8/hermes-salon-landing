---
name: telegram-digest
description: "Collect messages from Telegram channels and create daily digests"
platforms: [linux, macos, windows]
---

# Telegram Channel Digest Collector

## When to use
When user wants to monitor Telegram channels and get daily digests/summaries.

## Requirements
- Telethon library (`pip install telethon`)
- Telegram API credentials (api_id, api_hash) in .env
- User session file (created on first run)

## Posting to Channels (Bot API)

In addition to collecting messages, this skill covers **posting** to Telegram channels via Bot API.

### Finding channel IDs
Use the Telegram Bot API via `requests` (SAFE: HTTP request, no shell). Bot token is read from `TELEGRAM_BOT_TOKEN` env var at runtime.

### Sending messages
```python
# SAFE: Uses requests instead of subprocess+curl
import requests, os, json
token = os.environ.get('TELEGRAM_BOT_TOKEN')
if token:
    r = requests.post(
        f'https://api.telegram.org/bot{token}/sendMessage',
        headers={'Content-Type': 'application/json'},
        json={'chat_id': '@channel_name', 'text': 'Post text here', 'disable_web_page_preview': True}
    )
    print(r.json())
```

### Checking bot access
Bot must be added as **admin** to the channel with "Post messages" permission.
Use `getChat` to verify access — returns 404 if bot has no access.

### Listing accessible chats
`getUpdates` only shows DMs and groups, NOT channels. For channels, use `getChat` directly with known @usernames or chat_ids.

## Scripts

| Script | Purpose | Session file |
|--------|---------|-------------|
| `scripts/auth.py` | One-time Telegram auth | hermes_session |
| `scripts/collect_channels.py` | Raw message collection | hermes_session |
| `scripts/digest_pipeline.py` | Collect + format digest (cron-ready) | hermes_session |
| `scripts/monitor.py` | Collect → analyze interesting → report with proposals | hermes_monitor |
| `scripts/cron_monitor.py` | Cron wrapper for monitor.py | hermes_monitor |

### monitor.py — Smart Analysis

Unlike collect_channels.py (raw data), monitor.py:
- Scores messages by views, forwards, keyword density
- Finds viral/trending content (thresholds: 10k views, 2x channel avg)
- Generates report with proposals (reshare, evaluate, integrate)
- Supports presets: `--preset ai_news`, `--preset crypto`, `--preset all`
- Channels configured in `cache/telegram_monitor/channels.json`

## Fallback: t.me/s/ Preview Unreliable

t.me/s/ preview pages frequently fail. Tested 2026-06-27:
- `t.me/s/openai` — timeout (browser + web_extract both fail)
- `t.me/s/hugging_face` — server disconnects, no data
- `t.me/s/anthropic` → redirects to "Discover • Tech News" (wrong channel)
- `t.me/s/deepseek` — loads, but only 1 post (small channel)
- `t.me/s/GoogleAI` — loads, minimal branded content

**Reliable fallback chain:**
1. `web_search_plus(query="OpenAI latest news June 2026", time_range="week")` per company
2. `web_extract(urls=[official_news_page])` — e.g. `openai.com/news/`, `anthropic.com/news`
3. Combine into report, save to `cache/telegram_monitor/latest_report.md`

Do NOT retry t.me/s/ URLs more than once — switch to fallback immediately.

## Regional Network Block: MTProto Unreachable (2026-06-27)

**Symptom:** `ConnectionError: Connection to Telegram failed 5 time(s)` or `OSError: [WinError 121] Превышен таймаут семафора`

**Cause:** MTProto (Telethon) is blocked in some regions (e.g. Crimea). Direct TCP connections to Telegram servers time out.

**Fallback chain (in order):**
1. **Bot API** — works via HTTPS, less likely blocked. Use `urllib.request` to call `api.telegram.org/bot{token}/...`. Requires bot token in .env (`TELEGRAM_BOT_TOKEN` — placeholder, set via `hermes config`). Bot must be admin in channel to read messages.
2. **Browser scraping** — `browser_navigate` to `https://t.me/s/{channel}` renders JavaScript, then `browser_snapshot` extracts text content. Works for public channels. Slow but reliable.
3. **Web search fallback** — `web_search_plus(query="OpenAI latest news", time_range="week")` + `web_extract` on official news pages. Not real-time but covers major announcements.
4. **Give up** — if all above fail, report the block and suggest user configure a proxy/VPN.

**Do NOT** keep retrying MTProto after 2 failed attempts. Switch to fallback immediately.

**Test result (2026-06-27):**
- MTProto: BLOCKED (timeout)
- Bot API: works for channels where bot is admin
- Browser: works for public channels (t.me/s/ pages render JS)
- web_extract: FAILS on t.me/s/ (JS-heavy pages, returns empty shell)
- t.me/s/openai, t.me/s/hugging_face: timeout even in browser
- t.me/s/anthropic: redirects to wrong channel ("Discover • Tech News")

## Pitfalls
- **Never use `Path(__file__).parent.parent.parent...` chains** for locating .env or sessions dir. These break when files move. Always use `os.environ.get('HERMES_HOME', Path.home() / '.hermes')` to find the data root.
- **Always check imports match usage** — run `ast.parse()` on every script before committing. Common miss: `sys.exit()` without `import sys`.
- **Test auth flow before cron** — the session file must exist before any scheduled job runs. Run `auth.py` interactively first.
- **Channel usernames** — use without `@` prefix. Private channels require the user to be a member with the Telethon session account.
- **Credential redaction** — Hermes redacts secrets in all tool inputs. Never embed tokens directly in terminal/write_file. Write a .py script that reads from .env at runtime, then execute it. See `references/credential-redaction-workaround.md`.
- **Content quality** — never publish model reasoning ("Thought for..."). Check recent posts before publishing. See `references/content-quality-standards.md`.
- **Cron script location** — cron jobs require scripts in `~/.hermes/scripts/`, NOT in the skill directory. Copy the script: `cp SKILL_DIR/scripts/cron_monitor.py ~/.hermes/scripts/telegram_cron_monitor.py`. The cron tool rejects absolute paths outside that directory.
- **Telethon venv mismatch** — `pip install telethon` installs to system Python, but terminal runs the hermes venv Python. Fix: `uv pip install telethon --python "D:/Portable_Soft/hermes/hermes-agent/venv/Scripts/python.exe"`. Verify with: `python -c "import telethon; print('OK')"`.
- **Session file naming** — collect_channels.py defaults to `hermes_session`, monitor.py defaults to `hermes_monitor`. They are different session files. If switching scripts, auth may need re-running for the new session name.

## Pipeline Architecture
See `references/pipeline.md` for the full collect → digest → deliver chain.

## Monitor Scoring & Presets
See `references/monitor-scoring.md` for scoring algorithm, channel presets, and config format.

## Setup
1. Get api_id and api_hash from https://my.telegram.org
2. Add to .env:
```
|TELEGRAM_API_ID=<your_api_id>
|TELEGRAM_API_HASH=<your_api_hash>
```
3. Run auth flow once (see scripts/auth.py)

## Usage
```bash
# Collect last 24h messages from channels
python3 SKILL_DIR/scripts/collect_channels.py --channels "channel1,channel2" --hours 24

# Output JSON with messages
python3 SKILL_DIR/scripts/collect_channels.py --channels "channel1,channel2" --output /tmp/digest.json
```

## Output Format
```json
{
  "collected_at": "2026-05-24T09:00:00",
  "channels": {
    "channel_name": {
      "url": "https://t.me/channel_name",
      "messages": [
        {
          "id": 123,
          "date": "2026-05-24T08:30:00",
          "text": "message text",
          "views": 1500,
          "forwards": 50,
          "link": "https://t.me/channel_name/123"
        }
      ]
    }
  },
  "total_messages": 42
}
```
