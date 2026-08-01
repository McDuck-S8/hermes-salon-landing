# telegram-service-bot — Skill

## Purpose
Build Telegram booking bots for service businesses (salons, clinics, studios). Multi-role (client/master/admin), calendar with time slots, SQLite backend, inline keyboards. **python-telegram-bot + HTT

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: бот для салона / парикмахерской / маникюра, booking bot / appointment bot, telegram bot для записи клиентов, бот мастер / админ / клиент, салон красоты бот, запись через telegram
- **Required tools**: telegram, bot, booking, salon, aiogram, sqlite, service-business, calendar
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Build Telegram booking bots for service businesses (salons, clinics, studios)
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (12 files) |