# autonomous-coding-with-opencode-zen — Skill

## Purpose
Delegate coding tasks to OpenCode Zen agent and capture knowledge from the outcome. Use when you need autonomous code generation, refactoring, or debugging with the OpenCode CLI.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Delegate coding tasks to OpenCode Zen agent and capture knowledge from the outcome
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (8 files) |