# agent-reach — Skill

## Purpose
Capability layer giving Hermes Agent internet access: YouTube transcripts, web search/read, GitHub, Twitter/X, Reddit, Bilibili, RSS, Exa semantic search. Auto-updates backends when platforms change.


## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: web-access, youtube, search, github, social-media, rss, capability-layer
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Capability layer giving Hermes Agent internet access: YouTube transcripts, web search/read, GitHub, Twitter/X, Reddit, Bilibili, RSS, Exa semantic search
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