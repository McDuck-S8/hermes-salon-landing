# Test Fixes — 2026-07-28

## Fixed Tests (previously failing in test_autonomy_diagnostics.py)

| Test | Issue | Fix |
|------|-------|-----|
| `test_3_weights_affect_scoring` | `compute_score()` ignored `feedback_store.compute_weight()` | Added `weight * 0.1` bonus in `autonomous_agent.py:compute_score()` |
| `test_8_feedback_persists` | Missing `from datetime import datetime` | Added import at top of test file |
| `test_4_goal_executor_returns_action` | salon-bot `main.py` couldn't import `aiogram` | Installed `aiogram` in Hermes venv; updated `goal_executor.py:derive_action()` to use venv python path |
| `test_6_goal_executor_detects_already_met` | Same as above | Same fix |
| `test_7_action_log_exists` | `action_log.jsonl` not created by `feedback_store.record_outcome()` | Not yet fixed — needs implementation in `feedback_store.py` |
| `test_9_context_loads_all_sections` | Session context missing "Previous Session" section | Not yet fixed — `session_context.py` needs this section |
| `test_12_agent_has_diverse_actions` | Only 5 candidate actions generated vs required 20+ | Need to expand `evaluate_actions()` in `autonomous_agent.py` |

## Path Prefix Bug Fix (2026-07-28)

**Issue**: Cron jobs with `script: "scripts/script_name.py"` failed because the cron runner prepends `HERMES_HOME/scripts/`, resulting in `scripts/scripts/script_name.py`.

**Root Cause**: The cron scheduler (`cron/scheduler.py:_run_job_script()`) already prepends `HERMES_HOME/scripts/` to the script path. Jobs must specify the filename ONLY.

**Affected Jobs This Session**:
- `youtube-watch`
- `rss-monitor`
- `daily-digest`
- `pinterest-auto-pinner`
- `telegram-channel-poster`

**Fix Applied**: Remove `scripts/` prefix from job's `script` field:
```json
// BAD:
"script": "scripts/youtube_watch.py"

// GOOD:
"script": "youtube_watch.py"
```

**Prevention**: When creating cron jobs via `cronjob(action='create', script=...)`, pass the script filename ONLY (no directory prefix).