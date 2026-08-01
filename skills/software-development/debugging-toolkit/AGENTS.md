# debugging-toolkit — Skill

## Purpose
Unified debugging toolkit for Hermes: systematic-debugging + python-debugpy + node-inspect-debugger + debugging-hermes-tui-commands. One skill to load, four tools at hand.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Unified debugging toolkit for Hermes: systematic-debugging + python-debugpy + node-inspect-debugger + debugging-hermes-tui-commands
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