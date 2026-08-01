# design-style-patterns — Skill

## Purpose
Applies style design patterns: tailwind, css-grid, accessibility, css, responsive, variable-fonts, focus-states. Includes CSS/Tailwind implementations and usage contexts.

## Ownership
Managed by Hermes Agent. Self-contained skill with templates.

## Local Contracts
- **Triggers**: need style pattern, apply tailwind, apply css-grid, apply accessibility, apply css, apply responsive, apply variable-fonts, apply focus-states
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir

## Work Guidance
**When to use**: Applies style design patterns: tailwind, css-grid, accessibility, css, responsive, variable-fonts, focus-states. Includes CSS/Tailwind implementations and usage contexts.
**Common patterns**: pattern_tailwind, pattern_css_grid, pattern_accessibility, pattern_css, pattern_responsive, pattern_variable_fonts, pattern_focus_states
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
