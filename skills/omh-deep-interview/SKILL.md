---
name: omh-deep-interview
description: |
  Socratic requirements interview with coverage tracking.
  Clarifies vague requirements into concrete specifications through structured questioning.
version: 1.0.0
category: autonomous-ai-agents
tags:
  - interview
  - requirements
  - socratic
  - omh
---

# OMH Deep Interview

## Purpose
Conducts a Socratic requirements interview to transform vague ideas into concrete, testable specifications.
Uses systematic questioning with coverage tracking to ensure no critical dimension is missed.

## Usage
```python
from scripts.crystal.omh_integration import OMHIntegration
omh = OMHIntegration()
interview = omh.run_deep_interview("vague project idea")
```

## Process
1. **Problem Framing** — Identify the core problem and success criteria
2. **Stakeholder Mapping** — Who are the users, decision-makers, blockers?
3. **Constraint Discovery** — Budget, timeline, tech stack, compliance, team skills
4. **Edge Case Exploration** — Failure modes, abuse cases, scaling limits
5. **Coverage Verification** — Check all dimensions covered (functional, non-functional, operational)

## Outputs
- Structured requirements document (markdown)
- Question traceability matrix
- Assumptions register
- Risk register

## Templates
- `references/spec-template.md` — Output specification format
- `references/scoring-rubric.md` — Interview quality scoring
- `references/state-schema.md` — Interview state schema

## Dependencies
- Crystal Knowledge Cube (for prior context)
- OMH RAL Plan (for planning phase)