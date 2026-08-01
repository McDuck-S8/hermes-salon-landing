# TG Channel Poster — Automated CPA Content Posting

## Purpose
Script that posts content from `cache/tg_channel_posts.json` to a Telegram channel.
Designed for the CPA monetization pipeline: generate content -> post -> add CPA links -> earn.

## File
`scripts/tg_channel_poster.py`

## Features
- Posts one at a time or all with configurable delay
- Tracks which posts have been published (status file)
- Supports SOCKS5 proxy (reads from .env)
- Preview mode (--preview) to see what would be posted
- Status tracking (--status)

## Prerequisites
1. `TELEGRAM_BOT_TOKEN` in .env
2. `TELEGRAM_CHANNEL_ID` in .env (format: @channelname or -100xxxxxxxxxx)
3. `PROXY=socks5://127.0.0.1:10808` in .env (for RF network)
4. Posts in `cache/tg_channel_posts.json` — array of {title, text, hashtags}

## Usage
```bash
# Preview what would be posted
python scripts/tg_channel_poster.py --preview

# Post next unpublished post
python scripts/tg_channel_poster.py

# Post all with 30s delay between
python scripts/tg_channel_poster.py --post-all

# Check status
python scripts/tg_channel_poster.py --status

# Post to specific channel
python scripts/tg_channel_poster.py --channel @MyChannel
```

## Network Notes (2026-06-22)
On this machine, outbound HTTP may be blocked even with v2rayN running.
v2rayN ports detected (LISTENING):
- 10808 (SOCKS5) — PID 17080
- 10806 (SOCKS5 mixed) — PID 52208
- 10809 (HTTP) — PID 17080
- 10810 (HTTP) — PID 52208

The script loads PROXY from .env and uses PySocks for SOCKS5.
When proxy works, the script connects to api.telegram.org automatically.

## Content Pipeline
```
DeepSeek/Groq API -> cache/tg_channel_posts.json -> tg_channel_poster.py -> Telegram channel -> CPA links -> revenue
```

Posts should include CPA tracking links (Admitad, FinCPA, etc.).
Current posts reference @HotelCrimeaBot as CTA — replace with CPA links when account is ready.
