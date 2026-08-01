# rss-monitoring-cron — Skill

## Purpose
RSS/Atom feed monitoring cron job — fetches CPA, AI, and tech feeds, caches results, delivers digest. Includes cron path fix pattern.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: cron, rss, monitoring, digest, automation
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: RSS/Atom feed monitoring cron job — fetches CPA, AI, and tech feeds, caches results, delivers digest
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (13 files) |