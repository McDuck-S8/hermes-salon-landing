# Self-Monitor System (2026-06-25)

## Purpose
Track whether agent is ACTING or just TALKING. Prevents "report addiction" — talking about work instead of doing it.

## How It Works
- `record_action()` — call after every real action (file edit, API call, deployment)
- `record_talk()` — call when I only talked (no real action)
- `record_improvement()` — call when I improved something (fixed bug, added feature)
- `check_health()` — analyzes action ratio

## Health States
- `HEALTHY` — action ratio > 30%, improvements exist
- `TOO_MUCH_TALK` — action ratio < 30% (I talk too much, do too little)
- `ACTIONS_BUT_NO_IMPROVEMENTS` — I act but don't improve
- `NO_DATA` — no recorded actions yet

## File
`scripts/hermes_self_monitor.py`

## Usage
```python
from hermes_self_monitor import record_action, record_improvement, check_health

# After every real action
record_action()

# After every improvement
record_improvement()

# Check health
health = check_health()
if health == "TOO_MUCH_TALK":
    print("I talk too much, do too little. Fix: act first, talk second.")
```

## Rule
**Action ratio must be > 50%.** If I'm talking more than acting, I'm failing.

## Integration
- Call `record_action()` at end of every session
- Call `check_health()` at start of every session
- If health is not HEALTHY, adjust behavior immediately
