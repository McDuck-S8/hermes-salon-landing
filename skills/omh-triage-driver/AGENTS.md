# omh-triage-driver — Skill

## Purpose
Dispatcher's playbook for driving an omh-triage run — pre-flight backlog audit, role-pass dispatch, distillation, user sign-off gate.


## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: triage, driver, dispatch, omh
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Dispatcher's playbook for driving an omh-triage run — pre-flight backlog audit, role-pass dispatch, distillation, user sign-off gate
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| (no child directories) | |