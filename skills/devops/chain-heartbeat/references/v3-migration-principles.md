# Event Wiring Principles (v3 Migration)

## Core Rule

Events must fire at the **data mutation point**, not at a cron schedule or task-completion hook.

## Progression: v1 → v2 → v3

### v1 (original): Daemon polling
- Long-running processes that poll every N seconds
- `while True: time.sleep(5); check_status(); beat()`
- **Problem:** Wastes resources, misses events between polls

### v2 (previous): Cron-based heartbeat
- Scripts that run on schedule via cron, call `beat()` at end
- `cron(4:15) → cube_feeder.py → feed_entries() → beat()`
- **Problem:** Events only fire when cron runs. If cron is paused or scheduler skips — silence.

### v3 (current, 2026-07-19): Event-driven heartbeat
- Events fire at the exact function that mutates data
- `kc_rag.upsert() → INSERT → COMMIT → event_beat("knowledge_added")`
- **Benefit:** Event fires on EVERY data mutation, regardless of initiator

## Decision Matrix

| Approach | Event fires if... | Misses event when... |
|---|---|---|
| Daemon polling | Daemon is running | Daemon dies / interval too long |
| Cron-based | Cron fires on schedule | Cron is paused / scheduler skips |
| **Data-mutation (✓)** | **Data enters the system** | **— (always fires with data)** |

## Wiring Checklist

For each pipeline event:

- [ ] Identify the function where data ACTUALLY enters the system (DB insert, file write, API receive)
- [ ] Is there already an event emission at this point? (e.g., `eb_emit("knowledge_added")`)
- [ ] Wire `event_beat("event_name")` right after the data mutation, in the same try/except block
- [ ] Remove or deprecate cron-based event sources (leave cron for scheduling, not for event generation)
- [ ] Test: run the data-mutation function directly → event should appear in `system_status()`

## Current Wiring (2026-07-19)

| Event | Primary source | Fallback | Removed |
|---|---|---|---|
| `knowledge_added` | `kc_rag.upsert()` | `cube_feeder.feed_entries()` | `hooks.on_task_complete()` deprecated |
| `new_suggestions_ready` | `self_improvement_loop.main()` | `suggestion_consumer.consume()`, `self_system.run_analysis()` | N/A |
| `architecture_scan_complete` | `architecture_model.py` scan | — | N/A |
| `user_correction` | `hermes_hooks.on_user_correction()` | — | N/A |

## Why Not Daemons?

Daemons (long-running processes with `while True: ... time.sleep()`) are:
- Resource-heavy (always running, even when idle)
- Brittle (crash = silent death until watchdog notices)
- Against the event-driven architecture principle

**Instead:** Every event IS a heartbeat. If nothing is happening, nothing beats — and that's CORRECT.
