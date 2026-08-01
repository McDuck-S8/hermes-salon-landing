# Ripple Consumer Pattern (2026-07-23)

**Alternative to event_bus DIRECT_EVENT_HANDLERS.** Simpler, no registration step.

## When to use this pattern

When you need a lightweight event consumer that:
- Is called directly from event sources (no event bus)
- Accumulates events before triggering (threshold-based)
- Runs a subprocess as the handler
- Creates goals from generated results

## Pattern

```python
# ripple_consumer.py
import json, subprocess
from pathlib import Path

THRESHOLD = 3
TRIGGER_FILE = Path("cache/ripple_trigger.json")

def on_knowledge_added(count=1):
    data = _load_trigger()
    data["pending_count"] = data.get("pending_count", 0) + count
    if data["pending_count"] >= THRESHOLD:
        return _generate()
    else:
        _save(data)
        return {"generated": False, "pending": f"{data['pending_count']}/{THRESHOLD}"}

def on_suggestions_ready():
    return _generate()

def _generate():
    result = subprocess.run([sys.executable, "scripts/handler.py"], ...)
    
    # Convert proposal to goal (closed loop)
    if result.returncode == 0:
        cache_path = Path("cache/latest_morning_report.json")
        if cache_path.exists():
            cache = json.loads(cache_path.read_text())
            if cache.get("top_proposal"):
                from goal_queue import create_goal
                goal_id = create_goal(
                    title=f"Unlock: {cache['top_proposal']['label']}",
                    tier=2, priority=5,
                )
    
    _save({"pending_count": 0, "last_generated": now})
    return {"generated": True}

def _load_trigger(): ...
def _save_trigger(data): ...
```

## Call site (in the event source)

```python
# kc_rag.py: after event_beat("knowledge_added")
try:
    from ripple_consumer import on_knowledge_added
    on_knowledge_added()
except ImportError:
    pass
```

## Extended Integration

The ripple consumer also beats heartbeats after generation and creates goals:

```python
# Inside _generate(), after successful handler run:
from chain_heartbeat import event_beat
event_beat("new_suggestions_ready")
event_beat("knowledge_added")

# Convert proposal to goal
if cache.get("top_proposal"):
    goal_id = create_goal(
        title=f"Unlock: {cache['top_proposal']['label']}",
        tier=2, priority=5,
        description=f"Morning report top proposal: {label} (maturity={maturity:.0%})",
        done_when=[f"Explored {label} in KC", f"Generated report for {label}"],
    )
```

## Advantages over event_bus DIRECT_EVENT_HANDLERS

1. No registration step needed
2. No timeout on handlers (subprocess handles timeout separately)
3. Threshold accumulation built-in
4. Import-and-call — zero ceremony
5. Graceful fallback if module not installed (ImportError caught)
6. Can create goals from handler output (closed loop)
