---
name: omh-ralph-driver
description: |
  Dispatcher playbook for driving an omh-ralph run — plan-shape, parallel batching, evidence gathering, verifier discipline, strike categorization, Step-7 final architect review, commit hygiene.
version: 1.0.0
category: autonomous-ai-agents
tags:
  - execution
  - driver
  - dispatch
  - omh
---

# OMH Ralph Driver

## Purpose
Dispatcher's playbook for driving an omh-ralph run. Manages plan-shape validation, parallel batching of tasks,
evidence gathering, verifier discipline, strike categorization, Step-7 final architect review, and commit hygiene.

## Usage
```python
from scripts.crystal.omh_integration import OMHIntegration
omh = OMHIntegration()
driver_result = omh.run_ralph_driver("plan_id")
```

## Responsibilities
- **Plan Shape Validation** — Ensure plan is well-formed before execution
- **Parallel Batching** — Dispatch independent tasks to parallel executors
- **Evidence Gathering** — Collect test results, logs, screenshots as verification
- **Verifier Discipline** — Enforce verification before marking tasks complete
- **Strike Categorization** — Classify failures (flake, bug, spec gap, env issue)
- **Step-7 Final Architect Review** — Mandatory final review before commit
- **Commit Hygiene** — Atomic commits, meaningful messages, linked issues

## Outputs
- Dispatch log with task→executor mapping
- Evidence bundles per task
- Strike categorization report
- Final architect review artifact
- Clean commit history

## References
- `references/state-schema.md`
- `references/architect-final-review-template.md`
- `references/executor-goal-template.md`
- `references/verifier-goal-template.md`
- `references/sibling-executor-preemption.md`
- `references/sibling-isolation-pattern.md`
- `references/caller-examples.md`