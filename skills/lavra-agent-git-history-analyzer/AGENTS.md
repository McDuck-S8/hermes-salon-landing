# lavra-agent-git-history-analyzer — Skill

## Purpose
Analyzes git history to understand code evolution, trace origins of specific code patterns, identify key contributors and their expertise areas, and extract development patterns from commit history.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Analyzes git history to understand code evolution, trace origins of specific code patterns, identify key contributors and their expertise areas, and extract development patterns from commit history
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