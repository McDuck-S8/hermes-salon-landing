# maps — Skill Contract

## Purpose
No description provided

## Ownership
Hermes Agent — self-maintained via skill-forge. Category: general.

## Local Contracts
### Triggers
- When the task matches the skill's domain and purpose

### Required Tools
- bash
- web_search
- pip
- python

### Configuration
- Standard skill configuration via SKILL.md frontmatter

## Work Guidance
### When to Use
- - User sends a Telegram location pin (latitude/longitude in the message) → `nearby`
- Europe and North America
- - User sends a Telegram location pin (latitude/longitude in the message) → `nearby`

### Common Patterns
- ```
MAPS=~/.hermes/skills/maps/scripts/maps_client.py
...```
- ```
python3 $MAPS search "Eiffel Tower"
...```
- ```
python3 $MAPS reverse 48.8584 2.2945
...```
- `nearby --near "Colosseum Rome" --category restaurant --radius 500`
- Extract lat/lon from the Telegram message
- `nearby LAT LON cafe --radius 1500`

### Integration Points
- Location
- User
- um
- supersedes
- ful

## Verification
- the `hours` field; if missing or unclear, verify
- ```bash

## Child DOX Index
- **scripts/** — 1 files: maps_client.py

---
*Generated: 2026-07-28 17:31*
*Source: SKILL.md frontmatter + content analysis*
