# lavra-agent-architecture-strategist — Skill

## Purpose
Analyzes code changes from an architectural perspective - evaluating system design, component boundaries, SOLID compliance, and dependency analysis. Use for structural changes, new services, or refact

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Analyzes code changes from an architectural perspective - evaluating system design, component boundaries, SOLID compliance, and dependency analysis
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