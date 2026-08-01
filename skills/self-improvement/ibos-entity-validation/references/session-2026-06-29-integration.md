# IBOS Entity Validation — Session Notes & Reproduction

## Session: 2026-06-29 — Full Stack Integration

### Problem
Hermes had runtime execution (autonomous agent, event bus, chains) but lacked governance layer:
- No frontmatter schema for entities
- No validation on startup
- No blocking of chain execution for invalid entities
- No dependency graph for memory_guard

### Solution Implemented
Full IBOS (Infinite Brain OS) entity validation layer:

1. **Frontmatter Schema** — `_system/schemas/frontmatter.schema.yaml`
2. **Startup Validator** — `scripts/ibos_entity_sensor.py`
3. **Sensor Integration** — `sensor_ibos_entities` in `sensor_array.py`
4. **Chain Blocking** — `check_ibos_validation()` in `chain_executor.py`
5. **Dependency Graph** — `entity_dependency_graph.json` for memory_guard

### Validation Test Results

| Test | Command | Result |
|------|---------|--------|
| All valid | `python scripts/ibos_entity_sensor.py validate` | ✅ 15/15 valid |
| Invalid entity (canon+agent) | Add test entity → sweep | ✅ `ibos_validation_failed` emitted, 1 blocked |
| Chain blocked | `run_chain_for_event("skill_updated", {"entity_id": "test-blocked"})` | ✅ `blocked: true, steps_run: 0` |
| Chain allowed | `run_chain_for_event("skill_updated", {"entity_id": "crystal-core"})` | ✅ `steps_run: 1, analyze executed` |
| Cleanup | Remove test entity → sweep | ✅ `ibos_validation_passed` |

### Key Integration Points

```python
# sensor_array.py — runs once per session
if not state.get("ibos_validated_this_session"):
    validation_state = run_startup_validation()
    # emits ibos_validation_failed if violations

# chain_executor.py — pre-check before chain
entity_id = payload.get("entity_id")
if entity_id and is_entity_blocked(entity_id):
    return {"blocked": True, "steps_run": 0, "reason": "IBOS validation failure"}

# ibos_entity_sensor.py — validation logic
def is_entity_blocked(entity_id):
    if BLOCKED_ENTITIES_FILE.exists():
        blocked = json.loads(BLOCKED_ENTITIES_FILE.read_text())
        return entity_id in blocked
    return False
```

### Files Modified/Created

| File | Type | Lines |
|------|------|-------|
| `_system/schemas/frontmatter.schema.yaml` | Schema | 120 |
| `scripts/ibos_entity_sensor.py` | Validator | 400 |
| `scripts/sensor_array.py` | Sensor | +80 |
| `scripts/chain_executor.py` | Chain blocking | +50 |
| `scripts/validate_entities.py` | Legacy validator | 400 |
| 15 entity files | Canonical entities | ~300 |

### Verification Commands

```bash
# Full validation
python scripts/ibos_entity_sensor.py validate

# Show state
python scripts/ibos_entity_sensor.py state

# List blocked
python scripts/ibos_entity_sensor.py blocked

# Show deps
python scripts/ibos_entity_sensor.py deps crystal-core

# Test chain blocking
python -c "
import sys; sys.path.insert(0, 'scripts')
from chain_executor import run_chain_for_event
print(run_chain_for_event('skill_updated', {'entity_id': 'test-blocked', 'text': 'test'}))
"
```

### Integration with Existing Skills

| Skill | Integration |
|-------|-------------|
| `verification-gate` | IBOS validation IS a verification gate |
| `self-conscience` | Could call IBOS check before responses |
| `closed-loop-autonomy` | Validation signal → block action → emit event |
| `memory_guard` | Loads `entity_dependency_graph.json` |

### Next Steps (Phase 2-4)

1. **Namespace Registry** — `_system/namespaces/` with profiles
2. **Promotion Workflow** — support→synthesis→candidate→canon (operator approval)
3. **Session Ledger** — `sessions/active|logs|reviews|closed/`
4. **Sync Adapters** — `entities/` → `.hermes/skills/`, `.claude/commands/`
5. **Obsidian Compat** — `.obsidian/`, wikilinks, aliases
5. **Canon Governance** — Operator approval gate