# Ring of Rules (Кольцо правил)

## Core Principle

Three rules locked in a closed loop. Breaking any one breaks all three.

```
Event (E) → Action (3) → Artifact (0) → new Event (E)
   ↑           ↑             ↑
   E           3             0
```

## The Rules

### Rule 0 — Zero Artifact
"Сказал = сделал" → show the artifact. No artifact = lie.

### Rule 3 — Three Steps
Understanding → Action → Artifact. Skipping any step breaks the ring.

### Rule E — Events
Action follows event, not alarm clock. Never create cron jobs for reactions — only `emit_event()`.

## Violation Cascade

If Rule E broken (cron instead of event):
→ Action never fires → Rule 3 broken → No artifact → Rule 0 broken → Ring broken

If Rule 3 broken (understood but didn't act):
→ No artifact → Rule 0 broken → No new event created → Rule E broken → Ring broken

If Rule 0 broken (lied about artifact):
→ No artifact → No event from real result → Rule E broken → No action → Rule 3 broken → Ring broken

## Anti-patterns vs Event-driven

| Anti-pattern (cron/timer) | Event-driven replacement |
|---|---|
| "Check health every 5 min" | `module_down` → emit_event → immediate reaction |
| "Scan RSS every hour" | `new_rss_item` → emit_event → process |
| "Clean logs daily" | `log_threshold_exceeded` → emit_event → cleanup |
| "Fix skills every 2h" | `skill_issues_detected` → emit_event → remediation |
| "Research URLs every 6h" | `research_urls_provided` → emit_event → research |
| "Recover service every 30m" | `service_down` → emit_event → recovery |

## How to implement

### 1. Define an event type
Choose a descriptive name: `service_down`, `skill_issues_detected`, `research_urls_provided`

### 2. Register a trigger (event_type → action)
```python
conn = sqlite3.connect(str(EVENTS_DB))
conn.execute(
    "INSERT INTO triggers (event_type, action, cooldown_hours) VALUES (?, ?, ?)",
    ("service_down", "recover_service", 0)  # 0 = immediate
)
conn.commit()
```

### 3. Register a handler (action → callback)
```python
# In scripts/event_handlers.py:
def register_handlers(engine):
    engine.register_handler("recover_service", on_service_down)

def on_service_down(action, event):
    service = event.data.get("service", "unknown")
    # ... handle ...
```

### 4. Emit the event
```python
from event_evolution import emit_event
emit_event("service_down", {"service": "browseros", "module": "external"}, priority=1)
```

## Verification

- [ ] No cron jobs exist for reactive tasks (health checks, research, recovery, polling)
- [ ] Every action has a corresponding event that triggers it
- [ ] Events fire at DATA MUTATION POINTS, not at timer intervals
- [ ] Process the event queue via `process_pending_events()` on session start
- [ ] The event_trigger.py (every 2m) picks up events autonomously
