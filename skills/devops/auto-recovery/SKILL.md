---
name: auto-recovery
category: devops
description: Autonomous daemon health monitoring and crash recovery with adaptive thresholds, rate limiting, and state preservation
version: 1.0.0
---

# Auto-Recovery — Autonomous Daemon Health & Crash Recovery

> Revisit: when daemon health checks, recovery policies, or rate limits change. Last touched: 2026-07-16.

Monitors Hermes daemons (signal_daemon, event_daemon, process_supervisor) continuously, restarts on failure with adaptive thresholds and exponential backoff.

## Architecture

```
scripts/auto_recovery.py
    ├── DaemonConfig (dataclass) — per-daemon policy
    ├── Health Checks — pluggable per daemon
    ├── Recovery Actions — full state reset + restart
    └── AutoRecoveryEngine — 15s monitoring loop
```

## Features

- **Adaptive thresholds** — signal_daemon uses scanner's `backoff_interval` × 3 (dynamic) instead of fixed 90s
- **Rate limiting** — max 10 restarts/hour per daemon, exponential backoff (5s, 10s, 30s, 60s, 300s)
- **State preservation** — preserves scanner `total_signals` on signal_daemon recovery
- **Process supervisor integration** — complements (not replaces) process_supervisor; longer check_interval avoids race
- **Alert callbacks** — JSONL log at `cache/auto_recovery.log` + console callbacks

## Daemon Registry

```python
DAEMON_REGISTRY = {
    "signal_daemon": DaemonConfig(
        script="scripts/signal_daemon.py",
        args=["run"],
        health_check_interval=30,
        health_check=check_signal_daemon_health,
        post_crash_hook=recover_signal_daemon,
    ),
    "event_daemon": DaemonConfig(
        script="scripts/event_daemon.py",
        args=["run"],
        health_check_interval=30,
        health_check=check_event_daemon_health,
        post_crash_hook=recover_event_daemon,
    ),
    "process_supervisor": DaemonConfig(
        script="skills/devops/process-supervisor/scripts/process_supervisor.py",
        args=["run"],
        health_check_interval=60,
        health_check=check_process_supervisor_health,
        post_crash_hook=recover_process_supervisor,
    ),
}
```

## Health Checks

| Daemon | Checks |
|--------|--------|
| signal_daemon | PID alive + heartbeat age < 3×backoff_interval + scanner_state.json valid |
| event_daemon | PID alive + heartbeat age < 90s |
| process_supervisor | PID alive + supervisor_state.json fresh + managed_daemons > 0 |

## Recovery Actions

| Daemon | Actions |
|--------|---------|
| signal_daemon | kill → clear PID → reset scanner_state (preserve total_signals) → restart |
| event_daemon | kill → clear PID → restart |
| process_supervisor | kill → clear PID → restart (writes new PID file) |

## Usage

```bash
# One-time health check
python scripts/auto_recovery.py check

# Continuous monitoring (background)
python scripts/auto_recovery.py run &

# Manual restart
python scripts/auto_recovery.py restart --daemon signal_daemon
python scripts/auto_recovery.py restart --daemon event_daemon
python scripts/auto_recovery.py restart --daemon process_supervisor
```

## Integration with Process Supervisor

| Aspect | process_supervisor | auto_recovery |
|--------|-------------------|---------------|
| Primary role | Daemon lifecycle manager | Health monitor + recovery |
| Check interval | 30s (configurable) | 15s (configurable) |
| Restart policy | Always/on_failure/never | Always/on_failure/never |
| Rate limit | Per-hour with backoff | Per-hour with backoff |
| State tracking | supervisor_state.json | DaemonStatus + auto_recovery.log |
| Windows Service | ✅ Native | ❌ Run via cron or supervisor |

**Recommended:** Run both. process_supervisor as Windows Service (primary), auto_recovery as cron job (secondary safety net with adaptive thresholds).

## Verified Tests (2026-07-16)

1. Fresh supervisor start → all 3 daemons healthy
2. Manual crash signal_daemon → auto-recovery restarts in ~15s, new PID, healthy
3. Manual restart command → works for all 3 daemons
4. Adaptive threshold: heartbeat_age 69s with backoff_interval=60s → healthy (69 < 180)
5. Crash recovery preserves scanner total_signals

## Files

- `scripts/auto_recovery.py` — main implementation (597 lines)
- `cache/auto_recovery.log` — JSONL alert log (generated at runtime)
- `cache/scanner_state.json` — read for adaptive threshold (signal_daemon)
- `cache/supervisor_state.json` — read for process_supervisor health

## Pitfalls & Workarounds

**Pitfall: signal_daemon "start" vs "run" args**
- `signal_daemon.py start` forks to background (parent exits immediately)
- `signal_daemon.py run` runs in foreground (suitable for subprocess.Popen with CREATE_NEW_PROCESS_GROUP)
- Recovery uses `run`; supervisor uses `run` — consistent.

**Pitfall: PID file not written by supervisor**
- process_supervisor doesn't create `process_supervisor.pid` itself
- Auto-recovery writes it after `Popen()` in `recover_process_supervisor()`
- Boot check should read `supervisor_state.json.supervisor_pid` + verify with psutil

**Pitfall: Race between supervisor and auto-recovery**
- Both monitor same daemons; can double-restart
- Mitigation: auto_recovery check_interval (15s) ≥ supervisor health_check_interval (10-30s)
- Or: disable auto-recovery for daemons supervisor manages, use only for independent daemons

**Pitfall: Windows taskkill locale**
- `tasklist /FI "PID eq X"` output uses cp1251; decode with `errors="replace"`
- Use psutil where available (cross-platform)