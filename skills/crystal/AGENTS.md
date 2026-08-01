# crystal — Skill

## Purpose
Замкнутый контур самосознания: observe → diagnose → will → record. 3263 строки, 37 функций. Реализация: scripts/crystal.py

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Замкнутый контур самосознания: observe → diagnose → will → record
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `scripts/` | Helper scripts (1 files) |