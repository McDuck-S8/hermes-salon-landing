# session-state-isolation — Skill

## Purpose
Session State Isolation - full reset of transient flags on new session connection. Pattern from Mark-XLVIII: _interrupted, _vision_busy, _pending_vision etc reset completely, preventing state leakage 

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: session, state, isolation, transient-flags, mark-xlviii, self-healing
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Session State Isolation - full reset of transient flags on new session connection
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
| `templates/` | Templates (1 files) |