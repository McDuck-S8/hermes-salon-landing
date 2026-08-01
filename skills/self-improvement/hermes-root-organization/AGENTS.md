# hermes-root-organization — Skill

## Purpose
Organize the Hermes root directory — sort files into proper subdirs, clean trash, maintain FILE_REGISTRY.md as the single source of truth for every file in the repo.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Organize the Hermes root directory — sort files into proper subdirs, clean trash, maintain FILE_REGISTRY
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