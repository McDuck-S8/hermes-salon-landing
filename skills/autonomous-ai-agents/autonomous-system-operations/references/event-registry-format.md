# Event Registry Config Format

## config/event_registry.json structure

```json
{
  "_principles": ["list of immutable principles"],
  
  "L0_IMMEDIATE": {
    "event_type": {
      "name": "Human-readable name",
      "triggers": ["trigger1", "trigger2"],
      "agents": ["agent_name"],
      "actions": ["action1", "action2"]
    }
  },
  
  "L1_FAST": { ... },
  "L2_BACKGROUND": { ... },
  "L3_PERIODIC": { ... },
  
  "unknown_event": {
    "name": "Fallback",
    "agents": ["investigator"],
    "actions": ["log_unknown"]
  }
}
```

## Adding events via code

```python
from event_registry import learn_event
learn_event(
    event_type="new_salon_booking",
    triggers=["бронирование", "запись", "забронировал"],
    agents=["order_processor"],
    actions=["confirm_booking", "notify_salon"],
    level=1
)
# Saves to cache/learned_events.json, auto-merged on next load
```

## Adding events manually

Edit `config/event_registry.json` directly. Follow the level key format:
- `L0_IMMEDIATE` — safety, security, critical
- `L1_FAST` — operational, needs quick action
- `L2_BACKGROUND` — can wait, runs in background
- `L3_PERIODIC` — time-based, scheduled

## Detection logic

`detect_event(input_text)` does substring matching:
- For each event type, checks if any trigger substring is in the input
- Returns best match by confidence (longer trigger match = higher confidence)
- Falls back to `unknown_event` if no match

## Key rules

1. Events are DATA, not CODE. Never hardcode event types in Python.
2. Triggers should be BOTH Russian AND English for maximum coverage.
3. Each event needs: name, triggers, agents, actions.
4. Level determines reaction speed, not importance.
5. `learn_event()` adds to `cache/learned_events.json` (merged at load time).
