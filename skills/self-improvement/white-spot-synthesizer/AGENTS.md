# white-spot-synthesizer — Skill

## Purpose
Не отбрасывать непроверенные схемы, а достраивать их гипотезами с confidence. Превращать белые пятна в проверяемые утверждения.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Не отбрасывать непроверенные схемы, а достраивать их гипотезами с confidence
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| (no child directories) | |