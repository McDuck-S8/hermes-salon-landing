# knowledge-filter — Skill

## Purpose
Three-stage knowledge filter between parsers and Knowledge Cube. Integrates human-source (personal relevance), audience-analyzer (market relevance), skill-pathfinder (deduplication). Only passes knowl

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: knowledge-filter, pipeline, human-source, audience-analyzer, skill-pathfinder, deduplication
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Three-stage knowledge filter between parsers and Knowledge Cube
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
| `templates/` | Templates (1 files) |
| `scripts/` | Helper scripts (4 files) |