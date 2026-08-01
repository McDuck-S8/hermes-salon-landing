# memory-extractor — Skill

## Purpose
Extract durable memories from recent conversation turns into user, feedback, project, and reference categories while avoiding stale code-state facts.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Extract durable memories from recent conversation turns into user, feedback, project, and reference categories while avoiding stale code-state facts
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
| `scripts/` | Helper scripts (1 files) |