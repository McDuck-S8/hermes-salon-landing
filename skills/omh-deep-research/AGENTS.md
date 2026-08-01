# omh-deep-research — Skill

## Purpose
Multi-phase web research: decompose topic → parallel search → synthesize findings → verify citations.
Outputs structured research report with sources. Part of OMH pipeline.


## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: research, web-search, synthesis, citations, omh
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Multi-phase web research: decompose topic → parallel search → synthesize findings → verify citations
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