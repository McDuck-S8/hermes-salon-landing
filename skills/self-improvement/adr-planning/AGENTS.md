# adr-planning — Skill

## Purpose
Architecture Decision Records (ADR) — документирование архитектурных решений с контекстом и последствиями. Внедрено после изучения 5 репозиториев планирования.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: planning, adr, architecture, decision, documentation, strategy
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Architecture Decision Records (ADR) — документирование архитектурных решений с контекстом и последствиями
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