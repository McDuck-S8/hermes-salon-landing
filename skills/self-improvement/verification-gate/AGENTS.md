# verification-gate — Skill

## Purpose
Run a read-only verification pass after implementation to check whether completion claims are real, validation actually ran, and obvious edge cases or regressions were missed.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Run a read-only verification pass after implementation to check whether completion claims are real, validation actually ran, and obvious edge cases or regressions were missed
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (7 files) |
| `scripts/` | Helper scripts (1 files) |