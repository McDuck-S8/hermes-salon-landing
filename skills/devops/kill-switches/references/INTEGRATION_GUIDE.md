# Kill Switches — Integration Guide (Real Status)

## Actual Integration Points (Implemented 2026-07-03)

| Switch | File | Function | Line | Status |
|--------|------|----------|------|--------|
| `HERMES_LLM_ENABLED` | `scripts/llm_analyst.py` | `call_llm()` | ~98 | ✅ Active |
| `HERMES_CRON_ENABLED` | `hermes-agent/cron/scheduler.py` | `tick()` | ~2872 | ✅ Active |
| `HERMES_CRON_ENABLED` | `hermes-agent/cron/scheduler.py` | `run_job()` | ~1980 | ✅ Active |
| `HERMES_BRIDGE_ENABLED` | `scripts/telegram_bridge.py` | `send_telegram_message()` | ~71 | ✅ Active |
| `HERMES_KC_WRITE_ENABLED` | `scripts/knowledge_cube.py` | `add_experience()` | ~136 | ✅ Active |

## Integration Pattern Used

```python
# Pattern: Early return with clear message
if os.environ.get("HERMES_XXX_ENABLED", "true").lower() != "true":
    return {"status": "blocked", "reason": "HERMES_XXX_ENABLED=false — disabled by kill switch"}
```

For `run_job` (which returns tuple):
```python
if os.environ.get("HERMES_CRON_ENABLED", "true").lower() != "true":
    err = "HERMES_CRON_ENABLED=false — cron job execution disabled by kill switch"
    logger.warning("Job '%s': %s", job_id, err)
    return False, "", "", err
```

## Exfiltration Guard Integration (Bonus)

Kill switches now work alongside Exfiltration Guard:

| File | Both Checks Present |
|------|---------------------|
| `scripts/telegram_bridge.py` | ✅ Kill switch + Exfil scan |
| `scripts/knowledge_cube.py` | ✅ Kill switch + Exfil scan |
| `hermes-agent/cron/scheduler.py` | ✅ Kill switch + Exfil scan |

## Hot Reload Verification

Tested: Edit `.env` → next call sees new value (~instant, no restart needed).

## Audit Log

Not yet implemented — `audit_logger.py` is a placeholder. Next step: implement structured logging of every switch flip.

## Remaining from Playbook

| Switch | Status | Target |
|--------|--------|--------|
| `HERMES_SELF_MODIFY_ENABLED` | ❌ Not implemented | `scripts/skill_manage.py`, `procedural_executor.py` |
| `HERMES_WARROOM_ENABLED` | ❌ Not implemented | `skills/devops/war-room/scripts/war_room.py` |