# design-color-patterns — Skill

## Purpose
Applies color design patterns: glassmorphism, dark-mode. Includes CSS/Tailwind implementations and usage contexts.

## Ownership
Managed by Hermes Agent. Self-contained skill with templates.

## Local Contracts
- **Triggers**: need color pattern, apply glassmorphism, apply dark-mode
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir

## Work Guidance
**When to use**: Applies color design patterns: glassmorphism, dark-mode. Includes CSS/Tailwind implementations and usage contexts.
**Common patterns**: pattern_glassmorphism, pattern_dark_mode
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
