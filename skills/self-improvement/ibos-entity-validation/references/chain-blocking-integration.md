# Chain Execution Blocking Integration

## Overview

This document describes how IBOS entity validation blocks chain execution for invalid entities in Hermes.

## Integration Points

### 1. Chain Executor Pre-Check (`scripts/chain_executor.py`)

Added at the start of `run_chain_for_event()`:

```python
def run_chain_for_event(event_type: str, payload: dict = None) -> dict:
    """Полный путь: классификация → цепочка → результат."""
    
    # IBOS Validation: Check if the event payload references a blocked entity
    if payload:
        entity_id = payload.get("entity_id")
        if entity_id:
            try:
                sys.path.insert(0, str(HERMES_HOME / "scripts"))
                from ibos_entity_sensor import is_entity_blocked
                if is_entity_blocked(entity_id):
                    return {
                        "event_type": event_type,
                        "severity": "critical",
                        "confidence": 1.0,
                        "steps_run": 0,
                        "steps_succeeded": 0,
                        "blocked": True,
                        "reason": f"Entity {entity_id} is blocked due to IBOS validation failure",
                        "ts": datetime.now().isoformat(),
                    }
            except ImportError:
                pass  # IBOS sensor not available
    
    # ... normal chain execution
```

### 2. Event Payload Convention

For chain blocking to work, events that target entities must include `entity_id` in payload:

```python
# Example: emitting skill update event
event_bus.emit("skill_updated", {
    "entity_id": "crystal-core",  # REQUIRED for IBOS check
    "text": "Crystal core updated",
    "changes": ["module_added"]
})
```

### 3. Blocked Entity Response

When entity is blocked, chain executor returns:

```json
{
  "event_type": "skill_updated",
  "severity": "critical",
  "confidence": 1.0,
  "steps_run": 0,
  "steps_succeeded": 0,
  "blocked": true,
  "reason": "Entity test-blocked-chain is blocked due to IBOS validation failure",
  "ts": "2026-06-29T09:43:10.685650"
}
```

This prevents any chain steps from running and logs the blockage in `chain_log.json`.

## Event Types Requiring entity_id

| Event Type | Description | Required Payload |
|------------|-------------|------------------|
| `skill_updated` | Skill modified/created | `entity_id` (skill id) |
| `agent_updated` | Agent modified/created | `entity_id` (agent id) |
| `tool_updated` | Tool modified/created | `entity_id` (tool id) |
| `knowledge_updated` | Knowledge entry modified | `entity_id` (knowledge id) |
| `rule_updated` | Rule modified/created | `entity_id` (rule id) |
| `workflow_updated` | Workflow modified/created | `entity_id` (workflow id) |

## Testing Chain Blocking

```bash
# 1. Create invalid entity (canon + owner=agent)
cat > entities/skills/test-blocked.md << 'EOF'
---
id: test-blocked
type: skill
namespace: knowledge/test
status: canon
version: 1.0.0
owner: agent  # WRONG - canon requires operator
created: 2026-06-29T00:00:00Z
summary: Test blocked chain
description: Should block chain execution
---
EOF

# 2. Reset session validation flag
python -c "
import json
from pathlib import Path
s = json.loads(Path('cache/sensors_state.json').read_text())
s['ibos_validated_this_session'] = False
Path('cache/sensors_state.json').write_text(json.dumps(s, indent=2))
"

# 3. Run sweep to trigger validation
python scripts/sensor_array.py sweep

# 4. Test chain execution with blocked entity
python -c "
import sys
sys.path.insert(0, 'scripts')
from chain_executor import run_chain_for_event
result = run_chain_for_event('skill_updated', {'entity_id': 'test-blocked', 'text': 'test'})
import json
print(json.dumps(result, indent=2, ensure_ascii=False))
"

# Expected: blocked: true, steps_run: 0

# 5. Cleanup
rm entities/skills/test-blocked.md
```

## Files Involved

| File | Role |
|------|------|
| `scripts/chain_executor.py` | Pre-check in `run_chain_for_event()` |
| `scripts/ibos_entity_sensor.py` | `is_entity_blocked()` function |
| `cache/blocked_entities.json` | Blocked entities list |
| `cache/ibos_validation_state.json` | Validation state with blocked_entities |

## Verification

After implementation, verify:

1. Valid entity chain executes normally: `run_chain_for_event("skill_updated", {"entity_id": "crystal-core"})` → `steps_run > 0`
2. Blocked entity chain returns early: `run_chain_for_event("skill_updated", {"entity_id": "test-blocked"})` → `blocked: true, steps_run: 0`
3. Event bus receives `ibos_validation_failed` on sweep
4. `chain_log.json` logs blocked attempts with `blocked: true`