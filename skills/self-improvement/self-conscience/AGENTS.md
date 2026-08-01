# self-conscience — Skill

## Purpose
Gate before every significant response — 3 вопроса совести. Лучшая версия тебя проверяет решения до их принятия.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: conscience, gate, self-review, quality
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Gate before every significant response — 3 вопроса совести
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