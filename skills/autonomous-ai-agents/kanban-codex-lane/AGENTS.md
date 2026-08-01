# kanban-codex-lane — Skill Contract

## Purpose
No description provided

## Ownership
Hermes Agent — self-maintained via skill-forge. Category: general.

## Local Contracts
### Triggers
- Use the Codex lane when
- use the Codex lane when

### Required Tools
- python
- npm
- bash
- git
- terminal

### Configuration
- Standard skill configuration via SKILL.md frontmatter

## Work Guidance
### When to Use
- Use the Codex lane when all of these are true:
- Use the Codex lane when all of these are true:

### Common Patterns
- ```
TASK_ID="${HERMES_KANBAN_TASK:-t_manual}"
...```
- ```
git -C "$REPO" fetch --all --prune
...```
- ```
git -C "$REPO" worktree remove "$WORKTREE"
...```
- Hermes owns the Kanban lifecycle. Codex must never call `kanban_complete`, `kanban_block`, `kanban_create`, gateway mess
- Hermes owns final acceptance. Treat Codex commits/diffs as untrusted patches until reviewed and verified.
- Hermes owns test execution. Codex may run tests, but those runs are advisory; repeat required verification from Hermes w

### Integration Points
- the
- Use
- market
- d
- Codex

## Verification
- execution. Codex may run tests, but those runs are advisory; repeat required verification from Hermes with the repo's canonical wrapper.

## Child DOX Index
- **templates/** — 1 files: pmb-codex-lane-prompt.md

---
*Generated: 2026-07-28 17:31*
*Source: SKILL.md frontmatter + content analysis*
