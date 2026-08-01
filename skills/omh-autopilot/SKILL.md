---
name: omh-autopilot
description: |
  Full pipeline composing all three skills end-to-end: research → interview → plan → execute.
  Entry point for unfamiliar domains.
version: 1.0.0
category: autonomous-ai-agents
tags:
  - pipeline
  - autopilot
  - end-to-end
  - omh
---

# OMH Autopilot

## Purpose
Full pipeline composing all OMH skills end-to-end: research → interview → plan → execute.
Recommended for unfamiliar domains where you need the full structured workflow.

## Usage
```python
from scripts.crystal.omh_integration import OMHIntegration
omh = OMHIntegration()
result = omh.run_autopilot("domain description", "optional goal")
```

## Pipeline
```
research (omh-deep-research)
    → interview (omh-deep-interview)
    → plan (omh-ralplan + omh-ralplan-driver)
    → execute (omh-ralph + omh-ralph-driver)
```

## Modes
- **Full Autopilot** — All phases autonomous, final review gate only
- **Guided Autopilot** — Human checkpoints at phase boundaries
- **Driver Mode** — You drive the dispatchers, skills execute

## Outputs
- Research report (from deep-research)
- Requirements spec (from deep-interview)
- Consensus plan (from ralplan)
- Working artifacts (from ralph)

## Dependencies
- All OMH skills
- Crystal Knowledge Cube
- Agent Reach (for research phase)

## References
- `references/state-schema.md`
- `references/adr-template.md`
- `references/architect-final-review-template.md`