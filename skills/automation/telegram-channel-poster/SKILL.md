---
name: telegram-channel-poster
description: "Post beautiful formatted messages with inline buttons to Telegram channels via Bot API. Supports HTML/Markdown, scheduling, multiple channels, content templates."
platforms: [linux, macos, windows]
---

# Telegram Channel Poster

## When to use
When you need to post formatted content with buttons to Telegram channels autonomously. Supports multiple channels, content templates, inline keyboards, and scheduling.

## Requirements
- Python 3.10+
- `python-telegram-bot` v22+ (`pip install python-telegram-bot`)
- Bot token with admin rights in target channels
- Channel IDs or @usernames

## Quick Start

```bash
# Set bot token
export TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."

# Test post
python scripts/telegram_poster.py test --channel @mychannel --category ai_tool

# Run cycle (posts to all channels at scheduled times)
python scripts/telegram_poster.py cycle
```

## Channel Configuration

Channels are defined in the script's `CHANNELS` dict:
```python
CHANNELS = {
    "max_brain_chef_official": -1003777013964,
    "ai_frontier_you": -1003705792421,
    "max_brain_chef_ai": -1003882833000,
    "neuro_kitchen_ai": -1003525498743,
}
```

Get channel IDs:
```bash
curl "https://api.telegram.org/bot${TOKEN}/getChat?chat_id=@channel_name"
```

## Content Templates

| Category | Use Case | Example |
|----------|----------|---------|
| `ai_news` | AI releases, model launches | "GPT-5 announced — reasoning at PhD level" |
| `ai_tool` | Tool reviews, tutorials | "Fal.ai — serverless GPU for Flux/SDXL" |
| `code_tip` | Code snippets, patterns | "Async HTTP with retry & backoff" |
| `analytics` | Traffic/CPA insights | "Cricket betting India: ROI 200-400% in IPL" |
| `motivation` | Quotes, productivity | "Rule of 2 minutes: do it now if <2min" |

Each template includes:
- HTML formatting (bold, italic, code, blockquote)
- Inline keyboard with CTA buttons (Source, Try, Save, Channels)
- Automatic hashtag injection

## Inline Keyboards

Every post gets a contextual keyboard:
```python
# Category-specific button (e.g., "🚀 Try Fal.ai" → https://fal.ai)
# Global buttons (always present):
#   📢 All Channels → https://t.me/max_brain_chef_official
#   🤖 Bot → https://t.me/max_brain_chef_bot
#   💬 Chat → https://t.me/+nVpNjeTXzXE5YTRi
#   🔥 Top → callback_data="top_posts"
```

## Scheduling

`POST_TIMES = ["09:00", "12:00", "15:00", "18:00", "21:00"]` (MSK)

Cron runs every 30 min, checks if current time matches a slot, posts one per channel per slot.

## Database

SQLite at `cache/tg_poster.db`:
- `posts` table: id, channel, category, content, status, msg_id, posted_at
- `schedule` table: channel, time, category, active

## Commands

| Command | Description |
|---------|-------------|
| `cycle` | Run posting cycle (cron entry point) |
| `status` | Show stats: total, posted, schedule, recent |
| `gen [N]` | Generate N preview posts |
| `test --channel @name --category ai_tool` | Send test post |
| `sched-add <channel> <time> <category>` | Add schedule entry |
| `sched-list` | List schedule |

## Pitfalls

- **Bot must be admin** in channel with "Post Messages" permission
- **HTML parse_mode** — escape `<`, `>`, `&` in user content
- **Rate limits** — 30 msg/sec globally, 20 msg/min per chat. Script sleeps 2s between channels
- **Session file** — not needed for Bot API (unlike Telethon)
- **Dry-run mode** — set `POST_TO_TELEGRAM = False` to test without sending

## Verification Results (2026-07-29)

| Test | Command | Result |
|------|---------|--------|
| Bot API connection | `getMe` | ✅ PASS (bot: @max_brain_chef_bot) |
| Channel access | `getChat` ×4 | ✅ PASS (4/4 channels, bot is admin) |
| Posting with inline keyboard | `sendMessage` ×4 | ✅ PASS (all delivered) |
| Callback query handling | Webhook test | 🟡 Pending (needs ngrok + webhook server) |
| Dry-run mode | `POST_TO_TELEGRAM=False` | ✅ PASS |

**Channels verified:**
- `max_brain_chef_official` (-1003777013964): "MAX BRAIN | AI & Agents"
- `ai_frontier_you` (-1003705792421): "AI: Фронтир | Агентные системы"
- `max_brain_chef_ai` (-1003882833000): "MAX BRAIN | AI & Agents"
- `neuro_kitchen_ai` (-1003525498743): "НейроКухня | AI Recipes"

**Bot token:** Loaded from `TELEGRAM_BOT_TOKEN` env var (.env)

## Integration

Use in cron:
```yaml
# cron/jobs.json
{
  "name": "telegram-channel-poster",
  "schedule": "*/30 * * * *",
  "script": "telegram_poster.py cycle",
  "workdir": "D:/Portable_Soft/hermes"
}
```

## File Structure

```
skills/automation/telegram-channel-poster/
├── SKILL.md
├── scripts/
│   └── telegram_poster.py
├── references/
│   ├── content-templates.md
│   └── button-patterns.md
└── templates/
    └── post_templates.json
```