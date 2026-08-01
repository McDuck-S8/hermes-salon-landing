# Result Producer Pattern

Replaces error alerters with auto-fixers. Key lesson from user correction 2026-06-07: "а нахрена мне -и пинает в Telegram при ошибках мне нужен результат"

## Principle
Every cron/script that detects a problem must ATTEMPT TO FIX IT before reporting. The deliverable is the fix outcome, not the error notification.

## Implementation
- Script: `scripts/result_producer.py`
- Cron: `result-producer` (job `0aed4311f592`), every 30min, no_agent=True
- Log: `logs/result_producer.log`

## Architecture
```python
FIXERS = {
    "job-name": lambda: attempt_fix_for_job(),
}

def check_cron_errors():
    # Read latest output for each failing cron job
    # Match known job names to fixers
    
def main():
    errors = check_cron_errors()
    for name in errors:
        fixer = FIXERS.get(name)
        if fixer:
            result = fixer()  # try to fix
            deliver(f"🔧 {name}: {result}")
        else:
            deliver(f"ℹ️ {name}: diagnosis only: {diagnosis}")
```

## What Was Replaced
- **REMOVED:** `error-alerter` cron (every 5min) — sent Telegram messages to @max_brain_chef_official for EVERY cron error
- **CREATED:** `result-producer` cron (every 30min) — tries known fixes, reports outcomes

## Adding New Fixers
1. Identify the cron job's common failure pattern
2. Write a fix function that addresses the root cause
3. Add to FIXERS dict with the job name
4. Test with `python scripts/result_producer.py`
