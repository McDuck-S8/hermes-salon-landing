# omh-deep-interview — Skill

## Purpose
Socratic requirements interview with coverage tracking.
Clarifies vague requirements into concrete specifications through structured questioning.


## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: interview, requirements, socratic, omh
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Socratic requirements interview with coverage tracking
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