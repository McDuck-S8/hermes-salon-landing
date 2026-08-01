---
name: omh-triage-driver
description: |
  Dispatcher's playbook for driving an omh-triage run — pre-flight backlog audit, role-pass dispatch, distillation, user sign-off gate.
version: 1.0.0
category: autonomous-ai-agents
tags:
  - triage
  - driver
  - dispatch
  - omh
---

# OMH Triage Driver

## Purpose
Dispatcher's playbook for driving an omh-triage run. Handles pre-flight backlog audit, role-pass dispatch,
distillation, and user sign-off gate.

## Usage
```python
from scripts.crystal.omh_integration import OMHIntegration
omh = OMHIntegration()
driver_result = omh.run_triage_driver("backlog_id")
```

## Responsibilities
- **Pre-flight Backlog Audit** — Scan all issues, detect duplicates, stale items
- **Role-Pass Dispatch** — Dispatch to Maintainer and Skeptic in parallel
- **Distillation** — Merge role assessments, resolve conflicts
- **User Sign-off Gate** — Present triaged backlog for approval

## Outputs
- Pre-flight audit report
- Dispatch log with role assignments
- Distilled triage decisions
- User sign-off request

## References
- `references/triage-doc-template.md`
- `references/state-schema.md`