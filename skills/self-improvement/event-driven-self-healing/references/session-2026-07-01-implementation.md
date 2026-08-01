# Session 2026-07-01: Event-Driven Self-Healing Implementation

## Context
User demanded: "Твоя задача сейчас — не писать новый скрипт, а сделать так, чтобы падение любого cron'а немедленно вызывало событие и рефлекс восстановления. Без ежедневных проверок!"

## Changes Made

### 1. procedural_executor.py — TRIGGER-012
Added cron health check trigger that runs every 5 minutes:
- Scans `cron/jobs.json` for jobs with `last_status: "error"` AND `next_run_at` in past
- Emits `cron_job_died` event for each dead job
- Auto-restarts: resets `next_run_at = now + 5min`, clears error, sets `last_status = "pending"`
- Logs to ALERTS.md and procedural_feedback.jsonl

### 2. event_bus.py — Event Map + Direct Handlers
**EVENT_JOB_MAP additions:**
```python
"cron_job_died": ["procedural-executor", "self-healing-monitor"],
"heartbeat_missed": ["procedural-executor", "anomaly-detector"],
"knowledge_cube_stale": ["cube-feeder", "knowledge-gap-filler"],
```

**DIRECT_EVENT_HANDLERS additions:**
- `_handle_cron_job_died`: boost_goal +2 for 15min → procedural_executor --run cron_health
- `_handle_heartbeat_missed`: boost_goal +1.5 for 10min → procedural_executor --run signal_daemon
- `_handle_knowledge_cube_stale`: runs cube_feeder.py directly

### 3. bayesian_scorer.py — boost_goal()
```python
def boost_goal(goal_id: str, boost: float = 2.0, duration_minutes: int = 15):
    # Loads goals from goal_queue.json
    # Increases priority (max 10)
    # Sets boosted_until, boost_reason, updated_at
    # Saves with _backup_file() helper
```

Also added `_backup_file()` helper to prevent "name '_backup_file' is not defined" error.

## Test Results

All tests passed:
```
✅ python scripts/procedural_executor.py --run cron_health
   → Found 2 dead jobs (self-upgrade-loop, ai-tools-hub-poster)
   → Emitted 2 cron_job_died events
   → Auto-restarted both with next_run_at = now + 5min

✅ python scripts/event_bus.py emit cron_job_died '{"job_id":"test","job_name":"test"}'
   → Event emitted, triggers: procedural-executor, self-healing-monitor

✅ python scripts/event_bus.py process
   → [DIRECT] cron_job_died → running handler
   → [BOOST] Goal g-001 priority boosted +2 for 15min
   → procedural_executor: Running TRIGGER-012

✅ python scripts/event_bus.py emit heartbeat_missed '{}'
   → [BOOST] Goal g-001 priority boosted +1.5 for 10min

✅ python scripts/event_bus.py emit knowledge_cube_stale '{}'
   → cube_feeder ran directly, added 2 new entries

✅ Verified goal_queue.json: g-001 has priority=10, boosted_until set
```

## Verification Commands for Future Sessions

```bash
# Full health check
python scripts/procedural_executor.py

# Test specific triggers
python scripts/procedural_executor.py --run cron_health
python scripts/event_bus.py emit cron_job_died '{"job_id":"test","job_name":"test"}'
python scripts/event_bus.py process

# Check goal boost
python -c "import sys; sys.path.insert(0,'scripts'); from bayesian_scorer import _load_goals_from_file; [print(g) for g in _load_goals_from_file() if g.get('id')=='g-001']"
```