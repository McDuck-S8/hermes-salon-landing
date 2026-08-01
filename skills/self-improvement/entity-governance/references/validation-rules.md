# Validation Rules — Detailed Explanations

Each validation rule in `frontmatter.schema.yaml` is implemented in `scripts/ibos_entity_sensor.py::validate_frontmatter()`.

## Required Keys (8)
All entity files MUST have these frontmatter keys:

| Key | Purpose | Example |
|-----|---------|---------|
| `id` | Unique stable identifier | `crystal-core` |
| `type` | Entity type (11 valid) | `skill` |
| `namespace` | Namespace path | `knowledge/ai-core` |
| `status` | Lifecycle state (6 valid) | `canon` |
| `version` | Semantic version | `1.0.0` |
| `owner` | `operator` or `agent` | `operator` |
| `created` | ISO8601 timestamp | `2026-06-29T00:00:00Z` |
| `summary` | One-line description | `Self-learning loop: observe→diagnose→will→execute→learn` |
| `description` | Full description | Multi-line markdown content |

## Valid Types (11)
```
command, agent, skill, rule, workflow, tool, knowledge, data, memory, output, project
```
Invalid type → auto-fix to `skill` by self-heal.

## Valid Statuses (6)
```
scratch → research → candidate → canon → deprecated → archived
```
Invalid status → auto-fix to `scratch` by self-heal.

**Canon Governance**: `status == "canon"` requires `owner == "operator"`. Agents cannot self-promote to canon. Self-heal demotes to `candidate`.

## Valid Owners (2)
```
operator, agent
```
Invalid owner → auto-fix to `agent` by self-heal.

## Retrieval Classes (3)
```
hot, warm, cold
```
Affects retrieval priority in Knowledge Cube / session_recall.

## Export Classes (3)
```
public, private, operator
```
Controls visibility in external adapters (Obsidian, .claude/, etc.)

## ID Format
Regex: `^[a-z0-9-]+$` — kebab-case, lowercase, alphanumeric + hyphens only.
- No timestamps, no random suffixes
- Stable identifier

## Namespace Format
Regex: `^[a-z0-9-]+(/[a-z0-9-]+)*$` — kebab-case path.
Examples: `knowledge/ai-core`, `knowledge/arbitrage/seo`

## Version Format
Regex: `^\d+\.\d+\.\d+$` — semantic versioning.
Invalid → self-heal defaults to `1.0.0`

## Created Format
ISO8601: `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$`
YAML parses this as datetime object — validator handles both string and datetime objects.

## Canon Governance Rule
```
check: "status == 'canon' and owner != 'operator'"
severity: error
message: "canon status requires operator approval (owner must be 'operator')"
```
**Self-heal action**: Demotes `canon` + `agent` → `candidate` (never promotes to canon).

## Candidate Source Rule
```
check: "status == 'candidate' and (promotes_from is null or promotes_from | length == 0)"
severity: warning
message: "candidate status should have promotes_from (source synthesis nodes)"
```

## No Self-Promotion Rule
```
check: "promotes_to contains id"
severity: error
message: "entity cannot promote to itself"
```

## Plumbing Patterns (Exempt from Validation)
Files matching these patterns are skipped entirely:
- `README.md`, `CLAUDE.md`, `AGENTS.md`, `START-HERE.md`
- `.obsidian/`, `_system/`, `swarms/`, `docs/`
- `knowledge/*/INDEX.md`, `knowledge/*/support/*`, `knowledge/*/archive/*`
- `intake/*`, `sessions/*`, `*/waves/surfaces/dist/`
- `node_modules/`, and more (see `plumbing_patterns` in schema)

## Namespace Profiles (8)
| Profile | Required Surfaces | Core File |
|---------|-------------------|-----------|
| `standard` | INDEX.md, canon/, playbooks/, support/, synthesis/ | core-doctrine.md |
| `reduced` | INDEX.md, canon/ | core-doctrine.md |
| `tool-contract` | INDEX.md, canon/, core-contract.md | core-contract.md |
| `ai-core` | INDEX.md, canon/, playbooks/, support/, synthesis/ | core-doctrine.md |
| `telegram-bots` | INDEX.md, canon/, playbooks/, support/, synthesis/ | core-doctrine.md |
| `arbitrage` | INDEX.md, canon/, playbooks/, support/, synthesis/ | core-doctrine.md |
| `finance` | INDEX.md, canon/, playbooks/, support/, synthesis/ | core-doctrine.md |
| `personal` | INDEX.md, canon/ | core-doctrine.md |

**Reduced base** (`reduced_base: true`) only requires `INDEX.md` and `canon/`.