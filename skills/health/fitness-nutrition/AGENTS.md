# fitness-nutrition — Skill Contract

## Purpose
No description provided

## Ownership
Hermes Agent — self-maintained via skill-forge. Category: general.

## Local Contracts
### Triggers
- When the task matches the skill's domain and purpose

### Required Tools
- bash
- pip
- curl
- python

### Configuration
- Standard skill configuration via SKILL.md frontmatter

## Work Guidance
### When to Use
- Trigger this skill when the user asks about:
- Trigger this skill when the user asks about:

### Common Patterns
- ```
# Search exercises by name
...```
- ```
# Get full details for a specific exercise
...```
- ```
# List exercises filtering by muscle, category, or equipment
...```
- **wger** (https://wger.de/api/v2/) — open exercise database, 690+ exercises with muscles, equipment, images. Public endp
- **USDA FoodData Central** (https://api.nal.usda.gov/fdc/v1/) — US government nutrition database, 380,000+ foods. `DEMO_K
- BMI, TDEE (Mifflin-St Jeor), one-rep max (Epley/Brzycki/Lombardi), macro splits, body fat % (US Navy method)

### Integration Points
- rs
- the
- Macro
- when
- Trigger

## Verification
- outputs (e.g. TDEE should be 1500-3500 for most adults).
- After running exercise search: confirm results include exercise names, muscle groups, and equipment.

## Child DOX Index
- **references/** — 1 files: FORMULAS.md
- **scripts/** — 2 files: body_calc.py, nutrition_search.py

---
*Generated: 2026-07-28 17:31*
*Source: SKILL.md frontmatter + content analysis*
