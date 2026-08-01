# event_beat vs emit_event — Two Event Systems

## The Confusion

Hermes has TWO separate event systems. They live in different modules, serve different purposes, and have different APIs. Confusing them causes ImportError or silent failures.

## System 1: chain_heartbeat.event_beat() — Health Monitoring

**Purpose**: Track whether each component/event fires within its expected interval. Powers the SILENT/HEALTHY/DEGRADED status display in `system_status()`.

**Module**: `chain_heartbeat`

**Signature**: `event_beat(event_name: str)`

**Effect**: Writes a timestamp + incremented counter to `cache/system_heartbeat.json`. Auto-clears alerts for that event on fire.

**Pipelines affected** (from PIPELINE_EVENTS mapping):
- `knowledge_added` → knowledge_pipeline
- `new_suggestions_ready` → self_improvement_pipeline
- `architecture_scan_complete` → none (no pipeline)

**When to call**: At data mutation points — right after knowledge is inserted, suggestions generated, architecture scanned. NOT by cron.

**Example call sites** (from `references/event-map.md`):
- `kc_rag.upsert()` calls `event_beat('knowledge_added')` internally
- `self_improvement_loop.main()` calls `event_beat('new_suggestions_ready')` after generating suggestions
- `architecture_model.py` calls `event_beat('architecture_scan_complete')` after scan

## System 2: event_evolution.emit_event() — Event Processing

**Purpose**: Write events to the events database for processing by EvolutionEngine (auto-fixes, pattern detection, skill evolution).

**Module**: `event_evolution`

**Signature**: `emit_event(event_name: str, data: dict)`

**Effect**: Inserts a row into EVENTS_DB. Later, `process_pending_events()` reads unprocessed rows and runs the auto-fix pipeline.

**When to call**: Any time a meaningful system event occurs that should trigger downstream processing (user corrections, task completions, errors).

## Example: What happened in this session

```python
# CORRECT — fires the heartbeat event (clears SILENT alert, updates health status)
from chain_heartbeat import event_beat
event_beat('new_suggestions_ready')

# ALSO correct — writes event for processing pipeline
# (if you need the event to trigger EvolutionEngine)
from event_evolution import emit_event
emit_event('new_suggestions_ready', {'source': 'auto_boot_scan', 'suggestions': 'skill audit done'})

# WRONG — event_evolution has no event_beat
from event_evolution import event_beat  # ImportError!
```

## Quick Reference

| Need | Module | Function | Args |
|------|--------|----------|------|
| Clear SILENT alert, update health | `chain_heartbeat` | `event_beat(name)` | `str` only |
| Process event through EvolutionEngine | `event_evolution` | `emit_event(name, data)` | `str, dict` |
| Register modules for heartbeat | `chain_heartbeat` | `register_all_modules()` | none |
| Full system health check | `chain_heartbeat` | `system_status()` | none |
| Print health table + return dict | `chain_heartbeat` | `self_check()` | none |
| Process pending events | `event_evolution` | `process_pending_events()` | none |
