# Salon Bot Deployment Checklist (verified 2026-06-22)

## Pre-flight

1. Verify correct Python: `"D:/Program Files/Python311/python.exe" -c "from aiohttp import BasicAuth; print('OK')"`
2. Kill stale instances: `wmic process where "name='python.exe'" get ProcessId,CommandLine` → find main.py entries → `subprocess.run(['taskkill', '/PID', pid, '/F'])`
3. Verify proxy: `curl -x socks5://127.0.0.1:10806 -s --connect-timeout 5 https://api.telegram.org`

## Start

```bash
cd D:/Portable_Soft/hermes/projects/salon-bot && "D:/Program Files/Python311/python.exe" -u main.py
```

Run via `terminal(background=true)`. Note: output will likely be invisible in process logs.

## Verify (programmatic, never ask user)

1. `getMe()` → bot username and ID
2. `getMyCommands()` → registered commands list
3. `getWebhookInfo()` → confirm polling mode, 0 pending updates
4. `sendMessage(superadmin_id, "Health check")` → confirm delivery
5. If TelegramConflictError → another instance is still running; kill and retry

## DB Sanity Check

```python
import sqlite3
for path in ['data/salon.db', 'bot/data/salon.db']:
    try:
        conn = sqlite3.connect(path)
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        print(f'{path}: {tables}')
    except: pass
```

bot/db.py uses `Path(__file__).parent / "data" / "salon.db"` → resolves to `bot/data/salon.db`.
config.DB_PATH may point to `data/salon.db` (possibly empty).
The Path(__file__) resolution is what the bot actually uses.
