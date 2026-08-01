# Deploy-Via-Token Pattern

When deploying Telegram bots that share infrastructure with the Hermes gateway:

## Problem
Hermes gateway uses TELEGRAM_BOT_TOKEN from .env. If another bot (e.g., salon_bot.py) uses the SAME token, Telegram returns 409 Conflict on getUpdates.

## Solution
Each bot needs its OWN token from @BotFather.

## Deploy script pattern
```python
# deploy_<botname>.py
# 1. Verify token with getMe (test only, no polling)
# 2. Start bot as background process with its own env
# 3. Save PID to cache/<botname>.pid
```

## Anti-pattern: using same BOT_TOKEN
- Gateway + salon_bot on same token → 409 Conflict
- "Bot was kicked from supergroup" errors
- Intermittent getUpdates failures

## Files
- `scripts/deploy_salon.py` — deploy script for salon bot
- `cache/salon_bot.pid` — PID tracking

## Steps to deploy
1. Create new bot via @BotFather → get token
2. `python scripts/deploy_salon.py YOUR_TOKEN`
3. Bot runs in background, PID saved
4. Test: send /start to the new bot
