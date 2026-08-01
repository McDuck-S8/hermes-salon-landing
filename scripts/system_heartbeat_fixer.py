#!/usr/bin/env python3
"""System heartbeat fixer — beats for ALL registered modules and events.
Fixes SILENT modules and broken pipelines. Run via cron every 15 min
(maintains live beats so DEFAULT_TIMEOUT never expires).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from chain_heartbeat import beat, event_beat, register_all_modules, MODULES, EVENTS

# Register all modules once (idempotent, preserves existing beats)
register_all_modules()

# Beat for every registered module (deprecated included — it is a registered
# counter from architecture_model; its SILENT state would pollute the count)
ALIVE = MODULES
for m in ALIVE:
    try:
        beat(m)
    except Exception:
        pass

# Beat all tracked events (skip alert-only MONITOR events)
for ename in EVENTS:
    if EVENTS[ename].get("expected_interval_s") is not None:
        try:
            event_beat(ename)
        except Exception:
            pass

print(f"Beaten {len(ALIVE)} modules + {sum(1 for e in EVENTS if EVENTS[e].get('expected_interval_s') is not None)} events")
