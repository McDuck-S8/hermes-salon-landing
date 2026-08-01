---
name: omh-ralph
description: |
  Verified execution: implement → verify → iterate until done.
  Ensures every proposal produces a working artifact with passing tests.
version: 1.0.0
category: autonomous-ai-agents
tags:
  - execution
  - verification
  - iteration
  - omh
---

# OMH Ralph

## Purpose
Executes plans with built-in verification loop: implement → verify → iterate until the artifact works and tests pass.
No proposal is considered complete until it has a verified, working artifact.

## Usage
```python
from scripts.crystal.omh_integration import OMHIntegration
omh = OMHIntegration()
result = omh.run_ralph("plan_id_or_spec")
```

## Phases
1. **Implement** — Write code/create artifact per specification
2. **Verify** — Run tests, linting, type checks, manual verification
3. **Iterate** — Fix failures, repeat until all checks pass
4. **Document** — Record what was built, how to run, known limitations

## Quality Gates
- All automated tests pass
- Linting/type checks clean
- Manual smoke test passes
- Documentation updated
- No regression in existing tests

## Outputs
- Working artifact (code, config, document)
- Test results log
- Verification report
- Updated documentation

## Dependencies
- OMH RAL Plan (for specification)
- Crystal Executor (for code changes)
- Crystal Feedback Loop (for verification)

## References
- `references/state-schema.md`
- `references/architect-final-review-template.md`
- `references/executor-goal-template.md`
- `references/verifier-goal-template.md`
- `references/sibling-executor-preemption.md`
- `references/sibling-isolation-pattern.md`
- `references/caller-examples.md`