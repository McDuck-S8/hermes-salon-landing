---
name: process-supervisor
category: devops
description: Immortal daemon manager for Hermes - survives session kills, crashes, reboots
version: 1.0.0
---

# Process Supervisor — Immortal Daemon Manager

> Revisit: when supervisor config, restart policies, or health checks change. Last touched: 2026-07-03.

Manages Hermes daemons as immortal processes. Survives session kills, crashes, reboots.

## Architecture

```
process_supervisor.py (runs as Windows Service / background)
    ├── signal_daemon.py (PID tracked, auto-restart)
    ├── event_daemon.py (PID tracked, auto-restart)
    └── health_monitor.py (checks every 30s, emits events)
```

## Features

- **PID tracking** in `cache/supervisor_state.json`
- **Auto-restart** on crash (exponential backoff: 5s, 10s, 30s, 60s, max 5min)
- **Health checks** every 30s (process alive + heartbeat recent)
- **Graceful shutdown** on SIGTERM / Ctrl+C
- **Windows Service** installation via `nssm` or native `winsvc`
- **Event emission** on daemon death/restart → `event_bus.py`

## Config

```yaml
supervisor:
  daemons:
    - name: signal_daemon
      script: scripts/signal_daemon.py
      args: ["run"]
      restart_policy: always
      health_check_interval: 30
    - name: event_daemon
      script: scripts/event_daemon.py
      args: ["run"]
      restart_policy: always
      health_check_interval: 30
  backoff: [5, 10, 30, 60, 300]  # seconds
  max_restarts_per_hour: 10
```

## Usage

```bash
# Run in foreground (for testing)
python scripts/process_supervisor.py run

# Install as Windows Service (requires admin)
python scripts/process_supervisor.py install

# Start/stop service
python scripts/process_supervisor.py start
python scripts/process_supervisor.py stop

# Status
python scripts/process_supervisor.py status
```

## State File

`cache/supervisor_state.json`:
```json
{
  "daemons": {
    "signal_daemon": {
      "pid": 12345,
      "status": "running",
      "restart_count": 0,
      "last_start": "2026-07-03T10:00:00",
      "last_health_check": "2026-07-03T10:05:00",
      "backoff_index": 0
    }
  },
  "supervisor_pid": 99999,
  "started_at": "2026-07-03T10:00:00"
}
```

## Known Issues & Workarounds

**Pitfall: SIGBREAK on Windows — daemon ignores supervisor stop**  
The supervisor sends `CTRL_BREAK_EVENT` (Win32) which maps to `signal.SIGBREAK`. If the daemon only handles `SIGTERM`/`SIGINT`, the signal is silently ignored and `stop()` falls through to `process.kill()` after timeout.

**Fix:** Every daemon managed by supervisor must register `signal.SIGBREAK`:
```python
import signal
signal.signal(signal.SIGTERM, lambda *_: setattr(self, 'running', False))
signal.signal(signal.SIGINT,  lambda *_: setattr(self, 'running', False))
if hasattr(signal, 'SIGBREAK'):
    signal.signal(signal.SIGBREAK, lambda *_: setattr(self, 'running', False))
```

**Detection:** After `supervisor status` shows a daemon running but `daemon.py --status` shows a different PID — the original daemon wasn't killed on restart and a duplicate was spawned. Run `tasklist /FI "IMAGENAME eq python.exe"` and compare PIDs.

**Pitfall: Windows — os.kill/POSIX signals not supported**
On Windows, os.kill(pid, signal.SIGTERM) raises OSError WinError 87. Use taskkill /F /PID and tasklist /FI with cp1251 locale decode. See auto-boot skill's windows-process-management.md.

**Pitfall: is_process_alive() — os.kill(pid, 0) also fails on Windows**
The signal 0 fallback raises the same WinError 87. Patched 2026-07-10 in process_supervisor.py to use tasklist before signal 0.

**Alternative: Light watchdog pattern (no supervisor needed)**
For simple daemons, use a cron-based watchdog:
1. Write a small watchdog.py that checks tasklist and restarts via subprocess.Popen if dead
2. Create a cronjob(no_agent=True, script='watchdog.py') running every 10-15m
3. Use CREATE_NO_WINDOW flag on Windows
4. Track PID via a simple .pid file in cache/
Example: scripts/bot_watchdog.py keeps cpa_telegram_bot.py alive under cron every 10m.

**Pitfall: Supervisor doesn't write its own PID file**
- The supervisor tracks child daemon PIDs but doesn't create `process_supervisor.pid` itself
- Boot reconciliation's `is_process_running("process_supervisor")` checks for this file → false negative
- Workaround: Check `supervisor_state.json` for `supervisor_pid` + verify with `psutil` instead of PID file
- Fix needed: Add PID file write in `run_foreground()` before entering main loop

**Pitfall: Race condition in boot final check**
- Supervisor starts child daemons asynchronously
- Boot's final compliance check runs before supervisor state is fully written
- Workaround: Add 2-3 second delay after `start_process_supervisor` repair before final check, or poll `supervisor_state.json` until daemons show `status: "running"`

**Pitfall: Supervisor + Auto-Recovery dual monitoring**
- Both process_supervisor and auto_recovery.py monitor the same daemons
- Can cause double-restart if both detect failure simultaneously
- Solution: Use single source of truth — process_supervisor as primary, auto_recovery as secondary with longer check_interval (30s vs 10s)
- Config: auto_recovery's check_interval should be >= process_supervisor's health_check_interval to avoid race

**Integration: Auto-Recovery Engine**
- `scripts/auto_recovery.py` provides complementary monitoring with adaptive thresholds
- Uses scanner's `backoff_interval` for signal_daemon heartbeat tolerance (dynamic vs fixed)
- Rate limiting: max 10 restarts/hour with exponential backoff
- State preservation: preserves scanner `total_signals` on signal_daemon recovery
- CLI: `python scripts/auto_recovery.py check|run|restart --daemon <name>`
- Runs independently of supervisor; can be added as supervisor-managed daemon itself