# telegram-bot-integration — Skill

## Purpose
Build Telegram bots that receive commands via long-polling and run local Hermes/system scripts (crystal.py, etc.). Covers proxy config for Russia, subprocess integration, output formatting without Mar

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: telegram, bot, long-polling, proxy, wsl, background-process, integration
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Build Telegram bots that receive commands via long-polling and run local Hermes/system scripts (crystal
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (14 files) |