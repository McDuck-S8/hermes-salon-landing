---
name: hermes-entity-governance
category: devops
description: "Class-level skill for managing Hermes entities with IBOS-compliant governance: validation, blocking, self-healing, cascade revalidation, and unblocking."
version: "1.0.0"
tags:
  - hermes
  - ibos
  - validation
  - self-healing
  - cascade-revalidation
  - entity-governance
---

# Hermes Entity Governance — IBOS Validation, Self-Healing & Cascade Revalidation

**Class-level skill** for managing the full lifecycle of Hermes entities (skills, agents, tools, knowledge, etc.) with IBOS-compliant governance: validation → blocking → self-healing → cascade revalidation → unblocking.

## Architecture Overview

```
SENSOR → VALIDATION → SELF-HEAL → CASCADE REVALIDATION → UNBLOCK
  │           │            │              │             │
  ▼           ▼            ▼              ▼             ▼
entities/*  ibos_       trigger_      cascade_      proceed
ibos_       validation  ibos_self_    revalidate    with
entities    failed      heal (15min)  dependent     chains
```

## Components

| Component | File | Role |
|-----------|------|------|
| Schema | `_system/schemas/frontmatter.schema.yaml` | 11 entity types, 12 validation rules, 8 namespace profiles |
| Validator | `scripts/ibos_entity_sensor.py` | Scans all entities, validates frontmatter, builds dependency graph, blocks invalid |
| Self-Heal | `scripts/procedural_executor.py::trigger_ibos_self_heal` | TRIGGER-009: Auto-fixes 6 common frontmatter issues |
| Cascade Reval | `scripts/procedural_executor.py::cascade_revalidate` | Re-validates transitive dependents, unblocks if valid |
| Sensor | `scripts/sensor_array.py::sensor_ibos_entities` | Runs once per boot, emits `ibos_validation_failed`/`passed` |
| Chain Block | `scripts/chain_executor.py::run_chain_for_event` | Checks `blocked_entities` before executing chains |

## 6 Auto-Fix Rules (Self-Healing)

| Rule | Trigger | Fix |
|------|---------|-----|
| 1. Missing required keys | `summary`, `version`, `status`, `owner`, `created`, `type`, `namespace`, `id`, `description` | Auto-generates from description/body/directory |
| 2. Invalid status | Not in `scratch|research|candidate|canon|deprecated|archived` | → `scratch` |
| 3. Invalid type | Not in 11 valid types | → `skill` |
| 4. Invalid owner | Not `operator|agent` | → `agent` |
| 5. Canon with non-operator | `status: canon` + `owner != operator` | `status: candidate` |
| 6. Invalid confidence | Outside `[0.0, 1.0]` | → `0.5` |

## Cascade Revalidation Algorithm

```python
def cascade_revalidate(fixed_entity_id, validation_data):
    # 1. Build reverse dependency map from dependency_graph
    reverse_deps = build_reverse_map(validation_data["dependency_graph"])
    
    # 2. Find ALL transitive dependents (DFS)
    dependents = set()
    to_check = [fixed_entity_id]
    while to_check:
        current = to_check.pop()
        for dep in reverse_deps.get(current, []):
            if dep not in dependents:
                dependents.add(dep)
                to_check.append(dep)
    
    # 3. Re-validate each dependent
    for dep_id in dependents:
        if revalidate_entity(dep_id):
            unblock_entity(dep_id)
```

## Integration Points

| System | Integration |
|--------|-------------|
| Boot | `sensor_ibos_entities` runs once per session via `sensor_array.py` |
| Event Bus | Emits `ibos_validation_failed` (level 0) / `ibos_validation_passed` |
| Procedural Executor | TRIGGER-009 runs every 15 min via `check_all_triggers()` |
| Chain Executor | `run_chain_for_event` checks `blocked_entities` before execution |
| Memory Guard | Uses `entity_dependency_graph.json` for dependency awareness |

## Event Types

| Event | Level | Payload | Action |
|-------|-------|---------|--------|
| `ibos_validation_failed` | 0 (critical) | `{total, valid, invalid, blocked: [...]}` | Triggers self-heal |
| `ibos_validation_passed` | 2 | `{valid: N}` | Proceed with chains |
| `ibos_entity_blocked` | 0 | `{entity_id, reason}` | Logs blocking |
| `ibos_self_heal` | 2 | `{fixed: N, failed: M}` | Logs repair |
| `cascade_revalidate` | 2 | `{unblocked: [...], fixed_entity: X}` | Logs cascade |

## CLI Commands

```bash
# Full validation
python scripts/ibos_entity_sensor.py validate

# Self-heal trigger
python scripts/procedural_executor.py --run ibos_heal

# Check validation state
python -c "import json; print(json.load(open('cache/ibos_validation_state.json'))['blocked_entities'])"

# Show dependency graph
python -c "import json; print(json.load(open('cache/ibos_validation_state.json'))['dependency_graph'])"
```

## Files Created/Modified This Session

| File | Purpose |
|------|---------|
| `_system/schemas/frontmatter.schema.yaml` | IBOS frontmatter contract |
| `scripts/ibos_entity_sensor.py` | Main validator + cascade function |
| `scripts/procedural_executor.py` | TRIGGER-009 + cascade_revalidate |
| `scripts/sensor_array.py` | `sensor_ibos_entities` integration |
| `scripts/chain_executor.py` | Chain blocking via `check_ibos_validation` |
| `scripts/validate_entities.py` | Standalone validator CLI |

## Test Results (This Session)

| Scenario | Result |
|----------|--------|
| Valid entities (15) | ✅ `ibos_validation_passed` |
| Invalid entity: `status: canon` + `owner: agent` | ❌ Blocked → `ibos_validation_failed` |
| Self-heal runs | ✅ Auto-fixes: `canon` → `candidate` |
| Re-validation | ✅ `ibos_validation_passed: 17 entities valid` |
| Cascade: `test-dependent` depends on `test-base-entity` | ✅ Unblocked after base fixed |
| Chain execution blocked for invalid | ✅ `blocked: true` returned |
| Chain execution allowed for valid | ✅ Normal execution |

## Pitfalls & Lessons

1. **YAML datetime serialization** - `yaml.dump()` converts datetime to string, but `json.dumps()` fails. Use `default=str` when saving validation state.

2. **Validation session flag** - `sensor_ibos_entities` uses `ibos_validated_this_session` in `sensors_state.json` to run once per boot. Reset for testing: `sensors_state.json['ibos_validated_this_session'] = False`

3. **Reverse dependency traversal** - Must use DFS/BFS to catch transitive dependents (A→B→C means fixing A requires re-validating B AND C).

4. **Frontmatter parsing** - Always split on `---` with regex `^---\s*\n` to handle multiline frontmatter correctly.

5. **Entity file location** - Some entities may not be in expected directories; fallback to scanning all `ENTITY_DIRS`.

6. **Missing imports in procedural_executor.py (2026-06-29).** `trigger_ibos_self_heal()` uses `re.search()` and `yaml.safe_load()` but `procedural_executor.py` did not import `re` or `yaml` at the top. This caused "name 're' is not defined" errors in every self-heal attempt (6+ failures logged in feedback_store). **Fix:** Added `import re` and `try: import yaml / except ImportError: yaml = None` to the imports section. Always verify that functions using stdlib modules have the corresponding imports at the module level.

## Related Skills

- `self-improvement` - Crystal self-learning loop
- `procedural-logic` - Deterministic reflex chains
- `devops/cron-maintenance` - Cron job health monitoring
- `agent-browser` - Web surfing for external knowledge