# design-button-component — Skill

## Purpose
Provides reusable button components: Button. Includes HTML, CSS, Tailwind, and accessibility patterns.

## Ownership
Managed by Hermes Agent. Self-contained skill with templates.

## Local Contracts
- **Triggers**: need button component, create button
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir

## Work Guidance
**When to use**: Provides reusable button components: Button. Includes HTML, CSS, Tailwind, and accessibility patterns.
**Common patterns**: 
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in templates/
- Verify templates/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `templates/` | Code templates (HTML, CSS, Tailwind) |
| `config.yaml` | Skill configuration |
| `SKILL.md` | This skill definition |
| `AGENTS.md` | This file |
