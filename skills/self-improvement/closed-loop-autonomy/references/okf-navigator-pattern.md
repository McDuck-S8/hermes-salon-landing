# OKF Navigator — Event-Driven Domain Maturity Monitor

## Class

**Closed-loop autonomy** (Pipeline + User-facing): `kc_rag.upsert()` (producer) → `event_bus.emit("knowledge_added")` → `okf_navigator` (consumer) → `bd create` (user-facing task).

## Architecture

```
upsert(content, tags, source, category)
  │
  ├── writes to SQLite kc_entries
  ├── writes .md to OKF bundle (knowledge/okf/)
  └── event_bus.emit("knowledge_added", {domain, confidence, source, ...})
        │
        └── DIRECT_EVENT_HANDLERS["knowledge_added"]
              │
              └── okf_navigator.on_knowledge_added(event)
                    │
                    ├── analyze_domain(domain)
                    │     ├── avg confidence > 0.7 AND verified ≥ 3 → READY
                    │     └── expired ≥ 50% → NEEDS_RECHECK
                    │
                    └── create_beads_task(title, desc)
                          └── node bd.js create → beads issue
```

## Key Files

- `scripts/okf_navigator.py` — handler + registration
- `scripts/event_bus.py` — DIRECT_EVENT_HANDLERS dispatch
- `scripts/kc_rag.py` — emit("knowledge_added") in upsert()

## Registration

```python
from scripts import event_bus, okf_navigator

# At boot:
event_bus.DIRECT_EVENT_HANDLERS.setdefault("knowledge_added", [])
DIRECT_EVENT_HANDLERS["knowledge_added"].append(okf_navigator.on_knowledge_added)

# Or use the navigator's self-register:
okf_navigator.register()
```

The navigator uses `event_bus.DIRECT_EVENT_HANDLERS.setdefault()` pattern — register once, survive re-import.

## Domain Analysis Logic

```python
def analyze_domain(domain: str) -> dict:
    # Queries both kc_entries (by category) and experiences (by axis_domain)
    # Returns: total, avg_confidence, verified_offers, expired_count, expired_pct
    #          ready (bool), needs_recheck (bool)
    #
    # Maturity threshold: avg_confidence > 0.7 AND verified_offers >= 3
    # Expiration threshold: expired_pct >= 50%
```

## Cooldown

Uses a cooldown FILE (not timer, not memory) to avoid re-analysing the same domain within 6 hours. Cooldown is per-domain, survives restarts.

## Beads Task Creation

On Windows, `bd` is a bash script that calls node. Subprocess routing:

```
WRONG:  subprocess.run(["bash", "/d/.../bd", "create", ...])  # fails on Windows
RIGHT:  subprocess.run(["node", "D:/npm-global/.../bd.js", "create", ...])
```

## Edge Cases Handled

- **`sqlite3.Row`**: `.get()` not available → use `row["col"]` with `keys()` guard
- **Empty domain**: 0 concepts → skip (nothing to do)
- **Domain not in event payload**: skip (graceful degradation)
- **DB locked**: error logged, process continues (non-critical)
- **Event bus not available**: fallback to `emit_event.emit()` (file-only queue)

## When to Replicate This Pattern

- Any `upsert()` that should trigger downstream analysis
- Any domain/knowledge monitoring that should be event-driven (not cron)
- Any system that needs "if data mature → create task" logic
