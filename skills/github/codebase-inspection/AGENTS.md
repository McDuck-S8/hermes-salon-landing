# codebase-inspection — Skill Contract

## Purpose
No description provided

## Ownership
Hermes Agent — self-maintained via skill-forge. Category: general.

## Local Contracts
### Triggers
- When the task matches the skill's domain and purpose

### Required Tools
- git
- bash
- pip
- python

### Configuration
- Standard skill configuration via SKILL.md frontmatter

## Work Guidance
### When to Use
- - User asks for LOC (lines of code) count
- - User asks for LOC (lines of code) count

### Common Patterns
- ```
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
...```
- ```
cd /path/to/repo
...```
- ```
# Python projects
...```
- **Always exclude .git, node_modules, venv** — without `--folders-to-skip`, pygount will crawl everything and may take mi
- **Markdown shows 0 code lines** — pygount classifies all Markdown content as comments, not code. This is expected behavi
- **JSON files show low code counts** — pygount may count JSON lines conservatively. For accurate JSON line counts, use `w

### Integration Points
- pygount
- r
- User

## Verification
- Load skill and verify it responds to trigger conditions
- Run skill's example/test commands from SKILL.md
- Check skill output matches expected format

## Child DOX Index
- No child directories found (references/, templates/, scripts/)

---
*Generated: 2026-07-28 17:31*
*Source: SKILL.md frontmatter + content analysis*
