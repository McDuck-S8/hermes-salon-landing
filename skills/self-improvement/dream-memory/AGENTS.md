# dream-memory — Skill

## Purpose
Consolidate recent logs, sessions, and existing memory files into durable topic memories, normalize dates, prune stale entries, and keep MEMORY.md short enough for prompt use.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Consolidate recent logs, sessions, and existing memory files into durable topic memories, normalize dates, prune stale entries, and keep MEMORY
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (3 files) |
| `scripts/` | Helper scripts (1 files) |