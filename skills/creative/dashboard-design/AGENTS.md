# dashboard-design — Skill

## Purpose
Build self-contained HTML dashboards that fetch live JSON data and render interactive monitoring views — kanban boards, cron jobs, system health, agent status.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Build self-contained HTML dashboards that fetch live JSON data and render interactive monitoring views — kanban boards, cron jobs, system health, agent status
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (1 files) |
| `scripts/` | Helper scripts (2 files) |