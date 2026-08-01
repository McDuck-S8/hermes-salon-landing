# stealth-browser-mcp — Skill

## Purpose
Подключение к Chrome пользователя через CDP 9222 — browser-harness CLI + nodriver fallback. Обход блокировок через v2rayN прокси.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Подключение к Chrome пользователя через CDP 9222 — browser-harness CLI + nodriver fallback
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
| `scripts/` | Helper scripts (2 files) |