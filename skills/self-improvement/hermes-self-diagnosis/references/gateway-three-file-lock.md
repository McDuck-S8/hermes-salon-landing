# Gateway Three-File Lock Mechanism

## Problem
Gateway reports: `Telegram bot token already in use (PID 50540). Stop the other gateway first.`
Killing the PID does NOT fix it — the error persists across restarts.

## Root Cause
Three files form the lock mechanism. All three must be cleared:

1. **`gateway.lock`** — JSON with `{"pid": N, "kind": "hermes-gateway", ...}`
2. **`gateway_state.json`** — Full state including `platforms.telegram.error_code` and `exit_reason`
3. **Any other `.lock` files** referencing the dead PID

## Fix Sequence

```bash
# 1. Kill the dead process (if still alive)
taskkill /PID 50540 /F

# 2. Delete gateway.lock
rm D:/Portable_Soft/hermes/gateway.lock

# 3. Reset gateway_state.json
echo '{"pid":0,"kind":"hermes-gateway","argv":[],"start_time":null,"gateway_state":"idle","exit_reason":null,"restart_requested":false,"active_agents":0,"platforms":{},"updated_at":"<now>"}' > D:/Portable_Soft/hermes/gateway_state.json

# 4. Also clean auth.lock if present
rm -f D:/Portable_Soft/hermes/auth.lock

# 5. Restart gateway
cd D:/Portable_Soft/hermes/hermes-agent && HERMES_HOME=D:/Portable_Soft/hermes ./venv/Scripts/python.exe -m hermes_cli.main gateway run
```

## Why State Persists
`gateway_state.json` is written on every gateway lifecycle event (start, exit, error).
On restart, the gateway reads this file and sees the stale `telegram-bot-token_lock` error
from the previous session, even though the PID is dead. The file acts as a "last known state"
cache — clearing it forces a fresh evaluation.

## Detection
```bash
# Check if state file has stale lock
cat D:/Portable_Soft/hermes/gateway_state.json | grep "telegram-bot-token_lock"
# If found + PID is dead → reset required
tasklist /FI "PID eq <pid_from_state>" 2>/dev/null
```

## Cross-Installation PID Conflict

When two Hermes installations exist (e.g. `D:/Portable_Soft/hermes/` and `D:/Portable_Soft/hermes-usb-portable-main/`), the OLD installation's gateway may still be running and holding the Telegram bot token lock.

**Detection:**
```bash
# Error message will reference a PID
# "Telegram bot token already in use (PID 13916)"

# Check what process owns that PID:
wmic process where ProcessId=13916 get Name,CommandLine 2>/dev/null
# If output shows: pythonw.exe ... -m hermes_cli.main gateway run
# → it's the OLD installation's gateway

# Check which installation it belongs to:
wmic process where ProcessId=13916 get CommandLine 2>/dev/null
# Look for path: hermes-usb-portable-main → OLD installation
```

**Fix:**
```bash
# Kill the OLD gateway (must use cmd.exe /c — Git Bash converts /PID to path)
cmd.exe /c "taskkill /PID 13916 /F"

# Then follow the standard three-file lock fix above
```

**Why this happens:** The Scheduled Task "Hermes_Gateway" may point to the old installation's hermes binary. Check with:
```bash
schtasks /query /tn "Hermes_Gateway" /v /fo list 2>/dev/null | grep -A2 "Task To Run"
```

## Gateway "No messaging platforms enabled"

When `~/.hermes/config.yaml` has NO `gateway:` section, the gateway starts but finds zero platforms. It logs:
- "No messaging platforms enabled."
- "Gateway will continue running for cron job execution."

The gateway may exit immediately or run headless without Telegram. Cron jobs need the gateway's cron ticker thread, but without a `gateway:` section in config, the platform initialization loop finds nothing to adapter-ize.

**Fix:** Add a `gateway:` section to `~/.hermes/config.yaml`:
```yaml
gateway:
  telegram:
    enabled: true
```
Or run `hermes gateway setup` for guided configuration.

**Alternative for cron-only mode:** If you only need cron jobs (no Telegram), the gateway CAN run without platforms — but it must stay running. The "No messaging platforms enabled" warning is non-fatal; the cron ticker still starts. The issue is that without a configured platform, there's no reason for the gateway to stay alive long enough for the ticker to fire.

## Salon Bot Startup
The salon bot (`scripts/salon_booking_bot.py`) has its own requirements:
- Needs `TELEGRAM_BOT_TOKEN` env var (not auto-loaded from `.env`)
- Needs aiogram (only in system Python 3.11, NOT in hermes venv)
- Needs SOCKS5 proxy for Telegram API access from Russia

```bash
# Correct startup command:
cd D:/Portable_Soft/hermes
export TELEGRAM_BOT_TOKEN=$(grep TELEGRAM_BOT_TOKEN .env | cut -d= -f2)
"/d/Program Files/Python311/python.exe" scripts/salon_booking_bot.py
```

## Python Path Quirk
Two Python installations exist:
- `hermes-agent/venv/` — Python 3.13.2, has hermes-cli, NO aiogram
- `/d/Program Files/Python311/` — Python 3.11, has aiogram, NO hermes-cli

Scripts that need both (e.g., salon bot calling hermes hooks) must be run with system Python
and manually add hermes scripts to sys.path.
