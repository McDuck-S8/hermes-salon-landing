# lavra-patterns — Skill

## Purpose
Lavra/OpenClaude patterns for skill creation, knowledge capture, and multi-agent orchestration. Use when creating new skills, building knowledge bases, or orchestrating parallel tasks.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Lavra/OpenClaude patterns for skill creation, knowledge capture, and multi-agent orchestration
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