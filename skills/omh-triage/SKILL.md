---
name: omh-triage
description: |
  Multi-role consensus triage of an issue backlog — Maintainer (code-anchored) + Skeptic (pruning).
  More roles coming after lived rounds.
version: 1.0.0
category: autonomous-ai-agents
tags:
  - triage
  - backlog
  - consensus
  - omh
---

# OMH Triage

## Purpose
Multi-role consensus triage of an issue backlog. Currently two roles: Maintainer (code-anchored assessment) and Skeptic (pruning).
More roles will be added after lived rounds.

## Usage
```python
from scripts.crystal.omh_integration import OMHIntegration
omh = OMHIntegration()
triage = omh.run_triage(["issue1", "issue2", "issue3"])
```

## Roles
- **Maintainer** — Code-anchored assessment: knows the codebase, evaluates technical debt, architectural fit
- **Skeptic** — Pruning: challenges necessity, questions ROI, identifies duplicates, pushes for deletion

## Process
1. **Backlog Audit** — Pre-flight scan of all issues
2. **Role Pass** — Maintainer and Skeptic independently evaluate each issue
3. **Distillation** — Merge assessments, resolve conflicts
4. **User Sign-off** — Present triaged backlog for approval

## Outputs
- Triaged backlog with keep/archive/delete decisions
- Rationale per issue
- Prioritized action items

## Status
v0.1 — basic two-role triage. More roles coming after lived rounds.

## References
- `references/triage-doc-template.md`
- `references/state-schema.md`