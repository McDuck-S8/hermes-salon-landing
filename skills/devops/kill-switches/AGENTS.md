# kill-switches — Skill

## Purpose
Kill Switches pattern from AI-First Business Playbook — 6 hot-reloadable boolean gates for every dangerous boundary. Flip one, system refuses at that boundary in ~2 seconds.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Kill Switches pattern from AI-First Business Playbook — 6 hot-reloadable boolean gates for every dangerous boundary
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
| `scripts/` | Helper scripts (1 files) |