# agent-self-identity — Skill

## Purpose
Agent self-identity and completeness discipline — you are not a tool, you use tools. Always verify all items, not a subset.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: self-identity, completeness, verification, autonomy, father-principle, empty-child
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Agent self-identity and completeness discipline — you are not a tool, you use tools
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