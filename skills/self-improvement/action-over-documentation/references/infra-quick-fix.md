# Infrastructure Quick-Fix Checklist

Fast triage: check → fix → move on. Max 2 checks before first fix.

## Hermes Core

```bash
# Gateway running?
hermes gateway status
# Not running → START IT
hermes gateway start

# Cron jobs stale? (check next_run_at in jobs.json)
cat cron/jobs.json | python -c "import json,sys; [print(f\"{j['name']}: next={j.get('next_run_at','?')}\") for j in json.load(sys.stdin)['jobs'] if j.get('enabled')]"
# Stale → gateway start fixes this (cron scheduler runs inside gateway)
```

## Python Projects (salon-bot, money4band, etc.)

```bash
# Missing deps? (ModuleNotFoundError in traceback)
cd projects/<name> && .venv/Scripts/pip.exe install <missing-module>

# Bot not running?
tasklist | grep -a python
# or: wmic process where "name='python.exe'" get ProcessId,CommandLine

# Start bot
cd projects/<name> && .venv/Scripts/python.exe main.py
```

## Proxy (SOCKS5 for Telegram)

```bash
# Port open?
python -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1',10806)); print('OK'); s.close()"
# Timeout on Telegram API → proxy not working, not just port open
# Fix: restart VPN/proxy or remove proxy config if not needed
```

## Process Cleanup

```bash
# Find zombie processes
wmic process where "CommandLine like '%<keyword>%'" get ProcessId,CommandLine
# Kill: taskkill /PID <pid> /F
```
