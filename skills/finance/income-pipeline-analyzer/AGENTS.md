# income-pipeline-analyzer — Skill

## Purpose
Use when analyzing CPA/arbitrage scheme readiness — 50 schemes, blocker categorization (LANDING_PAGE, VIDEO_SCRIPT, BOT, MANUAL_ACCOUNT, API_KEY, AD_BUDGET), code-unblockable identification

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Use when analyzing CPA/arbitrage scheme readiness — 50 schemes, blocker categorization (LANDING_PAGE, VIDEO_SCRIPT, BOT, MANUAL_ACCOUNT, API_KEY, AD_BUDGET), code-unblockable identification
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