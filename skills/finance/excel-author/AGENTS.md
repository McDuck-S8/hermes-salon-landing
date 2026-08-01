# excel-author — Skill Contract

## Purpose
No description provided

## Ownership
Hermes Agent — self-maintained via skill-forge. Category: general.

## Local Contracts
### Triggers
- When NOT to use this

### Required Tools
- bash
- terminal
- pip
- python

### Configuration
- Standard skill configuration via SKILL.md frontmatter

## Work Guidance
### When to Use
- skill

### Common Patterns
- ```
pip install "openpyxl>=3.0"
...```
- ```
# WRONG — silent bug waiting to happen
...```
- ```
from openpyxl.workbook.defined_name import DefinedName
...```
- Raw historical inputs (actual revenues, reported EBITDA, etc.)
- Assumption drivers the user is meant to flex (growth rates, WACC inputs, terminal g)
- Current market data (share price, debt balance) — with a cell comment documenting source + date

### Integration Points
- this
- Users
- assumes
- named
- r

## Verification
- scripts, CI) need computed values.
- step-by-step with the user

## Child DOX Index
- **scripts/** — 1 files: recalc.py

---
*Generated: 2026-07-28 17:31*
*Source: SKILL.md frontmatter + content analysis*
