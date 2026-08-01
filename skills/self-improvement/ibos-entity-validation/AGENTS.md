# ibos-entity-validation — Skill

## Purpose
IBOS (Infinite Brain OS) entity validation layer for Hermes — frontmatter schema, startup validator, sensor integration, and chain execution blocking for invalid entities.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: validation, ibos, governance, entity-management, frontmatter, chain-blocking
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: IBOS (Infinite Brain OS) entity validation layer for Hermes — frontmatter schema, startup validator, sensor integration, and chain execution blocking for invalid entities
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (4 files) |
| `templates/` | Templates (1 files) |