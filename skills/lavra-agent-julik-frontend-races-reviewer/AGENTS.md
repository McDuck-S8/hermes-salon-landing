# lavra-agent-julik-frontend-races-reviewer — Skill

## Purpose
Reviews JavaScript and Stimulus code for race conditions, timing issues, and DOM irregularities. Checks Hotwire/Turbo compatibility, event handler cleanup, timer cancellation. Use after JavaScript cha

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Reviews JavaScript and Stimulus code for race conditions, timing issues, and DOM irregularities
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| (no child directories) | |