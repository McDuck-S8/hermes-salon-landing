# task-driven-agent — Skill

## Purpose
Build an autonomous AI agent that interprets natural language tasks via LLM and executes them through modular skill modules. Covers the agent-core + skill architecture, project structure, skill interf

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: agent, architecture, telegram, llm, modular, skills, automation
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Build an autonomous AI agent that interprets natural language tasks via LLM and executes them through modular skill modules
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