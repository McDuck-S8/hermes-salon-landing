# youtube-transcript — Skill

## Purpose
Извлечение транскриптов YouTube через youtube-transcript-api — автоматизация YouTube→текст→AI→Telegram

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: youtube, transcript, api, media, ai, telegram, pipeline
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Извлечение транскриптов YouTube через youtube-transcript-api — автоматизация YouTube→текст→AI→Telegram
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `scripts/` | Helper scripts (1 files) |