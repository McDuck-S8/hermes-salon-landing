# lavra-agent-migration-drift-detector — Skill

## Purpose
Detects unrelated or out-of-sync schema/migration changes in PRs across Rails, Alembic, Prisma, Drizzle, and Knex. Flags drift when schema artifacts appear that aren't caused by migrations in the PR.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Detects unrelated or out-of-sync schema/migration changes in PRs across Rails, Alembic, Prisma, Drizzle, and Knex
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