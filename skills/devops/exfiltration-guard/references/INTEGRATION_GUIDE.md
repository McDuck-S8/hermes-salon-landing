# Exfiltration Guard Integration Guide

## Integration Points (Implemented)

- **Telegram Bridge** (`scripts/telegram_bridge.py`) → `check_telegram_message()` called before `send_telegram_message()`
- **Knowledge Cube Write** (`scripts/knowledge_cube.py`) → `scan_outbound()` called before INSERT
- **Cron Scheduler** (`hermes-agent/cron/scheduler.py`) → `scan_outbound()` called on prompt/script before job execution
- **File Writer** → hook before `write_file` (planned)
- **HTTP Client** → hook before outbound requests (planned)
- **Agent Output** → hook before any external transmission (planned)

## Integration Pattern

```python
# At module top level
try:
    from skills.devops.exfiltration_guard.scripts.exfil_guard import scan_outbound
    _EXFIL_ENABLED = True
except ImportError:
    _EXFIL_ENABLED = False
    def scan_outbound(text, source="unknown"):
        return {"blocked": False}

def dangerous_operation(content, ...):
    # 1. Kill Switch check FIRST (if applicable)
    if os.environ.get("HERMES_<SWITCH>_ENABLED", "true").lower() != "true":
        return {"status": "blocked", "reason": "HERMES_<SWITCH>_ENABLED=false"}
    
    # 2. Exfiltration Guard check SECOND
    if _EXFIL_ENABLED:
        exfil_result = scan_outbound(content, source=f"<component>:<id>")
        if exfil_result.get("blocked"):
            return {
                "status": "blocked", 
                "reason": f"Exfiltration: {exfil_result['matches']}", 
                "quarantine_id": exfil_result.get("quarantine_id")
            }
    
    # 3. Proceed with operation
    ...
```

## Components with Exfiltration Guard

| Component | File | Function | Source Format |
|-----------|------|----------|---------------|
| Telegram Bridge | `scripts/telegram_bridge.py` | `send_telegram_message()` | `telegram_bridge` |
| Knowledge Cube | `scripts/knowledge_cube.py` | `add_experience()` | `kc_write:<source>` |
| Cron Scheduler | `hermes-agent/cron/scheduler.py` | `run_job()` | `cron_job:<job_id>` |