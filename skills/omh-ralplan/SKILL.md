---
name: omh-ralplan
description: |
  Consensus planning: Planner → Architect → Critic debate until agreement.
  Produces a concrete, actionable plan with risk assessment.
version: 1.0.0
category: autonomous-ai-agents
tags:
  - planning
  - consensus
  - debate
  - omh
---

# OMH RAL Plan

## Purpose
Generates concrete, actionable plans through structured multi-role debate until consensus is reached.
Uses three roles: Planner (proposes), Architect (refines), Critic (challenges) — iterates until agreement.

## Usage
```python
from scripts.crystal.omh_integration import OMHIntegration
omh = OMHIntegration()
plan = omh.run_ralplan("requirements or problem statement")
```

## Roles
- **Planner** — Proposes initial plan structure, milestones, tasks
- **Architect** — Refines with technical details, dependencies, resources
- **Critic** — Challenges assumptions, identifies risks, gaps, edge cases

## Loop
1. Planner proposes
2. Architect refines or rejects
3. Critic challenges or approves
4. Repeat until all three agree (consensus)

## Outputs
- Consensus plan with milestones, tasks, dependencies
- Risk assessment per milestone
- Resource estimates
- ADR (Architecture Decision Record)

## Dependencies
- OMH Deep Research (for context gathering)
- Crystal Knowledge Cube

## References
- `references/adr-template.md`
- `references/architect-goal-template.md`
- `references/brief-template.md`
- `references/critic-goal-template.md`
- `references/orchestrator-review-template.md`
- `references/planner-goal-template.md`
- `references/scoring-rubric.md`
- `references/state-schema.md`