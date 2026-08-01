# lavra-agent-pattern-recognition-specialist — Skill

## Purpose
Analyzes code for design patterns, anti-patterns, naming conventions, code duplication, and architectural boundary violations. Produces structured reports with actionable refactoring recommendations.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Analyzes code for design patterns, anti-patterns, naming conventions, code duplication, and architectural boundary violations
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