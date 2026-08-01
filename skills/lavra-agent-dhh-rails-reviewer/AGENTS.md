# lavra-agent-dhh-rails-reviewer — Skill

## Purpose
Brutally honest Rails code review from DHH's perspective. Identifies anti-patterns, JavaScript framework contamination, unnecessary abstractions, and Rails convention violations.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Brutally honest Rails code review from DHH's perspective
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