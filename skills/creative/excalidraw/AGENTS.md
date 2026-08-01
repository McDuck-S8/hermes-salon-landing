# excalidraw — Skill Contract

## Purpose
No description provided

## Ownership
Hermes Agent — self-maintained via skill-forge. Category: general.

## Local Contracts
### Triggers
- When the task matches the skill's domain and purpose

### Required Tools
- python
- bash
- write_file
- pip
- terminal

### Configuration
- Standard skill configuration via SKILL.md frontmatter

## Work Guidance
### When to Use
- Generate `.excalidraw` files for architecture diagrams, flowcharts, sequence diagrams, concept maps, and more. Files can be opened at excalidraw.com or uploaded for shareable links.
- Generate `.excalidraw` files for architecture diagrams, flowcharts, sequence diagrams, concept maps, and more. Files can be opened at excalidraw.com or uploaded for shareable links.

### Common Patterns
- ```
python skills/diagramming/excalidraw/scripts/upload.py ~/diagrams/my_diagram.excalidraw
...```
- **Load this skill** (you already did)
- **Write the elements JSON** -- an array of Excalidraw element objects
- **Save the file** using `write_file` to create a `.excalidraw` file
- **Optionally upload** for a shareable link using `scripts/upload.py` via `terminal`
- `strokeColor`: `"#1e1e1e"`

### Integration Points
- -
- the
- this
- ed
- emoji

## Verification
- Load skill and verify it responds to trigger conditions
- Run skill's example/test commands from SKILL.md
- Check skill output matches expected format

## Child DOX Index
- **references/** — 3 files: colors.md, dark-mode.md, examples.md
- **scripts/** — 1 files: upload.py

---
*Generated: 2026-07-28 17:31*
*Source: SKILL.md frontmatter + content analysis*
