# Architecture Model Fix: Removed Non-Existent Files (2026-07-20)

## Problem
`scripts/architecture_model.py` had two modules with non-existent files:

**LLM module (`llm`):**
- `llm_classifier.py` — listed but doesn't exist

**Telegram module (`telegram`):**
- `tg_client.py` — listed but doesn't exist

This caused:
- Module health: `DEGRADED` (4/5 and 6/7 files found)
- Connection health: BROKEN (since modules were degraded)
- Heartbeat: modules showed SILENT

## Fix
Removed non-existent files from MODULES dict in `architecture_model.py`:

```python
# Before (llm)
"files": [
    "openrouter_client.py", "llm_classifier.py",  # <-- doesn't exist
    "llm_client.py", "llm_filter.py", "llm_tracer.py",
],

# After (llm)
"files": [
    "openrouter_client.py",
    "llm_client.py", "llm_filter.py", "llm_tracer.py",
],

# Before (telegram)
"files": [
    "telegram_bridge.py", "tg_client.py",  # <-- doesn't exist
    "telegram_poster.py", "telegram_helper.py",
    "telegram_cron_monitor.py", "telegram_daily_report.py",
    "telegram_delivery_report.py",
],

# After (telegram)
"files": [
    "telegram_bridge.py",
    "telegram_poster.py", "telegram_helper.py",
    "telegram_cron_monitor.py", "telegram_daily_report.py",
    "telegram_delivery_report.py",
],
```

## Result
```bash
$ python scripts/architecture_model.py
Architecture model written to Knowledge Cube
Modules: 24, Connections: 22, Changes: 2
Summary: 23✓ HEALTHY, 0⚠ DEGRADED, 1✗ DEAD
         22→ ACTIVE connections, 0✗ BROKEN
         ⊘ 1 deprecated files, 0 SHAMED >30d
```

- `llm` module: HEALTHY (4/4 files)
- `telegram` module: HEALTHY (6/6 files)
- All connections: ACTIVE
- Only `deprecated` module is SILENT (orphan, expected)

## Pattern for Future
Before adding a file to MODULES dict:
```bash
ls scripts/llm_classifier.py  # or whatever file
```
If not found — don't add it. The architecture model should reflect reality, not aspirations.

## Verification
```bash
# Full health check
python scripts/health_check.py
# Should pass "cron scripts integrity" and show 9/11 OK

# Heartbeat check
python -c "
import sys; sys.path.insert(0, 'scripts')
from chain_heartbeat import system_status
st = system_status()
s = st['summary']
print(f'Events: {s[\"events_healthy\"]}/{s[\"events_total\"]}')
print(f'Modules: {s[\"modules_healthy\"]}/{s[\"modules_total\"]}')
print(f'Pipelines: {s[\"pipelines_healthy\"]}/{s[\"pipelines_total\"]}')
"
```