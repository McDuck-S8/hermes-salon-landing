# persistent-memory — Skill

## Purpose
File-based memory system for cross-session agent persistence. learnings.md < 100 lines loaded at boot, observations appended in real-time, goals tracked. Replaces broken session_bridge. Use at session

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: memory, persistence, architecture, boot, session-continuity
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: File-based memory system for cross-session agent persistence
**Common patterns**: - auto-wake
- self-improvement
- action-over-documentation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (7 files) |