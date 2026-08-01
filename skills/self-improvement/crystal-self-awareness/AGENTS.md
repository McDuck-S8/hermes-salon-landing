# crystal-self-awareness — Skill

## Purpose
Crystal self-awareness workflow: run iterative cycles, clear studied cache, verify self_model.json updates

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: crystal, self-awareness, self-model, iterative, self-model-json
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Crystal self-awareness workflow: run iterative cycles, clear studied cache, verify self_model
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (2 files) |
| `scripts/` | Helper scripts (1 files) |