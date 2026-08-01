# persona-system — Skill

## Purpose
Persona System — переключение режимов агента (arbitrage, sales, analyst, developer). Каждый режим имеет свои директивы, память, tool priority, temperature и system prompt.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: persona, mode-switching, arbitrage, sales, analyst, developer, self-improvement
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Persona System — переключение режимов агента (arbitrage, sales, analyst, developer)
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (2 files) |