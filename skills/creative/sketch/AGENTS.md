# sketch — Skill Contract

## Purpose
No description provided

## Ownership
Hermes Agent — self-maintained via skill-forge. Category: general.

## Local Contracts
### Triggers
- when the user says things like "sketch this
- When NOT to use this
- Use this skill when

### Required Tools
- write_file
- browser_navigate
- terminal

### Configuration
- Standard skill configuration via SKILL.md frontmatter

## Work Guidance
### When to Use
- skill when the user wants to **see a design direction before committing** to one — exploring a UI/UX idea as disposable HTML mockups. The point is to generate 2-3 interactive variants so the user can compare visual directions side-by-side, not to produce shippable code.
- - User wants a production component — use `claude-design` or build it properly
- - The kind of user or use case this variant actually serves

### Common Patterns
- **Feel.** "What should this feel like? Adjectives, emotions, a vibe." — *"calm, editorial, like Linear"* tells you more 
- **References.** "What apps, sites, or products capture the feel you're imagining?" — actual references beat abstract des
- **Core action.** "What's the single most important thing a user does on this screen?" — the variants should all serve th
- **Click a primary action** and something visible happens (state change, modal, toast, navigation feint)
- **See one meaningful state transition** (filter a list, toggle a mode, open/close a panel)
- User wants a production component — use `claude-design` or build it properly

### Integration Points
- rs
- Hermes
- this
- each
- when

## Verification
- variants visually — use Hermes' browser tools.** Don't just write HTML and hope it renders; load each variant and look at it:

## Child DOX Index
- No child directories found (references/, templates/, scripts/)

---
*Generated: 2026-07-28 17:31*
*Source: SKILL.md frontmatter + content analysis*
