---
name: entity-governance
category: self-improvement
description: Validation, blocking & self-healing for typed entity lifecycles (skills, agents, tools, knowledge, etc.)
version: 1.0.0
tags:
  - validation
  - schema
  - frontmatter
  - self-healing
  - governance
  - ibos
  - procedural
  - chain-blocking
---

# Entity Governance — Validation, Blocking & Self-Healing

**Class-level skill** for managing entity lifecycles with governance: schema validation, event-driven failure handling, chain blocking, and procedural self-healing.

## Purpose
Provides a reusable pattern for any system that manages typed entities (skills, agents, tools, knowledge, etc.) requiring:
- Frontmatter schema validation on startup
- Event-driven validation failure emission
- Automatic chain/execution blocking for invalid entities
- Procedural self-healing of common frontmatter errors
- Dependency graph management for initialization order

## Core Components

### 1. Frontmatter Schema (`_system/schemas/frontmatter.schema.yaml`)
Defines required keys, valid types, statuses, owners, and validation rules:
- 11 entity types: command, agent, skill, rule, workflow, tool, knowledge, data, memory, output, project
- 6 lifecycle states: scratch → research → candidate → canon → deprecated → archived
- Canon governance: requires `owner: operator` (agents cannot self-promote)
- Plumbing patterns exempt from validation

### 2. Entity Validator (`scripts/ibos_entity_sensor.py`)
- Scans all entity directories on startup
- Validates frontmatter against schema
- Builds dependency graph from `depends_on` → `cache/entity_dependency_graph.json`
- Emits `ibos_validation_failed` event for violations (level 0 = critical)
- Maintains blocked entities list → `cache/blocked_entities.json`

### 3. Chain Blocking (`scripts/chain_executor.py`)
```python
def run_chain_for_event(event_type, payload):
    entity_id = payload.get("entity_id")
    if entity_id and is_entity_blocked(entity_id):
        return {"blocked": True, "reason": "IBOS validation failure", "steps_run": 0}
    # ... normal execution
```

### 4. Self-Healing Trigger (`scripts/procedural_executor.py` → `trigger_ibos_self_heal()`)
Runs every 15min as TRIGGER-009. Auto-fixes 6 common frontmatter issues:
1. **Missing required keys** → generates from description/body (summary), defaults (version=1.0.0, status=scratch, owner=agent, created=now, type from dir, namespace from path)
2. **Invalid status** → scratch
3. **Invalid type** → skill
4. **Invalid owner** → agent
5. **Canon with non-operator owner** → candidate (critical governance rule)
6. **Confidence out of range** → 0.5

### 5. Sensor Integration (`scripts/sensor_array.py` → `sensor_ibos_entities()`)
- Runs once per session (`ibos_validated_this_session` flag)
- On failure: emits `ibos_validation_failed` with blocked entities list
- On success: emits `ibos_validation_passed`

## Event Flow
```
sensor_ibos_entities (boot)
    │
    ▼
ibos_validation_failed (level 0)
    │
    ├──▶ chain_executor blocks chains for entity_id
    │
    ▼
trigger_ibos_self_heal (every 15min via procedural_executor)
    │
    ▼
Auto-fix frontmatter → rewrite file
    │
    ▼
Next sensor sweep → ibos_validation_passed
    │
    ▼
blocked_entities cleared → chains unblocked
```

## Key Files
| File | Role |
|------|------|
| `_system/schemas/frontmatter.schema.yaml` | Validation schema |
| `scripts/ibos_entity_sensor.py` | Validator + CLI |
| `scripts/sensor_array.py` | Sensor integration |
| `scripts/chain_executor.py` | Chain blocking |
| `scripts/procedural_executor.py` | Self-heal trigger (TRIGGER-009) |
| `cache/ibos_validation_state.json` | Validation state |
| `cache/blocked_entities.json` | Blocked entity list |
| `cache/entity_dependency_graph.json` | Dependency graph |

## CLI Usage
```bash
# Validate all entities
python scripts/ibos_entity_sensor.py validate

# Show validation state
python scripts/ibos_entity_sensor.py state

# Show blocked entities
python scripts/ibos_entity_sensor.py blocked

# Show dependencies for entity
python scripts/ibos_entity_sensor.py deps <entity_id>

# Run self-heal manually
python scripts/procedural_executor.py --run ibos_heal
```

## Integration Checklist
- [ ] Add entity directories to `ENTITY_DIRS` in procedural_executor.py
- [ ] Define `VALID_TYPES`, `VALID_STATUSES`, `VALID_OWNERS`, `REQUIRED_KEYS` constants
- [ ] Register `sensor_ibos_entities` in `sweep_all()` sensor list
- [ ] Add `ibos_heal` to `TRIGGER_MAP` and `check_all_triggers()`
- [ ] Implement `check_ibos_validation()` and `extract_entity_from_event()` in chain_executor.py
- [ ] Add `ibos_validation_failed` / `ibos_validation_passed` to event_registry.json if using event_reactor

## Pitfalls & Gotchas
1. **YAML datetime serialization**: `yaml.dump()` handles datetime objects natively (ISO8601 string output)
2. **Frontmatter body preservation**: Split at closing `---` correctly, preserve body exactly
3. **Entity discovery**: Scan all `ENTITY_DIRS` recursively, respect plumbing patterns
4. **Idempotency**: Self-heal must be re-runnable — check `changed` flag before writing
5. **Canon governance**: Never auto-promote to canon; only demote (canon+agent → candidate)
6. **Session flag**: Use `ibos_validated_this_session` in sensors_state to run once per boot

## Related Skills
- `procedural-logic` — deterministic reflexes (TRIGGER-009 pattern)
- `self-improvement/closed-loop-autonomy` — producer/consumer loop (sensor → heal)
- `autonomous-ai-agents` — chain blocking as safety gate
- `autonomous-system-operations` — background validation sweeps

## Cross-Store Entity Sync (EE ↔ KC)

### The Trap
Entity Engine can have 3000+ entities with mention_count=0. This happens when EE was populated by an extraction pipeline (crystal_will, suggestion processor) but **no sync pipeline was ever created** to connect EE mentions with actual KC content.

When user sees "mentions=0" for their own name, it looks broken — because it is.

### The Fix Pattern

```
1. Read ALL text from ALL KC tables (experiences, kc_entries, kc_fts)
2. For each entity in EE, count real mentions via str.count(name_lower)
3. Batch-update mention_count in EE (executemany, 50-100 per batch)
4. Create relationships for co-occurring entities
```

**Critical implementation details:**
- **Filter by name length** (`LENGTH(name) >= 3`) — short names like "action", "error", "time" match thousands of times and drown out real entities
- **All KC tables** — `experiences.raw_text`, `kc_entries.content`, `kc_fts.content` all have different data
- **Relationships** — after mention sync, create `co_occurs_with` or `is_owner_of` relationships for entities that co-occur in records

### The Quality Problem
Most entities in EE are generic words extracted from system texts (improvement suggestions, log files):
- `known`, `unknown`, `pattern`, `time`, `error`, `event` — these are noise, not entities
- Real domain entities (DeepTutor, Bybit, Mem0, FastEmbed) are invisible because their names don't appear in system experiences

**Fix options:**
1. **Source filtering** — only extract entities from `kc_entries` (real knowledge), not from `experiences` (system noise)
2. **LLM entity extraction** — use LLM to extract real entities from KC content instead of naive substring matching
3. **Entity type gating** — only populate entities with type != 'Концепция' (which catches generic words)

### User Identity in Knowledge Systems
User names/references typically DON'T appear in KC:
- `experiences` table stores system events, not user conversations
- User identity lives in session databases (`sessions.db`, `session_recall.db`)
- **Fix**: use `record_user_to_kc.py` pattern — records messages with `[user:{name}]` prefix, creates principal fact, tags with `user:{name}`, re-syncs EE. See `references/user-message-recording.md` for full implementation.

### Verification
```python
ee = sqlite3.connect('cache/entity_engine.db')
c = ee.cursor()
c.execute('SELECT COUNT(*) FROM entities WHERE mention_count = 0')
print(f'Entities with 0 mentions: {c.fetchone()[0]}')
c.execute('SELECT COUNT(*) FROM relationships')
print(f'Relationships: {c.fetchone()[0]}')
```