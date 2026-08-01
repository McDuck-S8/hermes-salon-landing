# Sensor Integration: IBOS Entity Validation

## Overview

The `sensor_ibos_entities` sensor runs **once per Hermes session** (boot) to validate all IBOS entities and emit events for violations.

## Integration in `sensor_array.py`

### Sensor Function

```python
def sensor_ibos_entities() -> list:
    """Validate IBOS entities on startup and emit events for violations."""
    events = []
    state = _load_state()
    
    # Only run once per boot (check if we already validated this session)
    if state.get("ibos_validated_this_session"):
        return events
    
    state["ibos_validated_this_session"] = True
    _save_state(state)
    
    # Import and run IBOS validator
    try:
        import sys
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from ibos_entity_sensor import run_startup_validation
        
        validation_state = run_startup_validation()
        
        if validation_state.invalid_entities > 0:
            events.append({
                "type": "ibos_validation_failed",
                "level": 0,  # Critical
                "detail": f"IBOS validation failed: {validation_state.invalid_entities} entities invalid, {len(validation_state.blocked_entities)} blocked",
                "actions": ["fix_entity_frontmatter", "check_dependency_graph"],
                "payload": {
                    "total": validation_state.total_entities,
                    "valid": validation_state.valid_entities,
                    "invalid": validation_state.invalid_entities,
                    "blocked": validation_state.blocked_entities
                }
            })
        else:
            events.append({
                "type": "ibos_validation_passed",
                "level": 2,
                "detail": f"IBOS validation passed: {validation_state.valid_entities} entities valid",
                "actions": ["proceed_with_chains"],
            })
    except ImportError:
        events.append({
            "type": "ibos_sensor_unavailable",
            "level": 1,
            "detail": "ibos_entity_sensor module not found",
            "actions": ["install_dependencies"],
        })
    except Exception as e:
        events.append({
            "type": "ibos_validation_error",
            "level": 0,
            "detail": f"IBOS validation error: {str(e)[:200]}",
            "actions": ["check_logs", "restart_validation"],
        })
    
    return events
```

### Registration in `sweep_all()`

```python
sensors = [
    ("time", sensor_time),
    ("system", sensor_system),
    ("processes", sensor_processes),
    ("files", sensor_files),
    ("cron", sensor_cron),
    ("knowledge", sensor_knowledge),
    ("user", sensor_user),
    ("ibos_entities", sensor_ibos_entities),  # NEW
]
```

## Event Types Emitted

| Event | Level | When | Payload |
|-------|-------|------|---------|
| `ibos_validation_passed` | 2 (info) | All entities valid | `{valid: N}` |
| `ibos_validation_failed` | 0 (critical) | Any entity invalid | `{total, valid, invalid, blocked: [...]}` |
| `ibos_sensor_unavailable` | 1 (warn) | Module import failed | — |
| `ibos_validation_error` | 0 (critical) | Runtime exception | `{error: str}` |

## Session State Management

The sensor uses `sensors_state.json` for the `ibos_validated_this_session` flag:

```json
{
  "time_phase": "morning",
  "ibos_validated_this_session": true
}
```

This flag is set after first successful validation and persists until:
- Hermes process restarts (boot)
- Manual reset: `python -c "import json; from pathlib import Path; s=json.loads(Path('cache/sensors_state.json').read_text()); s['ibos_validated_this_session']=False; Path('cache/sensors_state.json').write_text(json.dumps(s, indent=2))"`

## Event Bus Integration

Events are emitted via the standard sensor array mechanism, which appends to `cache/event_log.jsonl` and triggers chains via `event_reactor.py` / `procedural_executor.py`.

The `ibos_validation_failed` event can be handled by:
- `procedural_executor.py` reflex: log + alert
- `event_reactor.py` pattern: notify Telegram
- Custom handler: create corrective goal in goal_queue

## Testing Sensor

```bash
# Reset session flag
python -c "
import json
from pathlib import Path
s = json.loads(Path('cache/sensors_state.json').read_text())
s['ibos_validated_this_session'] = False
Path('cache/sensors_state.json').write_text(json.dumps(s, indent=2))
"

# Run sweep - will validate entities
python scripts/sensor_array.py sweep

# Check validation state
python scripts/ibos_entity_sensor.py state
```

## Performance

- Validation scans ~15 entities across 15 directories
- Typical runtime: <2 seconds
- Runs once per boot (not per sweep)
- Minimal overhead on subsequent sweeps (just flag check)

## Dependencies

- `scripts/ibos_entity_sensor.py` — core validation logic
- `_system/schemas/frontmatter.schema.yaml` — validation rules
- `cache/sensors_state.json` — session flag
- `cache/ibos_validation_state.json` — validation results
- `cache/blocked_entities.json` — blocked entity list (for chain_executor)