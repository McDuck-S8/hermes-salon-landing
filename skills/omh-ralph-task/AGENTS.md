# omh-ralph-task — Skill

## Purpose
Executor's discipline for a single omh-ralph task — task-envelope contract, file-scope rigidity,
stash-verify-against-HEAD for sibling-task isolation, commit-author override, structured report-back sh

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: execution, task-discipline, isolation, omh
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Executor's discipline for a single omh-ralph task — task-envelope contract, file-scope rigidity,
stash-verify-against-HEAD for sibling-task isolation, commit-author override, structured report-back sh
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