# entity-governance — Skill

## Purpose
Validation, blocking & self-healing for typed entity lifecycles (skills, agents, tools, knowledge, etc.)

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: validation, schema, frontmatter, self-healing, governance, ibos, procedural, chain-blocking
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Validation, blocking & self-healing for typed entity lifecycles (skills, agents, tools, knowledge, etc
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (6 files) |
| `scripts/` | Helper scripts (1 files) |