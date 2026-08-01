# IBOS Governance Layer Validation Reference

**Created:** 2026-06-29  
**Context:** Bootstrapped full Infinite Brain OS (IBOS) governance layer for Hermes

---

## Quick Reference

### Frontmatter Schema (11 Entity Types)
| Type | Canonical Location | Runtime Adapter |
|------|-------------------|-----------------|
| command | `entities/commands/` | `.claude/commands/`, `.codex/commands/` |
| agent | `entities/agents/` | `.claude/agents/`, `.codex/agents/` |
| skill | `entities/skills/` | `.claude/skills/`, `.codex/skills/` |
| rule | `entities/rules/` | `.claude/rules/` |
| workflow | `workflows/`, `automations/n8n/` | none |
| tool | `tools/` | none |
| knowledge | `knowledge//` | none |
| data | `data/` | none |
| memory | `memory/` | none |
| output | `outputs/` | none |
| project | `projects/{name/PLAN.md` | none |

**Departments** (`departments/`) are assemblies over ontology, NOT a 12th type.

---

## Validation Rules (12 Rules)

| Rule ID | Description | Severity |
|---------|-------------|----------|
| `canon-requires-operator` | `status == 'canon'` requires `owner == 'operator'` | ERROR |
| `candidate-needs-source` | `candidate` must have `promotes_from` | WARNING |
| `no-self-promotion` | Entity cannot `promotes_to` itself | ERROR |
| `stable-id-format` | ID must be kebab-case `[a-z0-9-]+` | ERROR |
| `namespace-format` | Namespace must be `knowledge/domain/sub` path | ERROR |
| `version-semver` | Version must be semver `\d+\.\d+\.\d+` | ERROR |
| `created-iso8601` | Created must be ISO8601 timestamp | ERROR |
| `confidence-range` | Confidence 0.0-1.0 | WARNING |
| `retrieval-class-valid` | hot/warm/cold | WARNING |
| `export-class-valid` | public/private/operator | WARNING |
| `wikilinks-resolvable` | All `[[id]]` resolve to entity registry | WARNING |
| `namespace-surfaces` | Required surfaces per profile | ERROR |

---

## Namespace Profiles (8)

| Profile | Reduced Base | Core File | Required Surfaces |
|---------|-------------|-----------|-------------------|
| `ai-core` | No | `core-doctrine.md` | INDEX.md, canon/, playbooks/, support/, synthesis/ |
| `telegram-bots` | No | `core-doctrine.md` | INDEX.md, canon/, playbooks/, support/, synthesis/ |
| `arbitrage` | No | `core-doctrine.md` | INDEX.md, canon/, playbooks/, support/, synthesis/ |
| `finance` | No | `core-doctrine.md` | INDEX.md, canon/, playbooks/, support/, synthesis/ |
| `ops` | No | `core-doctrine.md` | INDEX.md, canon/, playbooks/, support/, synthesis/ |
| `research` | No | `core-doctrine.md` | INDEX.md, canon/, playbooks/, support/, synthesis/ |
| `infra` | No | `core-contract.md` | INDEX.md, canon/, playbooks/, support/, synthesis/ |
| `personal` | **Yes** | `core-doctrine.md` | INDEX.md, canon/ |

---

## Promotion Path

```
raw source → support/ → synthesis/ → canon-candidate → canon (operator approval REQUIRED)
```

- Agent CANNOT self-promote to canon
- Validator enforces: `status == 'canon'` → `owner == 'operator'`
- Candidate must have `promotes_from` (array of synthesis node IDs)
- Synthesis → canon-candidate → canon requires human operator approval

---

## Validator Usage

```bash
# Run validation
cd /d/Portable_Soft/hermes
python scripts/validate_entities.py

# With report
python scripts/validate_entities.py --report
# Generates: _system/validation_report.md

# JSON output
python scripts/validate_entities.py --json
```

### Exit Codes
- `0` = clean (all entities pass)
- `1` = errors found

### Output Example (Clean)
```
=== Hermes + IBOS Validator ===
Repo root: D:\Portable_Soft\hermes
Schema: D:\Portable_Soft\hermes\_system\schemas\frontmatter.schema.yaml

Found 15 entities

=== SUMMARY ===
Entities validated: 15
Total errors: 0
Total warnings: 0
```

---

## Entity Registry (as of 2026-06-29)

| Type | Count | IDs |
|------|-------|-----|
| Agents | 2 | `hermes-autonomous-agent`, `autonomous-agent` |
| Skills | 7 | `crystal-core`, `session-recall`, `signal-daemon`, `bayesian-scorer`, `sensor-array`, `event-classifier` |
| Tools | 5 | `event-bus`, `goal-queue`, `goal-executor`, `procedural-executor`, `rd-processor`, `dev-processor` |
| Knowledge | 1 | `knowledge-cube` |
| **Total** | **15** | All `status: canon`, `owner: operator` |

---

## Common Validation Fixes

### `created` datetime handling
YAML parses ISO8601 as `datetime` object. Validator handles both:
```python
if hasattr(created, 'isoformat'):
    created_str = created.isoformat()
else:
    created_str = str(created)
```

### Wikilink Resolution
All `[[id]]` must match entity `id` exactly.
```python
# Collect all entity IDs first
all_ids = set(entity['frontmatter']['id'] for entity in all_entities.values())
# Then validate each wikilink
for link in re.findall(r'\[\[([^\]]+)\]\]', content):
    link_id = link.split('|')[0].strip()
    if link_id not in all_ids:
        warnings.append(f"Broken wikilink: [[{link}]] -> '{link_id}'")
```

### Namespace Surfaces
Standard profile requires: `INDEX.md`, `canon/`, `playbooks/`, `support/`, `synthesis/`
Reduced profile (personal): `INDEX.md`, `canon/`

---

## Integration with Self-Diagnosis

Add to five-cube health check:

```bash
# 6. IBOS Governance Layer
echo "=== IBOS GOVERNANCE VALIDATION ==="
python scripts/validate_entities.py
if [ $? -eq 0 ]; then
    echo "✅ IBOS Governance: CLEAN"
else
    echo "❌ IBOS Governance: ERRORS FOUND"
    python scripts/validate_entities.py --report
fi
```

---

## Related Files

| File | Purpose |
|------|---------|
| `_system/schemas/frontmatter.schema.yaml` | Schema definition |
| `scripts/validate_entities.py` | Validator implementation |
| `scripts/validate_entities.py --report` | Report generator |
| `_system/validation_report.md` | Last validation report |
| `ARBITRAGE_WORKSHOP.md` | Full integration mapping |

---

## Next Steps (from integration plan)

| Phase | Target | Week |
|-------|--------|------|
| 1 | Frontmatter Contract + Validator CI hook | 1 |
| 2 | Namespace Registry + Promotion Path CLI | 2 |
| 3 | Session Ledger + Sync Adapters | 3 |
| 4 | Canon Governance + Obsidian Compat + MCP Config | 4 |