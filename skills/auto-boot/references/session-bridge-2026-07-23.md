# Session Bridge — Cross-Session Persistence

**Created:** 2026-07-23  
**Files:** `scripts/session_bridge.py`, `cache/session_bridge.json`  
**Usage:** `python scripts/session_bridge.py commit "what"` / `python scripts/session_bridge.py show`

## Purpose
Key decisions must survive between sessions. Session bridge provides:
- Principal identity (who owns the system)
- Key commitments (decisions made, what was decided)
- Active goals from goal_queue
- EE sync timestamp

## Format
```json
{
  "principal_name": "Александр",
  "principal_confirmed": true,
  "last_ee_sync": "2026-07-23T14:55:02",
  "key_commitments": [
    {"text": "EE-KC sync every hour", "category": "general", "created": "..."}
  ],
  "active_goals": [{"id": "g-001", "title": "Cross-cube audit"}]
}
```

## Boot Integration
`auto_boot_scan.py` reads bridge at session start and checks:
1. Principal identity confirmed in EE
2. EE sync fresh (< 1 hour)
3. Key commitments still valid

## When to Save
- After implementing a task → `session_bridge.py commit "Implemented X"`
- After user gives instruction → `session_bridge.py commit "User wants Y"`
- At session end → save current goals and EE sync timestamp

## Anti-Pattern
Don't save EVERY message — only decisions and commitments. Save max 20 entries, oldest dropped.
