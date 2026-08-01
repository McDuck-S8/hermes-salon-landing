# baoyu-comic — Skill Contract

## Purpose
No description provided

## Ownership
Hermes Agent — self-maintained via skill-forge. Category: general.

## Local Contracts
### Triggers
- use all defaults" pass after one timeout. If the user is genuinely absent, they will be equally absent for all five questions — but they can correct visible defaults when

### Required Tools
- terminal
- curl

### Configuration
- Standard skill configuration via SKILL.md frontmatter

## Work Guidance
### When to Use
- Trigger this skill when the user asks to create a knowledge/educational comic, biography comic, tutorial comic, or uses terms like "知识漫画", "教育漫画", or "Logicomix-style". The user provides content (text, file path, URL, or topic) and optionally specifies art style, tone, layout, aspect ratio, or language.
- Trigger this skill when the user asks to create a knowledge/educational comic, biography comic, tutorial comic, or uses terms like "知识漫画", "教育漫画", or "Logicomix-style". The user provides content (text, file path, URL, or topic) and optionally specifies art style, tone, layout, aspect ratio, or language.

### Common Patterns
- User-specified language (explicit option)
- User's conversation language
- Source content language
- Read the URL from the tool result
- Fetch the image bytes using an **absolute** output path, e.g.
- File path(s) → copy to `refs/NN-ref-{slug}.{ext}` alongside the comic output for provenance

### Integration Points
- Hermes
- batch
- ed
- r-specified
- it

## Verification
- existing directory
- Existing?] → [Confirm: Style + Reviews] → Storyboard → [Review?] → Prompts → [Review?] → Images → Complete
- existing directory | Handle conflicts |

## Child DOX Index
- **references/** — 12 files: analysis-framework.md, art-styles, auto-selection.md, base-prompt.md, character-template.md

---
*Generated: 2026-07-28 17:31*
*Source: SKILL.md frontmatter + content analysis*
