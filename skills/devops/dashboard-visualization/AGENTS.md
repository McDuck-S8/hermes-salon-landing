# dashboard-visualization — Skill

## Purpose
Build and maintain interactive management dashboards for agent work — kanban with drag & drop, task CRUD, cron control, system health.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Build and maintain interactive management dashboards for agent work — kanban with drag & drop, task CRUD, cron control, system health
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (3 files) |
| `scripts/` | Helper scripts (2 files) |