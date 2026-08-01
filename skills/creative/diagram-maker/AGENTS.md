# diagram-maker — Skill

## Purpose
Generate syntactically correct Mermaid diagrams from natural language. Covers flowcharts, sequence, class, ER, state, Gantt, pie, and more.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: diagrams, mermaid, visualization, architecture, documentation
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Generate syntactically correct Mermaid diagrams from natural language
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (2 files) |