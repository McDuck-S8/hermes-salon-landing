# Window Spam from Cron Jobs — Quick Reference

## Problem
Multiple cron jobs with short intervals (1m, 2m, 5m) running inside the Hermes gateway as `no_agent: true` spawn separate Python subprocesses simultaneously → dozens of `python.exe` / `pythonw.exe` windows/processes.

## Root Cause
- Cron ticker runs inside gateway process (background thread, every 60s)
- Each `no_agent: true` job = separate subprocess via `subprocess.Popen`
- Short intervals overlap → burst of processes
- Gateway: `pythonw.exe` (PID 3376), Jobs: `python.exe`

## Architecture
```
gateway (pythonw.exe, PID 3376)
  └── InProcessCronScheduler (thread, every 60s)
        ├── event-heartbeat (every 2m)     → python.exe event_bus.py process
        ├── telegram-network-watchdog (1m) → python.exe network_watchdog.py
        ├── procedural-executor (5m)       → python.exe procedural_executor.py
        ├── memory-guard (10m)             → python.exe memory_guard.py
        ├── health-check (15m)             → python.exe health_check.py
        └── ... etc
```

## Immediate Fixes
| Job | Issue | Fix |
|-----|-------|-----|
| `event-heartbeat` | Missing `process` arg | `"script": "event_bus.py process"` |
| `procedural-executor` | `tasklist` hangs | Replace with `psutil` or `wmic` |
| `health-check` | Exfiltration false positive | Fix phone regex in `exfil_guard.py` |

## Stop the Spam
```bash
# Option 1: Pause specific jobs
hermes cron pause 2675f72f7ecb  # event-heartbeat
hermes cron pause b5e3c20e7f35  # procedural-executor
hermes cron pause 57aaf43b0b8a  # health-check

# Option 2: Increase intervals in cron/jobs.json directly
# "schedule": { "kind": "interval", "minutes": 5, "display": "every 5m" }
# → increase to 15m or 30m

# Option 3: Stop gateway (stops ALL cron)
hermes gateway stop
```

## Preventive
- Default new cron intervals to ≥15m unless event-driven
- Use `event_bus` + daemon for reactive triggers
- Set `deliver: "local"` to avoid chat spam
- Monitor `cron/output/` for errors