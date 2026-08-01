# TG CPA Auto-Poster — Quick Reference

## Script
`D:/Portable_Soft/hermes/scripts/tg_cpa_poster.py`

## What it does
Posts AI-business-content to Telegram channels with CPA affiliate links.
- 10 pre-written post templates (ai_tips, business_ideas categories)
- Proxy support (HTTP 127.0.0.1:10809 via v2rayN)
- Post logging to `cache/tg_post_log.json`
- Loop mode with configurable interval

## Setup
1. Create TG channel (user action)
2. Add bot @HotelCrimeaBot as admin
3. Configure `cache/tg_channels.json`:
   ```json
   [{"id": "-1001234567890", "name": "AI Business Ideas", "active": true}]
   ```
4. Register in Admitad or FinCPANetwork for CPA links
5. Replace placeholder links in post templates

## Usage
```bash
# Preview posts
python scripts/tg_cpa_poster.py --preview

# Single post to all channels
python scripts/tg_cpa_poster.py

# Loop every hour
python scripts/tg_cpa_poster.py --loop 3600

# Specific channels
python scripts/tg_cpa_poster.py --channels -1001234567890
```

## Dependencies
- `scripts/telegram_bridge.py` (fixed proxy support)
- TELEGRAM_BOT_TOKEN in .env
- v2rayN proxy on 127.0.0.1:10809

## Known Issues
- CPA links are placeholders until network registration
- Channel must be created manually (bot can't create channels)
- **CRITICAL: CPA registration requires email/phone/approval — cannot be done autonomously.**
- **Workaround: Use direct services instead (see revenue-test-pivot-2026-06-28.md)**
