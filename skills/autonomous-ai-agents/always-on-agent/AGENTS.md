# always-on-agent — Skill

## Purpose
Background agent that runs continuously (via cron) to monitor CPA networks,  traffic sources, and competitor changes. Detects new offers, payout changes, creative trends, and market shifts while you s

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Background agent that runs continuously (via cron) to monitor CPA networks,  traffic sources, and competitor changes
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (15 files) |
| `scripts/` | Helper scripts (3 files) |