# Session Bridge Pattern

**Date:** 2026-07-23  
**Umbrella skill:** closed-loop-autonomy

## Problem

Hermes sessions are stateless. Key decisions, commitments, and state
(principal identity, last EE sync, active goals, user preferences)
are reset every session. The system starts fresh every time, forgetting
what it learned between sessions.

## Solution: Session Bridge

A JSON file (`cache/session_bridge.json`) that persists between sessions.
Read at boot, written throughout and at end of every session.

**Key commitments:** corrections, preferences, architectural decisions
**Sync state:** last_ee_sync timestamp, KC count
**Proactivity state:** morning_proposal, last_user_voice_analysis
**Goal tracking:** active_goals summary

```python
from session_bridge import load_bridge, save_bridge, add_commitment

# Load at boot
bridge = load_bridge()  # returns dict

# Save state anytime
save_bridge({"last_ee_sync": datetime.now().isoformat()})

# Add a commitment (appended to key_commitments list)
add_commitment("Principal: Александр — владелец системы", category="identity")
```

## Files

- `scripts/session_bridge.py` — API: load_bridge(), save_bridge(), add_commitment()
- `cache/session_bridge.json` — Persistent store (auto-created)

## Integration Points

| Module | Read/Write | When |
|--------|-----------|------|
| `auto_boot_scan.py` | Read principal, sync state | Every session start |
| `morning_report.py` | Write morning_proposal | Every morning |
| `proactive_voice.py` | Write corrections/preferences | Every user message |
| `record_user_to_kc.py` | Write sync state | After EE sync |
| `self_improvement_loop.py` | Write metrics | After each run |

## Pitfalls

- **Stale bridge:** If `cache/session_bridge.json` is deleted, system reverts
  to defaults (principal=Александр, confirmed=False). Next session will
  auto-confirm via record_user_to_kc.py --sync.
- **Bridge != source of truth:** Bridge reflects state, it's not the DB.
  Always verify against KC/EE when freshness matters.
