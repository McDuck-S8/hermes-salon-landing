# lavra-agent-spec-flow-analyzer — Skill

## Purpose
Analyzes specifications, plans, and feature descriptions to map all possible user flows, identify gaps and ambiguities, and surface critical questions. Use when reviewing feature specs or validating i

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Analyzes specifications, plans, and feature descriptions to map all possible user flows, identify gaps and ambiguities, and surface critical questions
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