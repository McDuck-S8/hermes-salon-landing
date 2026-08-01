# herdr-multiagent — Skill

## Purpose
Multi-agent orchestration via Herdr terminal workspace manager.
Creates isolated spaces/panes per agent role, shared message bus via Knowledge Cube,
persistent sessions, and task templates for orchest

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: herdr, multi-agent, orchestration, terminal, workspace, delegation
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Multi-agent orchestration via Herdr terminal workspace manager
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
| `templates/` | Templates (5 files) |
| `scripts/` | Helper scripts (5 files) |