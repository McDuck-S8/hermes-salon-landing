# Test Fixes Summary (2026-07-28)

## Tests Fixed

| Test | Status | Fix |
|------|--------|-----|
| `test_3_weights_affect_scoring` | ✅ PASS | Added weight bonus in `compute_score()` using `feedback_store.compute_weight()` |
| `test_8_feedback_persists` | ✅ PASS | Added `from datetime import datetime` import |
| `test_4_goal_executor_returns_action` | ⏳ IN PROGRESS | Fixed command splitting + aiogram installed in venv |

## Remaining Failures (5 tests)

| Test | Root Cause | Fix Needed |
|------|------------|------------|
| `test_4_goal_executor_returns_action` | Salon bot needs aiogram in venv | ✅ aiogram installed, command splitting fixed |
| `test_6_goal_executor_detects_already_met` | Same as above | Same fix |
| `test_7_action_log_exists` | `action_log.jsonl` not created by `feedback_store` | Add file logging to `record_outcome()` |
| `test_9_context_loads_all_sections` | "Previous Session" section missing | Add session bridge loading in `session_context.py` |
| `test_12_agent_has_diverse_actions` | Only 5 actions vs 20 required | Add more candidate actions in `evaluate_actions()` |

## Files Modified
- `scripts/autonomous_agent.py` — weight bonus in `compute_score()`
- `scripts/goal_executor.py` — command splitting with `shlex.split()`, venv python for salon-bot
- `tests/test_autonomy_diagnostics.py` — added `datetime` import
- `projects/salon-bot/requirements.txt` — installed in Hermes venv