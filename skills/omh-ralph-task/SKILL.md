---
name: omh-ralph-task
description: |
  Executor's discipline for a single omh-ralph task — task-envelope contract, file-scope rigidity,
  stash-verify-against-HEAD for sibling-task isolation, commit-author override, structured report-back shape.
version: 1.0.0
category: autonomous-ai-agents
tags:
  - execution
  - task-discipline
  - isolation
  - omh
---

# OMH Ralph Task

## Purpose
Defines the executor's discipline for a single omh-ralph task. Enforces task-envelope contract,
file-scope rigidity, stash-verify-against-HEAD for sibling-task isolation, commit-author override,
and structured report-back shape.

## Usage
```python
from scripts.crystal.omh_integration import OMHIntegration
omh = OMHIntegration()
task_result = omh.run_ralph_task("task_envelope")
```

## Contract
- **Task Envelope** — Every task has explicit scope, acceptance criteria, file list
- **File-Scope Rigidity** — Only modify files listed in envelope; no scope creep
- **Sibling Isolation** — Stash changes, verify against HEAD before commit
- **Commit Author Override** — Standardized commit metadata
- **Report-Back Shape** — Structured result with evidence, test results, issues

## Discipline Rules
1. Read full envelope before starting
2. Modify ONLY listed files
3. Run all verification commands before reporting done
4. Stash → verify against HEAD → commit (sibling isolation)
4. Use standardized commit author
5. Report back in exact structure

## Outputs
- Working artifact within envelope
- Verification evidence (test output, lint, type check)
- Structured report-back JSON

## References
- `references/state-schema.md`
- `references/executor-goal-template.md`
- `references/sibling-executor-preemption.md`
- `references/sibling-isolation-pattern.md`
- `references/caller-examples.md`