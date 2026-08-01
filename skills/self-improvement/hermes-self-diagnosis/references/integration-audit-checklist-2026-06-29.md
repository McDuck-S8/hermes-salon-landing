# Integration Audit — Post-Restart Checklist (2026-06-29)

When system worked yesterday but breaks after restart, check these 5 links IN ORDER:

## 1. Event Heartbeat → Event Bus
```bash
# Check: does cron job call event_bus.py process?
grep -A2 "event-heartbeat" cron/jobs.json
# WRONG: script = "hermes_heartbeat.py" (only health checks)
# RIGHT: hermes_heartbeat.py must call event_bus.py process via subprocess
```

## 2. Event Bus Process → Session Recall (timeout)
```bash
# Check: does event_bus.py process hang?
time python scripts/event_bus.py process
# If >30s: session_recall import hangs on indexing 5000 messages
# FIX: threading daemon + join(timeout=3) around slow imports
```

## 3. Event Bus → Goal Executor (pipeline)
```python
# Check: does DIRECT_EVENT_HANDLERS include goal creation?
grep "DIRECT_EVENT_HANDLERS" scripts/event_bus.py
# MISSING: event processed but no goal created
# FIX: add create_goal_from_event() in process_events()
```

## 4. Goal Executor → NO_ACTION handling
```python
# Check: what happens to goals without action_command?
grep "NO_ACTION\|failed\|skipped" scripts/goal_executor.py
# BUG: NO_ACTION → status='failed' destroys entire queue
# FIX: NO_ACTION → status='skipped'
```

## 5. Daemon Watchdog
```bash
# Check: is signal_daemon running?
cat cache/signal_daemon.pid
python -c "import os; print(os.kill(int(open('cache/signal_daemon.pid').read()), 0))"
# If dead: procedural_executor must auto-restart
# CHECK: grep "signal_daemon" scripts/procedural_executor.py
```

## Quick Verification (all 5 at once)
```bash
# 1. Pending events
python -c "import json; d=json.load(open('cache/event_bus.json')); print(f'Pending: {len(d.get(\"pending\",[]))}')"

# 2. Event bus process time
time python scripts/event_bus.py process

# 3. Goals created from events
python -c "import json; goals=json.load(open('cache/goal_queue.json'))['goals']; print(f'Goals: {len(goals)}')"

# 4. Signal daemon alive
cat cache/scanner_state.json | python -c "import json,sys; d=json.load(sys.stdin); print(f'Last scan: {d.get(\"last_scan\",\"never\")}')"

# 5. Procedural executor health
python scripts/procedural_executor.py --status 2>&1 | head -20
```

## Root Cause Pattern
All 5 bugs share ONE root cause: **processes were launched manually and lived in memory.
After restart, nobody relaunched them. Automation (cron/daemon) was broken or missing.**

Fix: ensure EVERY critical process either:
- Runs as a persistent daemon with watchdog (signal_daemon)
- Gets triggered by cron every 2-5 minutes (event-heartbeat, procedural-executor)
- Is called from within another running process (hermes_heartbeat → event_bus)
