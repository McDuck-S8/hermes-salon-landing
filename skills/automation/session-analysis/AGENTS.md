# session-analysis — Skill

## Purpose
Analyze recent sessions, extract tasks, identify patterns, and generate consultation reports. Covers the brain-auto-consult workflow and similar recurring analysis jobs.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: user asks to analyze recent sessions, user asks "what have I been working on", cron job runs session analysis or auto-consult, user asks for patterns across sessions, user asks for recommendations based on session history
- **Required tools**: sessions, analysis, cron, reporting, patterns
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Analyze recent sessions, extract tasks, identify patterns, and generate consultation reports
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