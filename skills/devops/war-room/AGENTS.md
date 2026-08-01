# war-room — Skill

## Purpose
War Room pattern from AI-First Business Playbook — multi-agent council with /standup and /discuss commands. Agents respond independently, consolidator synthesizes.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: War Room pattern from AI-First Business Playbook — multi-agent council with /standup and /discuss commands
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (5 files) |
| `templates/` | Templates (1 files) |
| `scripts/` | Helper scripts (2 files) |