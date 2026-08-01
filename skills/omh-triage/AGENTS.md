# omh-triage — Skill

## Purpose
Multi-role consensus triage of an issue backlog — Maintainer (code-anchored) + Skeptic (pruning).
More roles coming after lived rounds.


## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: triage, backlog, consensus, omh
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Multi-role consensus triage of an issue backlog — Maintainer (code-anchored) + Skeptic (pruning)
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