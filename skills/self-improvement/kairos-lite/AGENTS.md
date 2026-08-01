# kairos-lite — Skill

## Purpose
Build a lightweight proactive mode with scheduled checks, sleep intervals, concise user briefs, and expiry safeguards so an agent can work in the background without becoming an uncontrolled daemon.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Build a lightweight proactive mode with scheduled checks, sleep intervals, concise user briefs, and expiry safeguards so an agent can work in the background without becoming an uncontrolled daemon
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
| `scripts/` | Helper scripts (1 files) |