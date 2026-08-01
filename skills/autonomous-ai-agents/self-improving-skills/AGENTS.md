# self-improving-skills — Skill

## Purpose
Skills that rewrite themselves based on evaluation feedback. Uses Gemini/ADK to run evals, find failure patterns, and patch the SKILL.md + scripts. From awesome-llm-apps/agent_skills/self-improving-ag

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Skills that rewrite themselves based on evaluation feedback
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (6 files) |
| `scripts/` | Helper scripts (4 files) |