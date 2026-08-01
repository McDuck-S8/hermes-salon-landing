# knowledge-cube-gap-patch — Skill

## Purpose
Clean knowledge_cube.db — classify white spots, tag/confidence-bulk-update records, create deferred tasks. Run after scheme rejections or before major strategy shifts.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: knowledge-cube, gap-patch, cleanup, classification, cpa
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Clean knowledge_cube
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| (no child directories) | |