# Event-Driven Trigger Architecture

## Problem

Events are recorded in `events.db` when tasks complete, errors occur, skills
are used, sessions end, or user corrections happen. But no one processes them
in real-time. The system becomes a logger, not a learner.

## Solution: Tight-Loop Event Processing

Replace slow-polling (every 15m) with a tight loop (every 2m) that:
1. Checks for unprocessed events
2. If none → silent exit (no spam)
3. If events found → process them immediately (capture knowledge, run triggers)

## Implementation

### Script: `scripts/event_trigger.py`
```python
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from event_evolution import process_pending_events, get_engine

engine = get_engine()
unprocessed = engine.monitor.get_unprocessed()

if not unprocessed:
    sys.exit(0)  # Silent — nothing to report

print(f"[event-trigger] {len(unprocessed)} new event(s) detected")
result = process_pending_events()
print(f"[event-trigger] Processed {result['processed']}/{result['total']} events")
```

### Cron Registration
```
Name: event-trigger
Schedule: every 2m
Mode: no_agent=True
Script: event_trigger.py
```

## Architecture Layers

Layer 1: Event Trigger (every 2m, no_agent) → process_pending_events
Layer 2: System Watcher (every 60m, no_agent) → health checks
Layer 3: Unified Cycle (every 120m, no_agent) → knowledge cube, gaps

All layers use no_agent + script. No LLM dependency.

## Benefits vs 15-min Polling

| Aspect | 15m polling | 2m tight loop |
|---|---|---|
| Latency | 15 min max delay | 2 min max delay |
| Batch size | 15 min of events | 2 min of events |
| Cooldown bypass risk | Higher | Lower (near-real-time) |
| Load | Very low | Slightly higher, still trivial |

## Pitfalls

1. Cooldown bypass: should_trigger() compares datetime.now() vs last_triggered.
   In batch, all events fire triggers regardless of sequence. Tight loop (2m)
   minimizes this.
2. Stale DB connection: If events.db is locked, retry once then fail silently.
3. Scheduler ticks every ~60s. "every 2m" fires approximately every other tick.
   True sub-minute response needs a daemon process, not cron.
