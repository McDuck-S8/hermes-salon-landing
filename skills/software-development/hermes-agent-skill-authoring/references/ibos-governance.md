# IBOS Governance Patterns for Skill Authoring

**Created:** 2026-06-29  
**Context:** This session bootstrapped the full IBOS governance layer for Hermes. These patterns apply when creating/editing skills that live within the IBOS governance layer.

---

## Frontmatter for IBOS-Governed Entities

Every skill/command/agent/rule/workflow created in the IBOS governance layer MUST include this frontmatter:

```yaml
---
id: unique-kebab-case-id           # stable, no timestamps
type: skill|command|agent|rule|workflow|tool|knowledge|data|memory|output|project
namespace: knowledge/domain/sub    # kebab-case path
status: scratch|research|candidate|canon|deprecated|archived
version: 1.0.0                     # semver
owner: operator|agent              # canon requires operator
created: 2026-06-29T00:00:00Z      # ISO8601 (YAML parses as datetime)
summary: One-line summary
description: |
  Detailed description. Multi-line YAML string.
depends_on:                        # array of entity IDs
  - crystal-core
  - event-bus
tags:
  - self-learning
  - autonomous
confidence: 0.95                   # 0.0-1.0
retrieval_class: hot|warm|cold
export_class: public|private|operator
promotes_from: []                  # for candidate: synthesis node IDs
promotes_to: []                    # for support/synthesis: target IDs
---
```

---

## Skill Directory Structure (IBOS)

```
skills/<category>/<skill-name>/
├── SKILL.md                    # Entry point (loaded every activation, <500 lines)
├── references/
│   ├── ibos-governance.md      # This file
│   └── ...                     # Session-specific detail, error transcripts, API excerpts
├── templates/
│   └── frontmatter.template.yaml
└── scripts/
    └── validate_ibos.py        # Executable helpers
```

---

## Validation Workflow

When creating/editing an IBOS-governed entity:

1. **Write entity** with full frontmatter
2. **Run validator**: `python scripts/validate_entities.py`
3. **Fix errors** until 0 errors, 0 warnings
4. **Commit** both entity and any schema updates

### CI Hook (Planned)

```bash
# .git/hooks/pre-commit
python scripts/validate_entities.py || exit 1
```

---

## Common Patterns

### Wikilinks to Other Entities

Always use `[[entity-id]]` format. The validator will check resolution.

```markdown
## Related Entities
- [[crystal-core]] — Self-learning loop
- [[event-bus]] — Event-driven architecture
- [[autonomous-agent]] — Executive runtime
```

### Promotion Path Documentation

For entities intended to reach `canon`:

```yaml
# In synthesis node
status: synthesis
promotes_to:
  - canon-candidate-id

# In canon-candidate
status: candidate
promotes_from:
  - synthesis-node-id-1
  - synthesis-node-id-2
```

---

## Namespace Profiles Reference

| Profile | Use For | Base Surfaces |
|---------|---------|---------------|
| `ai-core` | Agent architecture, patterns | INDEX.md, canon/, playbooks/, support/, synthesis/ |
| `telegram-bots` | Bot knowledge, patterns | Same as ai-core |
| `arbitrage` | Traffic sources, monetization, schemes | Same as ai-core |
| `finance` | CPA networks, revenue models | Same as ai-core |
| `ops` | Infrastructure, deployment, monitoring | Same as ai-core |
| `research` | White papers, trends, experiments | Same as ai-core |
| `infra` | Hermes internals, config, scripts | INDEX.md, canon/, core-contract.md |
| `personal` | Operator profile, preferences | INDEX.md, canon/ (reduced base) |

---

## Schema Evolution

When adding new entity types or changing validation rules:

1. Update `_system/schemas/frontmatter.schema.yaml`
2. Update `scripts/validate_entities.py` validation logic
3. Run validator on all existing entities
4. Fix any regressions
5. Document in `references/ibos-governance-validation.md`

---

## Related Skills

- [[hermes-self-diagnosis]] — Full health check including IBOS validation
- [[hermes-agent-skill-authoring]] — Core skill authoring conventions