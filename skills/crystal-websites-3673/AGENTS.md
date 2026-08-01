# crystal-websites-3673 — Skill Contract

## Purpose
No description provided

## Ownership
Hermes Agent — self-maintained via skill-forge. Category: general.

## Local Contracts
### Triggers
- When the task matches the skill's domain and purpose

### Required Tools
- Standard Hermes toolset (read_file, write_file, search_files, terminal, web_search, skill_view, skill_manage)

### Configuration
- Standard skill configuration via SKILL.md frontmatter

## Work Guidance
### When to Use
- Закрепить успешный паттерн для websites как скилл

### Common Patterns
- Load skill via `skill_view(name='{name}')`, then follow skill-specific workflow

### Integration Points
- Self-contained skill; loads via `skill_view()`

## Verification
- Load skill and verify it responds to trigger conditions
- Run skill's example/test commands from SKILL.md
- Check skill output matches expected format

## Child DOX Index
- No child directories found (references/, templates/, scripts/)

---
*Generated: 2026-07-28 17:31*
*Source: SKILL.md frontmatter + content analysis*
