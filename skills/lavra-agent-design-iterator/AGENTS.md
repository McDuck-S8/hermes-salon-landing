# lavra-agent-design-iterator — Skill

## Purpose
Iteratively refines UI design through N screenshot-analyze-improve cycles. Use PROACTIVELY when design changes aren't coming together after 1-2 attempts, or when user requests iterative refinement.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Iteratively refines UI design through N screenshot-analyze-improve cycles
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