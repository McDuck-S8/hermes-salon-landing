# Self-Improving Skills - Failure Pattern Library

This file accumulates failure patterns discovered during self-improvement cycles.
Each entry documents a pattern, how to detect it, and the fix strategy.

---

## Pattern: missing_infrastructure
**Detection**: Skill has `self_improving: true` but lacks evals/, scripts/, references/
**Fix**: Create complete infrastructure:
- evals/cases.yaml - test cases
- evals/rubric.md - scoring criteria  
- evals/run_eval.py - runner
- scripts/improve.py - analyzer
- scripts/verify.py - verifier
- scripts/patch_applier.py - patcher
- references/patterns.md - this file
- .improvement-log.json - audit log

---

## Pattern: missing_safety_guard
**Detection**: Improve.py proposes >3 patches or no max_patches check
**Fix**: Add hard limit in improve.py:
```python
MAX_PATCHES_PER_CYCLE = 3
patches = patches[:MAX_PATCHES_PER_CYCLE]
```

---

## Pattern: missing_failure_categorization
**Detection**: Failures reported without pattern labels
**Fix**: Add pattern detection logic in improve.py using FAILURE_PATTERNS dict

---

## Pattern: no_revert_on_regression
**Detection**: Verify.py doesn't compare pass rates or trigger revert
**Fix**: Implement verify.py with pass rate comparison and revert logic

---

## Pattern: tool_misuse
**Detection**: Repeated wrong tool arguments, hallucinated tool names
**Fix**: Add tool usage examples and validation to SKILL.md

---

## Pattern: missing_validation
**Detection**: No input validation before API/tool calls
**Fix**: Add explicit validation steps in skill instructions

---

## Pattern: edge_case
**Detection**: Consistent failure on empty/null/boundary inputs
**Fix**: Add explicit `if empty: return default` branches

---

## Pattern: ambiguous_instruction
**Detection**: Multiple valid outputs for same input
**Fix**: Add decision tree or output schema with examples

---

## Pattern: context_leak
**Detection**: Test passes in isolation, fails in sequence
**Fix**: Add state reset/isolation between test runs

---

## Pattern: hallucinated_output
**Detection**: Output format doesn't match expected schema
**Fix**: Define output schema (JSON Schema/TypeScript) + validation step

---

## Pattern: no_eval_results
**Detection**: No eval_results.json found when running improve
**Fix**: Run evals first, then improve

---

*Auto-updated by self-improvement cycles. Do not edit manually - patches will append here.*