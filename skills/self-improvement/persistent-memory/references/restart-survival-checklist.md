# Restart Survival Checklist — 2026-06-29

## Problem
System works perfectly during session, breaks after restart. Root cause: processes run manually, not auto-started; wrong scripts called by cron; paths mismatched.

## Checklist (run after ANY restart)

### 1. MEMORY.md exists at ROOT?
```bash
test -f D:/Portable_Soft/hermes/MEMORY.md && echo "OK" || echo "MISSING — copy from memories/"
ls -la D:/Portable_Soft/hermes/memories/MEMORY.md  # should be symlink → root
```
If missing → `cp memories/MEMORY.md .` (symlink is safety net, but root file is canonical)
If symlink broken → `mklink D:\Portable_Soft\hermes\memories\MEMORY.md D:\Portable_Soft\hermes\MEMORY.md`

### 2. signal_daemon running?
```bash
python scripts/signal_daemon.py status
```
If dead → procedural_executor TRIGGER-010 restarts it (cron every 5 min)

### 3. event-heartbeat processing events?
Check `cache/event_bus.json` — pending count should be 0 after 2 min.
If stuck → hermes_heartbeat.py must call `event_bus.py process` (subprocess)

### 4. event_bus.py process not hanging?
`python scripts/event_bus.py process` should complete in <10s.
If >30s → session_recall import hanging. Threading timeout should catch it.

### 5. goal_executor not destroying queue?
Run: `python scripts/goal_executor.py --status`
If all goals show "failed" → NO_ACTION bug. Should be "skipped".

### 6. procedural_executor cron active?
```bash
# Check cron jobs.json for procedural-executor entry
python -c "import json; jobs=json.loads(open('cron/jobs.json').read())['jobs']; print([j['name'] for j in jobs if 'procedural' in j.get('name','')])"
```

### 7. Full health check?
```bash
python scripts/health_check.py  # Should be 10/10 OK
```

## Root Causes Found (2026-06-29)

| Issue | Cause | Fix |
|-------|-------|-----|
| MEMORY.md not found | memory_guard.py → memories/, Hermes reads root | Both point to root now |
| Events stuck forever | event-heartbeat calls hermes_heartbeat.py (no event processing) | hermes_heartbeat.py now calls event_bus.py process |
| event_bus hangs | session_recall indexes 5000 messages on import | Threading timeout 3s |
| All goals destroyed | NO_ACTION → failed | NO_ACTION → skipped |
| signal_daemon dead | No auto-restart, no watchdog | procedural_executor TRIGGER-010 |
| event_bus → no goals | DIRECT_EVENT_HANDLERS missing goal_executor | create_goal_from_event() added |
| IBOS self-heal "name 're' not defined" | procedural_executor.py missing `import re` and `import yaml` | Added both imports to procedural_executor.py |
| MEMORY.md empty after Crystal | Crystal wrote to memories/MEMORY.md, not root | Crystal paths fixed + symlink created |

## Key Pattern: What Breaks on Restart

Processes alive in memory die on restart. Cron jobs survive but may call wrong scripts. Files on disk survive but paths may be wrong. The gap between "working" and "works after restart" is:
1. Process auto-start (signal_daemon via procedural_executor)
2. Correct script references (event-heartbeat → event_bus.py process)
3. Correct file paths (MEMORY.md at root, not memories/)
4. Graceful error handling (threading timeouts, NO_ACTION → skipped)
