# Daemon Recovery Protocol — 2026-07-18

## Problem
All core Hermes daemons were dead:
- `signal_daemon` — PID dead, heartbeat 15h old
- `event_daemon` — PID dead
- `process_supervisor` — PID dead, managing 2 daemons
- Self-healing monitor running but reporting 0 alerts (false negative)

## Root Cause
The `process_supervisor` (which manages other daemons) was itself not running. No watchdog to restart the watchdog.

## Recovery Steps (via auto_recovery.py)

```bash
# Check status
python scripts/auto_recovery.py status

# Restart all daemons (required --daemon flag per daemon)
python scripts/auto_recovery.py restart --daemon signal_daemon
python scripts/auto_recovery.py restart --daemon event_daemon
python scripts/auto_recovery.py restart --daemon process_supervisor
```

## Verification
```bash
python scripts/auto_recovery.py status
# All three should show alive=true, healthy=true, heartbeat_age < 60s
```

## Self-Healing Monitor
```bash
python scripts/self_healing_monitor.py
# Should report: "49 jobs, 0 alerts" with actual health checks
```

## Key Scripts
| Script | Purpose |
|--------|---------|
| `scripts/auto_recovery.py` | Daemon health checks + restart hooks |
| `scripts/process_supervisor.py` | (Missing - referenced in skill but not in scripts/) |
| `scripts/signal_daemon.py` | Trend scanner with adaptive backoff |
| `scripts/event_daemon.py` | Event processing daemon |
| `scripts/self_healing_monitor.py` | Cron job health watcher |

## Pitfalls
1. **process_supervisor.py is referenced in auto_recovery.py but doesn't exist in scripts/** — it's under `skills/devops/process-supervisor/scripts/process_supervisor.py`. The recovery hook uses the correct path but if skills aren't loaded, it fails.
2. **No single "restart all" command** — must restart each daemon individually with `--daemon` flag.
3. **Self-healing monitor doesn't check daemon health** — only checks cron jobs. Daemon health is separate.
4. **Heartbeat age threshold is adaptive** — for signal_daemon, uses `backoff_interval * 3` from scanner_state.json. Don't hardcode 30s.

## Knowledge Cube Gap
- 4,244 total experiences
- 1,582 unprocessed (37%) — cube-categorizer cron not running effectively
- Self-improvement loop: 17,704 suggestions, 19 skills created (0.27% conversion)
- Error clusters: 275 in 48h — log noise overwhelming signal

## Fix Applied This Session
Restarted all three daemons via auto_recovery.py. Verified alive + healthy. Landing page verified live on GitHub Pages.