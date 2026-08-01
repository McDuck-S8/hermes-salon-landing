# osint-site-builder — Skill

## Purpose
OSINT → сайт за 1 фазу. Аналізує Telegram-канал бізнесу, збирає всі дані (послуги, ціни, фото, контакти) і генерує landing page. Три фази: OSINT → Генерація → Звіт.


## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: OSINT → сайт за 1 фазу
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (3 files) |