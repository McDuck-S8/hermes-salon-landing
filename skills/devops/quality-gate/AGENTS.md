# quality-gate — Skill

## Purpose
Quality Gate — саб-агент, який перевіряє HTML/CSS правки перед показом клієнту. Виявляє: биті посилання, відсутні файли, невалідний HTML, CSS-баги, неконсистентність змін, WCAG-помилки, неповноту конт

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Quality Gate — саб-агент, який перевіряє HTML/CSS правки перед показом клієнту
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
| `scripts/` | Helper scripts (1 files) |