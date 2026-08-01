# cron-maintenance — Skill

## Purpose
Clean up, diagnose, and maintain Hermes cron jobs. Find dead jobs (non-existent scripts), fix failing scripts, reduce error rate. Use when cron error rate is high or user says 'fix cron'.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: cron, maintenance, cleanup, devops, system-health
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Clean up, diagnose, and maintain Hermes cron jobs
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (16 files) |