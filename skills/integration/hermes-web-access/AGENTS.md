# hermes-web-access — Skill

## Purpose
Web access tools for Hermes autonomous research via Agent Reach capability layer.
Provides YouTube search/transcript, web search/read, GitHub read, RSS fetch.
Uses Agent Reach capability layer for bac

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: web-access, youtube, search, github, rss, agent-reach
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Web access tools for Hermes autonomous research via Agent Reach capability layer
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