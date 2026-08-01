# Health Check Script — System Verification
# Created: 2026-06-29
# Purpose: Verify all critical files and processes exist
# Location: scripts/health_check.py
# Cron: runs every 15 minutes via health-check cron job

## What It Checks

1. MEMORY.md exists at root
2. knowledge_cube.db exists
3. goal_queue.json exists
4. event_bus.json exists
5. signal_daemon alive (via PID file + tasklist on Windows)
6. scanner_state.json exists
7. knowledge_cube.db has data (experiences table)
8. scorer_history.json exists
9. memory_guard.py points to correct path
10. hermes_heartbeat.py calls event_bus.py process

## Usage

```bash
python scripts/health_check.py          # Full check, prints ✅/❌ for each
python scripts/health_check.py 2>&1     # Capture for logging
```

## Output Format

```
  ✅ MEMORY.md exists
  ✅ knowledge_cube.db
  ✅ goal_queue.json
  ✅ event_bus.json
  ✅ signal_daemon alive
  ✅ scanner_state.json
  ✅ knowledge_cube.db entries — 1147 entries
  ✅ scorer_history.json
  ✅ memory_guard.py path
  ✅ hermes_heartbeat → event_bus

  === HEALTH: 10/10 OK, 0 FAIL ===
  🟢 System healthy
```

## Cron Job

- Name: `health-check`
- Schedule: every 15m
- Type: no_agent (script-only, no LLM)
- Script: `scripts/health_check.py`

## Adding New Checks

Add a new `check("name", condition, "detail")` call in the script.
Return True for OK, False for FAIL.
