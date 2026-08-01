# omh-autopilot — Skill

## Purpose
Full pipeline composing all three skills end-to-end: research → interview → plan → execute.
Entry point for unfamiliar domains.


## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: pipeline, autopilot, end-to-end, omh
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Full pipeline composing all three skills end-to-end: research → interview → plan → execute
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