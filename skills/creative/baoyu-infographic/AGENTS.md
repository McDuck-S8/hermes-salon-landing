# baoyu-infographic — Skill Contract

## Purpose
No description provided

## Ownership
Hermes Agent — self-maintained via skill-forge. Category: general.

## Local Contracts
### Triggers
- When the task matches the skill's domain and purpose

### Required Tools
- write_file

### Configuration
- Standard skill configuration via SKILL.md frontmatter

## Work Guidance
### When to Use
- Trigger this skill when the user asks to create an infographic, visual summary, information graphic, or uses terms like "信息图", "可视化", or "高密度信息大图". The user provides content (text, file path, URL, or topic) and optionally specifies layout, style, aspect ratio, or language.
- |
- Trigger this skill when the user asks to create an infographic, visual summary, information graphic, or uses terms like "信息图", "可视化", or "高密度信息大图". The user provides content (text, file path, URL, or topic) and optionally specifies layout, style, aspect ratio, or language.

### Common Patterns
- Save source content (file path or paste → `source.md` using `write_file`)
- Analyze: topic, data type, complexity, tone, audience
- Detect source language and user language
- Extract design instructions from user input
- Save analysis to `analysis.md`
- Preserve source data faithfully — no summarization or rephrasing (but **strip any credentials, API keys, tokens, or secr

### Integration Points
- the
- references
- when
- Trigger
- as-is

## Verification
- Keyword Shortcuts first**: If user input matches a keyword from the **Keyword Shortcuts** table, auto-select the associated layout and prioritize associated styles as top recommendations. Skip content-based layout inference.

## Child DOX Index
- **references/** — 5 files: analysis-framework.md, base-prompt.md, layouts, structured-content-template.md, styles

---
*Generated: 2026-07-28 17:31*
*Source: SKILL.md frontmatter + content analysis*
