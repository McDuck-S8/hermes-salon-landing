# mandatory-system-health-reflex — Skill

## Purpose
Pattern for preventing silent system failures by making health checks mandatory reflexes, not optional skills. Includes syscheck script, AGENTS.md enforcement, watchdog alerts, and gateway persistence

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: devops, system-health, self-healing, silent-failure-prevention, mandatory-reflex
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Pattern for preventing silent system failures by making health checks mandatory reflexes, not optional skills
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