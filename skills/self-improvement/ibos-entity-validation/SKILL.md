---
name: ibos-entity-validation
description: IBOS (Infinite Brain OS) entity validation layer for Hermes — frontmatter schema, startup validator, sensor integration, and chain execution blocking for invalid entities.
tags:
  - validation
  - ibos
  - governance
  - entity-management
  - frontmatter
  - chain-blocking
---

# IBOS Entity Validation — Governance Layer for Hermes

Implements the Infinite Brain OS entity validation pattern on top of Hermes runtime. Provides:

- **Frontmatter Schema** — 11 entity types, 8 namespace profiles, lifecycle states (scratch→research→candidate→canon)
- **Startup Validator** — Scans all `entities/**/*.md` + `knowledge/**/*.md` on boot, validates against schema
- **Sensor Integration** — `sensor_ibos_entities` runs once per session, emits `ibos_validation_passed/failed`
- **Chain Blocking** — `chain_executor.py` checks `is_entity_blocked(entity_id)` before executing any chain
- **Dependency Graph** — Loads `depends_on` into `entity_dependency_graph.json` for `memory_guard`
- **Event Emission** — `ibos_validation_failed` event with blocked entity list for alerting

## Architecture

```
Hermes Boot
    │
    ▼
sensor_array.py:sweep_all()
    │
    ├── sensor_ibos_entities()  ──▶ ibos_entity_sensor.run_startup_validation()
    │       │
    │       ├── Scans 15+ entity directories
    │       ├── Validates frontmatter against _system/schemas/frontmatter.schema.yaml
    │       ├── Builds dependency graph from depends_on
    │       ├── Saves blocked_entities.json
    │       └── Emits ibos_validation_failed event if violations
    │
    ▼
event_bus.py receives ibos_validation_failed
    │
    ▼
chain_executor.py:run_chain_for_event()
    │
    ├── Extracts entity_id from payload
    ├── Calls ibos_entity_sensor.is_entity_blocked(entity_id)
    │
    ├── If BLOCKED ──▶ Returns {blocked: true, reason: "IBOS validation failure", steps_run: 0}
    │
    └── If ALLOWED ──▶ Proceeds with normal chain execution
```

## Files Created/Modified

| File | Role |
|------|------|
| `_system/schemas/frontmatter.schema.yaml` | Frontmatter contract (required keys, valid types, statuses, patterns) |
| `scripts/ibos_entity_sensor.py` | Core validator + CLI (`validate`, `state`, `blocked`, `deps <id>`) |
| `scripts/sensor_array.py` | Added `sensor_ibos_entities` + registered in `sweep_all()` |
| `scripts/chain_executor.py` | Added `check_ibos_validation()` + pre-check in `run_chain_for_event()` |
| `scripts/validate_entities.py` | Standalone validator (legacy, kept for CI) |

## Validation Rules (from schema)

| Rule | Severity |
|------|----------|
| Missing required keys (id, type, namespace, status, version, owner, created, summary, description) | ERROR |
| Invalid type (not in 11 types) | ERROR |
| Invalid status (not in scratch/research/candidate/canon/deprecated/archived) | ERROR |
| Invalid owner (not operator/agent) | ERROR |
| ID not kebab-case | ERROR |
| Namespace not kebab-case path | ERROR |
| Version not semver | ERROR |
| Created not ISO8601 | ERROR |
| Canon status with owner != operator | ERROR |
| Candidate missing promotes_from | WARNING |
| Self-promotion (promotes_to contains own id) | ERROR |
| Broken wikilinks [[...]] | WARNING |

## Lifecycle States

```
scratch (new, possibly wrong)
    │  agent validates, tests
    ▼
research (validated, worth refining)
    │  operator reviews
    ▼
candidate (nominated for canon)
    │  operator approves
    ▼
canon ──▶ operator-approved, immutable doctrine
    │
    ▼
deprecated / archived
```

**Canon Rule**: Agent CANNOT self-promote to canon. Only operator approval moves entity to canon.

## CLI Usage

```bash
# Run full validation (used by sensor on startup)
python scripts/ibos_entity_sensor.py validate

# Show last validation state
python scripts/ibos_entity_sensor.py state

# List blocked entities
python scripts/ibos_entity_sensor.py blocked

# Show dependencies for an entity
python scripts/ibos_entity_sensor.py deps crystal-core
```

## Integration Points

| Component | Integration |
|-----------|-------------|
| `sensor_array.py` | Runs once per session via `ibos_validated_this_session` flag |
| `event_bus.py` | Receives `ibos_validation_failed` for alerting |
| `chain_executor.py` | Pre-checks `is_entity_blocked(entity_id)` before chain |
| `memory_guard.py` | Loads `entity_dependency_graph.json` for context |
| `procedural_executor.py` | Could check before reflex chains (future) |

## Testing

```bash
# Create invalid entity (canon + owner=agent)
echo '---
id: test-invalid
type: skill
namespace: knowledge/test
status: canon
version: 1.0.0
owner: agent
created: 2026-06-29T00:00:00Z
summary: Test invalid
description: Should fail
---' > entities/skills/test-invalid.md

# Reset session flag
python -c "
import json; from pathlib import Path
s = json.loads(Path('cache/sensors_state.json').read_text())
s['ibos_validated_this_session'] = False
Path('cache/sensors_state.json').write_text(json.dumps(s, indent=2))
"

# Run sweep - should emit ibos_validation_failed with blocked entity
python scripts/sensor_array.py sweep

# Cleanup
rm entities/skills/test-invalid.md
```

## Verification Gate

This skill IS a verification gate. It prevents:
- Invalid frontmatter from propagating to Knowledge Cube
- Broken wikilinks from corrupting retrieval
- Canon violations (agent self-approval)
- Unversioned/untyped entities from entering system

**Run verification**: `python scripts/ibos_entity_sensor.py validate` — must return 0 errors before claiming "done".

## Related Skills

- `verification-gate` — General post-implementation verification pattern
- `self-conscience` — Pre-response conscience check (could call IBOS validation)
- `closed-loop-autonomy` — Ensures validation signal leads to action (blocking)

## Future Extensions

- [ ] Canon promotion workflow (operator approval gate)
- [ ] Namespace registry (`_system/namespaces/`)
- [ ] Sync adapters (`.hermes/skills/`, `.claude/commands/`)
- [ ] Session ledger integration (`sessions/active|logs|reviews|closed/`)
- [ ] Obsidian vault compatibility (`.obsidian/`, wikilink resolution)