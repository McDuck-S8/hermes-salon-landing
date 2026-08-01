# Auto-Recovery — Verification Protocol

Run this script to verify all auto-recovery capabilities:

```bash
python scripts/auto_recovery.py check
python scripts/auto_recovery.py restart --daemon signal_daemon
python scripts/auto_recovery.py run &
# kill signal_daemon manually
# verify restart in < 20s
```

## Expected Results (2026-07-16)

| Test | Expected |
|------|----------|
| Fresh supervisor + auto_recovery | All 3 daemons healthy (alive=true, healthy=true) |
| Manual kill signal_daemon | Restarted in < 20s, new PID, healthy=true |
| Manual restart command | Works for all 3 daemons |
| Adaptive threshold | heartbeat_age=69s, backoff=60s → healthy (69 < 180) |
| State preservation | scanner total_signals preserved after recovery |

## Failure Modes to Watch

- PID file not written by supervisor → use `supervisor_state.json.supervisor_pid`
- Double restart (supervisor + auto_recovery) → increase auto_recovery check_interval
- signal_daemon heartbeat_age > 3×backoff_interval → unhealthy, triggers restart
- Rate limit exceeded (10 restarts/hour) → pauses, logs warning