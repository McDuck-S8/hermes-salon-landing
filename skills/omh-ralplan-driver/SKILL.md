---
name: omh-ralplan-driver
description: |
  Dispatcher playbook for driving an omh-ralplan run — context-package authoring, round dispatch, distillation, final review.
version: 1.0.0
category: autonomous-ai-agents
tags:
  - planning
  - driver
  - dispatch
  - omh
---

# OMH RAL Plan Driver

## Purpose
Provides the dispatcher's playbook for driving an omh-ralplan run. Handles context-package authoring,
round dispatch, distillation of rounds, and final review.

## Usage
```python
from scripts.crystal.omh_integration import OMHIntegration
omh = OMHIntegration()
driver_result = omh.run_ralplan_driver("plan_id_or_context")
```

## Responsibilities
- **Context Package** — Author comprehensive context for the planning team
- **Round Dispatch** — Manage Planner → Architect → Critic rounds with timeouts
- **Distillation** — Synthesize round outputs into actionable plan updates
- **Final Review** — Orchestrate Step-7 final architect review

## Outputs
- Dispatch log with round-by-round progression
- Distilled plan after each round
- Final consensus plan artifact

## References
- `references/brief-template.md`
- `references/caller-examples.md`
- `references/state-schema.md`