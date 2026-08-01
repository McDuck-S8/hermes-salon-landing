# daily-monitoring — Skill

## Purpose
Automated daily monitoring — RSS feeds, YouTube channels, aggregator, HTML digest. One-stop setup for multi-source data collection and daily briefing.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: monitoring, rss, youtube, digest, cron, reporting
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Automated daily monitoring — RSS feeds, YouTube channels, aggregator, HTML digest
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