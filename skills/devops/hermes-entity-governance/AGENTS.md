# hermes-entity-governance — Skill

## Purpose
Class-level skill for managing Hermes entities with IBOS-compliant governance: validation, blocking, self-healing, cascade revalidation, and unblocking.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: hermes, ibos, validation, self-healing, cascade-revalidation, entity-governance
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Class-level skill for managing Hermes entities with IBOS-compliant governance: validation, blocking, self-healing, cascade revalidation, and unblocking
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (1 files) |
| `templates/` | Templates (1 files) |