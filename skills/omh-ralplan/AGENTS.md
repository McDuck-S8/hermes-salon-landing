# omh-ralplan — Skill

## Purpose
Consensus planning: Planner → Architect → Critic debate until agreement.
Produces a concrete, actionable plan with risk assessment.


## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: planning, consensus, debate, omh
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Consensus planning: Planner → Architect → Critic debate until agreement
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