# skill-evolution — Skill

## Purpose
Auto-evolve skills from Knowledge Cube — index, detect gaps, create/update skills automatically

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: skills, evolution, auto-update, knowledge-cube, self-improvement
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Auto-evolve skills from Knowledge Cube — index, detect gaps, create/update skills automatically
**Common patterns**: - self-improvement-runtime
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (8 files) |