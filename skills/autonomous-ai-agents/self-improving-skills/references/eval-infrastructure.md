# Self-Improving Skills Eval Infrastructure — Implementation Notes

## Built: 2026-07-23 (cron job)

## What Was Created

### evals/
- **cases.yaml** — 5 test cases covering the improvement pipeline
- **rubric.md** — PASS/PARTIAL/FAIL scoring with 85% threshold
- **run_eval.py** — Validates all scripts exist with required functions, exits 1 on FAIL

### scripts/
- **improve.py** — 10 failure patterns detected, proposes SKILL.md/script patches (max 3/cycle)
- **verify.py** — Applies patches, re-runs evals, compares pass rates, auto-reverts on regression
- **patch_applier.py** — Low-level patch ops (replace/insert/delete/create/diff) with git revert

### references/
- **failure-patterns.md** — 8 patterns with symptoms, root causes, fix templates
- **improvement-strategies.md** — 8 strategies with selection guide and patch format examples

## Current Test Results

| Test | Status | Issue |
|------|--------|-------|
| improve_analyzes_failures | FAIL | Expects `proposed_patches.json` output, improve.py saves `improvement_analysis_*.json` |
| improve_respects_safety_guards | PASS | 3-patch limit enforced |
| verify_reruns_evals | PASS | re_run_evals function present |
| verify_detects_regression | PASS | Regression detection + revert logic present |
| eval_runs_all_cases | PASS | run_tests function + last_results.json output |
| eval_scores_correctly | PASS | PASS/FAIL/PARTIAL constants present |
| eval_outputs_json | PASS | JSON output to last_results.json |
| patch_applier_exists | FAIL | Expects `revert_patches` function, has revert via git checkout |

## Fixes Needed (Next Cycle)

1. **improve.py** → write patches to `evals/proposed_patches.json` (not analysis file)
2. **patch_applier.py** → add explicit `revert_patches()` function wrapper
3. Run evals again after fixes to reach 100%

## Usage

```bash
# Run evals
python evals/run_eval.py

# Run improvement cycle on a skill (requires GEMINI_API_KEY)
python scripts/improve.py <skill_dir>

# Verify patches
python scripts/verify.py <skill_dir> <patches.json>

# Apply + verify in one step
python scripts/patch_applier.py <skill_dir> <patches.json>
```

## Integration with 6 Production Skills

The 6 skills with `self_improving: true` in autonomous-ai-agents/:
- advisor-orchestrator-worker
- ai-financial-coach
- always-on-agent
- mcp-integration-pattern
- multi-agent-researcher
- self-improving-skills (this skill)

Each needs eval infrastructure created before the improvement cycle can run.