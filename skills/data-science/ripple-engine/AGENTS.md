# ripple-engine — Skill

## Purpose
Ripple Engine: structured analytical methodology for Knowledge Cube entries. Extracts aspects, checks constraint conflicts, identifies gaps, generates new keys, scores entries on key_strength/confiden

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: ripple-engine, knowledge-cube, analysis, constraint-checking, gap-analysis, scoring
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Ripple Engine: structured analytical methodology for Knowledge Cube entries
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