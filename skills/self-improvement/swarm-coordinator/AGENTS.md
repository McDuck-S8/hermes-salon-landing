# swarm-coordinator — Skill

## Purpose
Coordinate multiple agents by splitting work into research, synthesis, implementation, and verification, assigning ownership, and keeping the coordinator focused on integration rather than raw explora

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Coordinate multiple agents by splitting work into research, synthesis, implementation, and verification, assigning ownership, and keeping the coordinator focused on integration rather than raw explora
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