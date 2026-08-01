# design-toolkit — Skill

## Purpose
Unified design toolkit for Hermes: hallmark (anti-AI-slop) + claude-design + design-md + popular-web-designs + anti-slop-design. One skill to load, all design engines at hand.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Unified design toolkit for Hermes: hallmark (anti-AI-slop) + claude-design + design-md + popular-web-designs + anti-slop-design
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (2 files) |