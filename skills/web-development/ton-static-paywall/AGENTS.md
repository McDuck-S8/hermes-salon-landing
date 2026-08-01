# ton-static-paywall — Skill

## Purpose
Add TON Connect paywall to static HTML — for demos/education only. NOT for commercial payments (no server-side verification possible)

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: ton, web3, paywall, ton-connect, static-site, demo-only, education, content-locking
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Add TON Connect paywall to static HTML — for demos/education only
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