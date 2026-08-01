# skill-factory — Skill

## Purpose
A meta-skill that silently watches your workflows and automatically generates reusable Hermes skills from them.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: meta, automation, skills, learning, productivity, workflow-capture
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: A meta-skill that silently watches your workflows and automatically generates reusable Hermes skills from them
**Common patterns**: - skill-evolution
- skill-indexer
- self-improvement-runtime
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| (no child directories) | |