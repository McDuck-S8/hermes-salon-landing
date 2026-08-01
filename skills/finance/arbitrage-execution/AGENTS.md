# arbitrage-execution — Skill

## Purpose
Autonomous execution of arbitrage schemes from ARBITRAGE_WORKSHOP.md — traffic source selection, offer connection, ЦА template, deployment, tracking, withdrawal verification

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: arbitrage, revenue, cpa, traffic, execution
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Autonomous execution of arbitrage schemes from ARBITRAGE_WORKSHOP
**Common patterns**: - earning-with-ai
- self-improvement/action-over-documentation
- self-improvement/closed-loop-autonomy
- finance-core
- autonomous-system-operations
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (8 files) |
| `templates/` | Templates (1 files) |