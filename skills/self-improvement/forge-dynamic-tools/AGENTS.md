# forge-dynamic-tools — Skill

## Purpose
Dynamic Tool Creation (Forge-lite) — LLM generates Python code, validates security, executes in isolated sandbox, returns structured result. Enables Hermes to create new tools on-demand without manual

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: forge, code-generation, sandbox, dynamic-tools, self-improvement, deepseek
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Dynamic Tool Creation (Forge-lite) — LLM generates Python code, validates security, executes in isolated sandbox, returns structured result
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (5 files) |
| `templates/` | Templates (1 files) |