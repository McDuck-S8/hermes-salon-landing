# user-perspective — Skill

## Purpose
Force user-centric perspective before creating ANY artifact. 4 mandatory questions.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: perspective, user-centric, artifact-validation, anti-self-referential
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Force user-centric perspective before creating ANY artifact
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