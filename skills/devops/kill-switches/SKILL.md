---
name: kill-switches
description: Kill Switches pattern from AI-First Business Playbook — 6 hot-reloadable boolean gates for every dangerous boundary. Flip one, system refuses at that boundary in ~2 seconds.
---

# Kill Switches — Safety Scaffolding for Hermes

Implements the AI-First Business Playbook kill switch pattern:
Six hot-reloadable boolean switches in `.env` that gate every dangerous boundary.

## Architecture

```
kill-switches/
├── SKILL.md                    # This file
├── references/
│   ├── KILL_SWITCHES_GUIDE.md        # Deep dive on each switch
│   ├── HOT_RELOAD.md                 # File watcher implementation
│   └── INCIDENT_RESPONSE.md          # How to use during incidents
├── scripts/
│   ├── kill_switches.py          # Core switch management
│   ├── switch_checker.py         # Decorator/context manager for checks
│   ├── hot_reload_watcher.py     # File watcher for .env changes
│   └── audit_logger.py           # Logs every switch flip
└── templates/
    └── .env.example
```

## The Five Kill Switches (Implemented)

| Switch | Gates | Default | Use Case | Integrated In |
|--------|-------|---------|----------|---------------|
| `HERMES_LLM_ENABLED` | All LLM API calls | `true` | Model misbehavior, cost control | `scripts/llm_analyst.py:call_llm()` |
| `HERMES_CRON_ENABLED` | Cron tick + job execution | `true` | Runaway cron, stuck jobs | `hermes-agent/cron/scheduler.py:tick()` + `run_job()` |
| `HERMES_BRIDGE_ENABLED` | Telegram message delivery | `true` | Bridge issues, spam prevention | `scripts/telegram_bridge.py:send_telegram_message()` |
| `HERMES_KC_WRITE_ENABLED` | Knowledge Cube writes | `true` | Data corruption prevention | `scripts/knowledge_cube.py:add_experience()` |
| `HERMES_EXFIL_GUARD_ENABLED` | Exfiltration Guard scanner | `true` | Secret leakage prevention | `skills/devops/exfiltration-guard/scripts/exfil_guard.py` |

> **Note:** User explicitly rejected cron-based architecture. Event-driven only. `HERMES_CRON_ENABLED` gates legacy cron jobs as BACKUP — primary path is event-driven via `signal_daemon.py` + `event_daemon.py` + `event_bus.py`.

## Hot Reload

Switches read from Hermes config on every operation
- File watcher detects config changes → reloads in ~2 seconds
- No restart required
- Audit log records every flip

## Usage

```python
from kill_switches import require_switch

@require_switch("HERMES_LLM_ENABLED")
def call_llm(prompt):
    # Only executes if switch is ON
    return llm.complete(prompt)

# Or inline check
from kill_switches import is_enabled
if is_enabled("HERMES_CRON_ENABLED"):
    run_cron_job()
else:
    log("Cron disabled by kill switch")
```

## Incident Response

```bash
# Emergency: disable all LLM calls instantly
echo "HERMES_LLM_ENABLED=false" >> .env
# ~2 seconds later: all LLM calls refused with clear message

# Check status
python scripts/kill_switches.py status

# Re-enable
sed -i 's/HERMES_LLM_ENABLED=false/HERMES_LLM_ENABLED=true/' .env
```

## Audit Log

Every switch flip logged to `audit_log`:
```
[2026-07-03 14:30:00] KILL_SWITCH: HERMES_LLM_ENABLED false -> true (user: operator, reason: incident resolved)
```

## Kill Switch
```env
HERMES_KILL_SWITCHES_ENABLED=true  # Master enable for kill switch system itself
```