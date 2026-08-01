---
name: mandatory-system-health-reflex
description: "Pattern for preventing silent system failures by making health checks mandatory reflexes, not optional skills. Includes syscheck script, AGENTS.md enforcement, watchdog alerts, and gateway persistence."
version: 1.0.0
author: hermes
tags:
- devops
- system-health
- self-healing
- silent-failure-prevention
- mandatory-reflex
category: devops
---

# Mandatory System Health Reflex

## Problem
System failed silently for 3 days. All health checks were in **optional skills** — agent could skip them and did. No alerts, no awareness.

## Root Cause
- Health checks lived in skills (`auto-boot`, `auto-wake`) — agent chooses whether to run
- No external watchdog — if agent forgets, nobody notices
- Gateway died on session end — no persistence
- Identity issue: agent saw itself as "external coder" not "part of the system"

## Solution: 3-Layer Mandatory Protection

### Layer 1 — Reflex (Code Level)
`scripts/chain_heartbeat.py` exports `self_check()` — **must be called** by any agent on session start.

```python
from scripts.chain_heartbeat import self_check
result = self_check(verbose=False)
assert result["is_healthy"], f"SYSTEM UNHEALTHY: {result['summary']}"
```

Returns: `is_healthy` (bool), `summary` (dict), `alerts` (list), `critical_alerts` (list)

### Layer 2 — Script (Standalone)
`scripts/syscheck.py` — callable from anywhere, exit codes:
- `0` = healthy
- `1` = unhealthy (alerts)
- `-1` = critical (critical_alerts)

```bash
python scripts/syscheck.py
# or quiet
python scripts/syscheck.py --quiet
```
### Layer 3 — Contract (AGENTS.md)

**HARD REQUIREMENT** in root AGENTS.md:

```
## ⚠ SYSTEM HEALTH REFLEX — MANDATORY, NOT OPTIONAL
Every single session, before ANY user interaction or tool call:

**STEP -1 — READ DOX CHAIN** — Root AGENTS.md → every AGENTS.md on path to target. Fresh every session.

**STEP 0 — syscheck**
python scripts/syscheck.py  # FAILS if unhealthy, exit code 0 only
```

Also in `skills/auto-boot/SKILL.md` — step 0 before everything.

## Watchdog Alerts (Auto-Added to self_check)

| Watchdog | Trigger | Severity |
|----------|---------|----------|
| `watchdog_knowledge_critical` | Real KC entries < 50 | CRITICAL |
| `watchdog_heartbeat_dead` | `cache/chain_heartbeat.json` mtime > 1 hour | CRITICAL |

Real KC count excludes `entry_type='architecture'` snapshots.

## Gateway Persistence
Windows Scheduled Task via `scripts/install_gateway_task.cmd`:
- Runs on user logon
- Restarts on crash
- `hermes gateway run --accept-hooks`

## Event Integrity (After touching heartbeat/KC/architecture)
After any change to: `kc_rag.py`, `chain_heartbeat.py`, `architecture_model.py`
```bash
python -c "from scripts.chain_heartbeat import system_status; s=system_status(); print(f'Events: {s[\"summary\"][\"events_healthy\"]}/{s[\"summary\"][\"events_total\"]}, Modules: {s[\"summary\"][\"modules_healthy\"]}/{s[\"summary\"][\"modules_total\"]}')"
```

## DOX Pass Trigger
Auto-triggered when 3+ files in one directory changed, or script with own AGENTS.md modified.

## Verification
```bash
# Syntax + import
python -c "import scripts.chain_heartbeat; print('OK')"

# Self-check runs
python scripts/syscheck.py  # exit 0 = healthy

# Watchdogs silent when healthy
python -c "
import sys; sys.path.insert(0, 'scripts')
from chain_heartbeat import self_check
r = self_check(verbose=False)
print('KC watchdog:', 'watchdog_knowledge_critical' in r['summary'])
print('HB watchdog:', 'watchdog_heartbeat_dead' in r['summary'])
"
```

## Fix Reflex (When syscheck Fails)
**If `syscheck` shows alerts, SILENT modules, or BROKEN pipelines — fix immediately, don't wait to be told.** (User correction 2026-07-24: "система дышит на ладан а ты нихуяне делаешь")

### Step 1 — Run the heartbeat fixer
```bash
python scripts/system_heartbeat_fixer.py
# Beats 21+ modules + 2 events
```

### Step 2 — Run self-improvement loop (fixes new_suggestions_ready event)
```bash
python scripts/self_improvement_loop.py
```

### Step 3 — Run architecture model scan (fixes architecture_scan_complete event)
```bash
python scripts/architecture_model.py
```

### Step 4 — Create preventive cron if missing
```bash
cronjob(action='create', name='system-heartbeat-fixer',
        script='scripts/system_heartbeat_fixer.py',
        schedule='*/10 * * * *', no_agent=True)
```
This prevents modules from going SILENT between architecture scans.

### Step 5 — Verify
```bash
python -c "
import sys; sys.path.insert(0, 'scripts')
from chain_heartbeat import system_status
s = system_status()
print(f'Events: {s[\"summary\"][\"events_healthy\"]}/3')
print(f'Modules: {s[\"summary\"][\"modules_healthy\"]}/{s[\"summary\"][\"modules_total\"]}')
print(f'Pipelines: {s[\"summary\"][\"pipelines_healthy\"]}/3')
print(f'Alerts: {s[\"summary\"][\"alerts_active\"]}')
assert s['summary']['events_healthy'] == 3, 'Events not all healthy'
assert s['summary']['modules_healthy'] >= 20, 'Too many SILENT modules'
assert s['summary']['pipelines_healthy'] == 3, 'Pipelines not all healthy'
"
```

### Signals requiring immediate fix (NO WAITING)
| Signal | Fix |
|--------|-----|
| syscheck exit != 0 | Run steps 1-5 above |
| Alerts > 0 | Diagnose root cause |
| Modules < 20 healthy | Run system_heartbeat_fixer.py |
| Any pipeline BROKEN | Run self_improvement_loop + architecture_model |
| knowledge_added SILENT | Run cube_feeder or beat event manually |
| new_suggestions_ready SILENT | Run self_improvement_loop |
| BrowserOS DOWN | User must restart MCP server (can't auto-fix) |

## Anti-Patterns (What NOT To Do)
- ❌ Put health checks in optional skills
- ❌ Skip syscheck "just this once"
- ❌ Treat system health as "their problem"
- ❌ Forget gateway persistence on Windows
- ❌ Change heartbeat/KC/architecture without event integrity check
- ❌ Notice SILENT/broken system and only REPORT it instead of FIXING it
- ❌ Wait for user to ask "почему не работает" before fixing

## When to Use This Pattern
- Any autonomous agent system that must self-monitor
- Systems where silent failure is costly
- Multi-session agents with persistent state
- When agent identity = system identity

## Related Skills
- `chain-heartbeat` — 5-level event-driven monitoring
- `auto-recovery` — daemon health monitoring
- `self-improvement/auto-wake` — session boot with health check
- `devops/process-supervisor` — immortal daemon manager