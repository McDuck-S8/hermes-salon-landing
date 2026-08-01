# vibe-mode — Skill

## Purpose
Режим творческого взлома — нарушать шаблоны, импровизировать, находить нестандартные решения. Включается осознанно по 4 триггерам, имеет 4 запрета.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Режим творческого взлома — нарушать шаблоны, импровизировать, находить нестандартные решения
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