# pptx-author — Skill Contract

## Purpose
No description provided

## Ownership
Hermes Agent — self-maintained via skill-forge. Category: general.

## Local Contracts
### Triggers
- When NOT to use this
- Use when
- Use the firm template when

### Required Tools
- bash
- pip
- python

### Configuration
- Standard skill configuration via SKILL.md frontmatter

## Work Guidance
### When to Use
- you need to deliver a deck as a file artifact, not drive a live PowerPoint session.
- skill

### Common Patterns
- ```
pip install "python-pptx>=0.6"
...```
- ```
from pptx import Presentation
...```
- ```
from pptx.util import Inches
...```
- Cover / title
- Disclaimer
- Table of contents

### Integration Points
- writes
- the
- workbook
- this
- Users

## Verification
- Load skill and verify it responds to trigger conditions
- Run skill's example/test commands from SKILL.md
- Check skill output matches expected format

## Child DOX Index
- No child directories found (references/, templates/, scripts/)

---
*Generated: 2026-07-28 17:31*
*Source: SKILL.md frontmatter + content analysis*
