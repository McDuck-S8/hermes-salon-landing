# action-over-documentation — Skill

## Purpose
When user says "изучи и используй" — produce working code, not guides. Anti-летописец pattern.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: workflow, user-preference, anti-pattern
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: When user says "изучи и используй" — produce working code, not guides
**Common patterns**: - self-improvement
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (7 files) |