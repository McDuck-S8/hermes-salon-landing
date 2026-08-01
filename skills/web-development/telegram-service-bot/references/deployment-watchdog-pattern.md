# Deployment + Watchdog Pattern (Windows/Hermes)

## Full Deployment Flow

1. **Bot token** — Create via @BotFather. Set `BOT_TOKEN` in project `.env` or `TELEGRAM_BOT_TOKEN` in Hermes root `.env`.
2. **Proxy** — If Telegram API is blocked, set `PROXY=socks5://127.0.0.1:10806` in project `.env`. Test proxy:
   ```python
   import socket; s=socket.socket(); s.settimeout(5); s.connect(('127.0.0.1',10806)); s.send(b'\x05\x01\x00'); print(s.recv(2).hex())
   # Expected: 0500 (SOCKS5 no auth)
   ```
3. **API compatibility check** — aiogram 3.24+ changed `AiohttpSession`:
   - OLD: `AiohttpSession(session=my_aiohttp_session)` → **broken**
   - NEW: `AiohttpSession(proxy=proxy_url)` or just `AiohttpSession()` (no proxy)
   - Pass to Bot: `Bot(token=token, session=session)`
4. **Foreground test** — `timeout 15 python -u main.py` should show "Bot @xxx started! Polling" within 10s.
5. **Kill leftover processes** — Before starting bg, ensure no old instances:
   ```
   taskkill //F //PID <pid>   # double-slash escapes MSYS path mangling
   ```
   Find PIDs via `wmic process where "name='python.exe'" get ProcessId,CommandLine | grep main.py`
6. **Background start** — `python -u main.py > data/bot.log 2>&1`
7. **Verify no conflict** — Check log: `grep -i conflict data/bot.log`. If `TelegramConflictError` appears, old instance is still running → go back to step 5.
8. **Verify polling** — Log should show "Run polling for bot @xxx" without errors.

## Watchdog Script Pattern

A simple liveness check (no close() to avoid flood control):

```python
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession

async def check_bot() -> bool:
    try:
        session = AiohttpSession(proxy=proxy_url) if proxy_url else AiohttpSession()
        bot = Bot(token=token, session=session)
        me = await bot.get_me()
        return bool(me)  # Don't close — flood control on repeated checks
    except Exception:
        return False
```

**Key:** Don't call `bot.close()` or `session.close()` in watchdog mode. Telegram imposes flood control on `Close` after ~5 rapid calls (retry after 400+ seconds). The session auto-cleans when the process exits.

### Hermes Cron Setup

The watchdog runs every 5 minutes via Hermes cron:

1. **Place script** in `~/.hermes/scripts/` — Hermes cron only accepts relative paths from this directory.
   ```
   # ~/.hermes/scripts/salon-bot-watchdog.bash
   #!/bin/bash
   cd "D:/path/to/project" && python -u cron/watchdog.py
   ```
2. **Create cron job**:
   - `action=create`, `schedule="every 5m"`, `script="salon-bot-watchdog.bash"`, `enabled_toolsets=["terminal"]`
   - Use `.bash` extension for bash scripts (`.sh` also works, resolved to bash)

## Conflict Recovery

If you get `TelegramConflictError: terminated by other getUpdates request`:

- One or more old bot processes are still running
- `process(action='kill')` is visual-only on Windows git-bash — does NOT terminate
- Proper kill: `taskkill //F //PID <pid>`
- Thorough sweep:
  ```
  wmic process where "CommandLine like '%main.py%' and name='python.exe'" get ProcessId
  ```
  Pipe each PID to `taskkill //F`
- After killing all, wait ~30s for Telegram to expire old polling session
- Restart fresh

### Prevent Recurrence

After a `TelegramConflictError`, the old poller may still be connected from Telegram's side even after local kill. Wait 30s before starting new instance.

### Why Multiple Instances Happen

Each `terminal()` call with `python main.py` creates a new process. If previous ones weren't properly killed (Windows `kill` is a no-op in git-bash), they accumulate. All fight for the same token. Scale: observed up to 4 instances from a single deployment session.
