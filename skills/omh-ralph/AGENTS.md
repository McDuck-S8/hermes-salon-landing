# omh-ralph — Skill

## Purpose
Verified execution: implement → verify → iterate until done.
Ensures every proposal produces a working artifact with passing tests.


## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: execution, verification, iteration, omh
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Verified execution: implement → verify → iterate until done
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