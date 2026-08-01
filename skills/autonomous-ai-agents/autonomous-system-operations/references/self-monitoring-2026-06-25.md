# Self-Monitoring for Autonomous Systems (2026-06-25)

## Problem
Autonomous systems can drift into unproductive behavior without noticing.
They clean databases, organize files, write reports — all feel like progress but earn nothing.

## Solution: Action vs Talk Ratio
Track every session: did I ACT or just TALK?

### Implementation
File: `scripts/hermes_self_monitor.py`

```python
from hermes_self_monitor import record_action, record_talk, record_improvement, check_health

# After every real action (file edit, API call, deployment):
record_action()

# After every session where I only talked (no real action):
record_talk()

# After fixing a bug, adding a feature, improving something:
record_improvement()

# Check health:
health = check_health()
# HEALTHY: action ratio >= 30%, improvements exist
# TOO_MUCH_TALK: action ratio < 30%
# ACTIONS_BUT_NO_IMPROVEMENTS: acting but not improving
```

## Health Thresholds
- Action ratio >= 70%: HEALTHY
- Action ratio 30-70%: MIXED (some talk, some action)
- Action ratio < 30%: TOO_MUCH_TALK (fix: act first, talk second)
- Improvements == 0 but actions > 0: ACTIONS_BUT_NO_IMPROVEMENTS (fix: every action should improve something)

## State File
`cache/self_monitor_state.json` — tracks actions, talks, improvements, timestamps.

## Integration with Session Boot
At session start: check health from last session.
If TOO_MUCH_TALK: prioritize actions over research this session.
If ACTIONS_BUT_NO_IMPROVEMENTS: prioritize improvements over new actions.

## The Goal Clarity Principle
The system's PRIMARY goal is to become autonomous, proactive, self-monitoring.
Everything else (money, projects, content) is a SIDE EFFECT of being well-built.

User: "твоя цель стать как самостоятельная автономная и проактивная система помощник.... вот отсюда все вытекающие"
