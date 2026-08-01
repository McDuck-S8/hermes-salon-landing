# airtable — Skill Contract

## Purpose
No description provided

## Ownership
Hermes Agent — self-maintained via skill-forge. Category: general.

## Local Contracts
### Triggers
- When the task matches the skill's domain and purpose

### Required Tools
- curl
- python
- bash
- jq
- browser_navigate
- terminal
- web_extract

### Configuration
- Standard skill configuration via SKILL.md frontmatter

## Work Guidance
### When to Use
- BEFORE mutating — confirms exact field names and IDs, surfaces `options.choices` for select fields, and shows primary-field names.

### Common Patterns
- ```
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?maxRecords=5" \
...```
- ```
curl -s "https://api.airtable.com/v0/meta/bases" \
...```
- ```
curl -s "https://api.airtable.com/v0/meta/bases/$BASE_ID/tables" \
...```
- Create a **Personal Access Token (PAT)** at https://airtable.com/create/tokens (tokens start with `pat...`).
- Grant these scopes (minimum):
- **Important:** in the same token UI, add each base you want to access to the token's **Access** list. PATs are scoped pe

### Integration Points
- the
- this
- Python
- ed
- JSON

## Verification
- the schema (step 3) before concluding a field is missing.

## Child DOX Index
- No child directories found (references/, templates/, scripts/)

---
*Generated: 2026-07-28 17:31*
*Source: SKILL.md frontmatter + content analysis*
