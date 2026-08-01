# youtube-channel-monitor — Skill

## Purpose
YouTube channel monitoring via yt-dlp cron job — fetches latest videos from configured channels, caches results, detects new videos by comparing against previous snapshot. Includes cron path fix patte

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: cron, youtube, monitoring, yt-dlp, automation, cpa-arbitrage
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: YouTube channel monitoring via yt-dlp cron job — fetches latest videos from configured channels, caches results, detects new videos by comparing against previous snapshot
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