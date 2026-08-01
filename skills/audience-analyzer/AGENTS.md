# audience-analyzer — Skill

## Purpose
Universal Audience Analyzer — анализ любой ЦА из публичных источников (Telegram, YouTube, VK, форумы) или подбор ЦА под оффер. Два режима: Audience→Offer и Offer→Audience. Использует методологию human

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: audience-analysis, cpa-research, telegram-parsing, youtube-analysis, value-mapping, ripple-engine
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Universal Audience Analyzer — анализ любой ЦА из публичных источников (Telegram, YouTube, VK, форумы) или подбор ЦА под оффер
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
| `templates/` | Templates (2 files) |
| `scripts/` | Helper scripts (1 files) |