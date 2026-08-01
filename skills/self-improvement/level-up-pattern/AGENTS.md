# level-up-pattern — Skill

## Purpose
Мета-паттерн: когда застрял на одном уровне анализа — поднимись на уровень выше. Не меняй значение, меняй ось.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: meta, problem-solving, level-up, stuck
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Мета-паттерн: когда застрял на одном уровне анализа — поднимись на уровень выше
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