# crimea-job-search — Skill

## Purpose
CLI tool for searching jobs on hh.ru in Crimea/Simferopol. Async hh.ru API client with SQLite cache, filtering, and multiple output formats. Designed for autonomous operation via cron.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: hh-ru, job-search, crimea, simferopol, async, cli, telegram
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: CLI tool for searching jobs on hh
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `scripts/` | Helper scripts (1 files) |