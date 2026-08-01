# Self-Heal Rules — 6 Auto-Fix Patterns

These are the 6 deterministic rules applied by `trigger_ibos_self_heal()` in `procedural_executor.py` (TRIGGER-009).

## Rule 1: Missing Required Keys
**Trigger**: Any of `REQUIRED_KEYS` absent from frontmatter.

| Key | Auto-Fix Source |
|-----|-----------------|
| `summary` | First 150 chars of `description` or body |
| `description` | First 500 chars of body |
| `version` | `"1.0.0"` |
| `status` | `"scratch"` |
| `owner` | `"agent"` |
| `created` | `datetime.now(timezone.utc).isoformat()` |
| `type` | Inferred from directory: `agents/`→agent, `skills/`→skill, `tools/`→tool, `knowledge/`→knowledge, else `skill` |
| `namespace` | Inferred from path: `knowledge/ai-core`→`knowledge/ai-core`, `knowledge/arbitrage`→`knowledge/arbitrage`, `knowledge/finance`→`knowledge/finance`, else `knowledge/ai-core` |
| `id` | Uses entity_id from validation state |

**Idempotency**: Only writes if `changed=True` after applying all fixes.

## Rule 2: Invalid Status
**Trigger**: `status` not in `VALID_STATUSES` (scratch, research, candidate, canon, deprecated, archived)
**Fix**: `status = "scratch"`

## Rule 3: Invalid Type
**Trigger**: `type` not in `VALID_TYPES` (command, agent, skill, rule, workflow, tool, knowledge, data, memory, output, project)
**Fix**: `type = "skill"`

## Rule 4: Invalid Owner
**Trigger**: `owner` not in `VALID_OWNERS` (operator, agent)
**Fix**: `owner = "agent"`

## Rule 5: Canon Governance (CRITICAL)
**Trigger**: `status == "canon"` AND `owner != "operator"`
**Fix**: `status = "candidate"` (demotes, never promotes)
**Rationale**: Canon is operator-approved only. Agents cannot self-promote. This is the **governance guard** — prevents unauthorized canon elevation.

## Rule 6: Confidence Out of Range
**Trigger**: `confidence` present but not a float in [0.0, 1.0]
**Fix**: `confidence = 0.5`
**Handles**: Missing, string, out-of-range, NaN, null

---

## Execution Order
Rules run sequentially within a single pass. Multiple fixes can apply to one entity — all are applied before writing.

```python
changed = False
# Rule 1: Missing keys
for key in REQUIRED_KEYS:
    if key not in fm:
        fm[key] = default_for(key)
        changed = True
# Rule 2: Invalid status
if fm.get("status") not in VALID_STATUSES:
    fm["status"] = "scratch"
    changed = True
# Rule 3: Invalid type
if fm.get("type") not in VALID_TYPES:
    fm["type"] = "skill"
    changed = True
# Rule 4: Invalid owner
if fm.get("owner") not in VALID_OWNERS:
    fm["owner"] = "agent"
    changed = True
# Rule 5: Canon governance
if fm.get("status") == "canon" and fm.get("owner") != "operator":
    fm["status"] = "candidate"
    changed = True
# Rule 6: Confidence range
if "confidence" in fm:
    try:
        conf = float(fm["confidence"])
        if not (0.0 <= conf <= 1.0):
            fm["confidence"] = 0.5
            changed = True
    except (ValueError, TypeError):
        fm["confidence"] = 0.5
        changed = True

if changed:
    write_back(fm, body)
```

---

## Idempotency Guarantees
- **No-op on clean entities**: `changed` remains False → no write
- **Re-runnable**: Same input → same output every time
- **Preserves unknown keys**: Unknown frontmatter keys are kept (only warnings emitted)
- **Body preserved exactly**: Only frontmatter rewritten; body untouched

---

## Failure Modes (logged, not fatal)
| Mode | Logged As | Behavior |
|------|-----------|----------|
| File not found | `ibos_self_heal:<id>` / `locate_file` / `not found` | `failed += 1` |
| YAML parse error | `ibos_self_heal:<id>` / `error` / `<exception>` | `failed += 1` |
| No frontmatter | `ibos_self_heal:<id>` / `error` / `"No frontmatter"` | `failed += 1` |
| Unclosed frontmatter | `ibos_self_heal:<id>` / `error` / `"Unclosed frontmatter"` | `failed += 1` |
| Write permission | `ibos_self_heal:<id>` / `error` / `<OSError>` | `failed += 1` |

All failures logged to `procedural_feedback.jsonl` and `ALERTS.md` — **never crash the executor**.

---

## Event Emission
- **On fix**: `log_feedback("ibos_self_heal:<id>", "auto_fix", "fixed N fields", True)`
- **On fix batch**: `log_alert("TRIGGER-009: IBOS self-heal fixed X entities, Y failed")`
- **On all fail**: `log_alert("TRIGGER-009: IBOS self-heal could not fix Y entities")`
- **Next sensor sweep**: Emits `ibos_validation_passed` when `blocked_entities == []`

---

## Integration Points
| Component | File | Role |
|-----------|------|------|
| Trigger registration | `procedural_executor.py` | `TRIGGER_MAP["ibos_heal"]` + `check_all_triggers()` |
| Sensor | `sensor_array.py` | `sensor_ibos_entities()` in `sweep_all()` |
| Validator | `ibos_entity_sensor.py` | `run_startup_validation()` |
| Chain blocker | `chain_executor.py` | `run_chain_for_event()` → `is_entity_blocked()` |
| State storage | `cache/` | `ibos_validation_state.json`, `blocked_entities.json`, `entity_dependency_graph.json` |