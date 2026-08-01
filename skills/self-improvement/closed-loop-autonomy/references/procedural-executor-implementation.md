# Procedural Executor — Implementation Reference

## Architecture

```
event_daemon.py beat():
  1. procedural_executor.check_all_triggers()  ← NO LLM, deterministic
  2. sensor_array.sweep_all()                   ← detect events
  3. event_sense.fire()                         ← emit events
  4. log everything
```

## 8 Triggers

| ID | Trigger | Action | Log |
|----|---------|--------|-----|
| TRIGGER-001 | Network dead (ping 8.8.8.8 fails) | Log, escalate | ALERTS.md |
| TRIGGER-002 | Gateway process not found | Kill stale locks, restart via `hermes gateway start` | feedback_store |
| TRIGGER-003 | Cron job `last_status == "error"` + `next_run_at` in past | Delay `next_run_at` +1h | feedback_store + ALERTS.md |
| TRIGGER-004 | Goal `status == "blocked"` > 24h | Escalate to user via ALERTS.md | ALERTS.md |
| TRIGGER-005 | Port dead (netstat) | Kill process, restart service | feedback_store |
| TRIGGER-006 | Disk > 80% | Find files > 100MB | feedback_store |
| TRIGGER-007 | Memory > 80% | Log top processes | ALERTS.md |
| TRIGGER-008 | Telegram API unreachable (curl) | Log, suggest proxy switch | ALERTS.md |

## Port Configuration

| Port | Service | Restart Command |
|------|---------|-----------------|
| 3264 | FreeQwenApi | `cd D:/Portable_Soft/FreeQwenApi && node index.js` |
| 9655 | FreeDeepseekAPI | `cd D:/Portable_Soft/FreeDeepseekAPI && node server.js` |
| 11434 | Ollama | `ollama serve` |

## CLI

```bash
python scripts/procedural_executor.py          # Run all triggers
python scripts/procedural_executor.py --status # Show status
python scripts/procedural_executor.py --list   # List triggers
python scripts/procedural_executor.py --run network  # Run specific trigger
python scripts/procedural_executor.py --run port_3264  # Run port trigger
```

## File Locations

- Skills definition: `skills/PROCEDURAL_SKILLS.md`
- Engine: `scripts/procedural_executor.py`
- Feedback log: `cache/procedural_feedback.jsonl` (JSONL, one entry per action)
- Alerts: `cache/ALERTS.md` (human-readable)

## Feedback Store Format

```json
{
  "timestamp": "2026-06-27T17:05:55",
  "trigger": "cron_error_3x",
  "action": "delay_job_1e45cd2656bd",
  "result": "delayed to 2026-06-27T18:05:55",
  "success": true
}
```

## Adding New Triggers

1. Add trigger function to `procedural_executor.py`:
```python
def trigger_my_new_thing():
    """TRIGGER-009: Description."""
    if condition_met():
        return True  # no action needed
    print("  [TRIGGER-009] Something happened")
    # ... take action ...
    log_feedback("my_trigger", "action_name", "result", success)
    return success
```

2. Register in TRIGGER_MAP:
```python
TRIGGER_MAP["my_trigger"] = ("TRIGGER-009: Description", trigger_my_new_thing)
```

3. Add to check_all_triggers() in the appropriate section.

4. Document in `skills/PROCEDURAL_SKILLS.md`.

## Integration Notes

- `check_all_triggers()` returns count of actions taken (int)
- Timezone-naive datetimes for comparison (strip tz from cron job timestamps)
- Feedback store is append-only JSONL
- ALERTS.md is append-only markdown
- No LLM calls anywhere in the executor
