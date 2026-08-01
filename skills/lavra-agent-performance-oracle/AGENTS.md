# lavra-agent-performance-oracle — Skill

## Purpose
Analyzes code for performance bottlenecks, algorithmic complexity, N+1 queries, memory leaks, caching opportunities, and scalability concerns. Projects performance at 10x/100x/1000x volumes.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Analyzes code for performance bottlenecks, algorithmic complexity, N+1 queries, memory leaks, caching opportunities, and scalability concerns
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