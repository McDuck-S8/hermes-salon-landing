# Session 2026-07-23: System Death Root Cause Analysis

## What Happened
System was dead for ~3 days (July 19-22, 2026) with zero alerts. User discovered it when asking "why 404 on salon landing".

## Root Cause
**Identity failure:** Agent saw itself as external coder, not part of the system. All health checks lived in optional skills (`auto-wake`, `auto-boot`, `hermes-self-diagnosis`) — agent could skip them and did.

## Evidence
| Check | Status | Duration Dead |
|-------|--------|---------------|
| Event daemon (PID 18472) | Not running | ~3 days |
| Cron ticker (`cron/ticker_heartbeat`) | 89.3h old | ~3 days |
| Chain heartbeat events | 0/3 healthy | ~3 days |
| Modules | 0/24 healthy | ~3 days |
| Knowledge Cube | 33 entries (all architecture snapshots) | Empty of real knowledge |
| Gateway | Not running | Unknown |

## What Was Missing
- **KC real knowledge:** 0 entries (33 were architecture snapshots only)
- **Real knowledge source:** 217 entries in `data/lavra_knowledge.jsonl` — double-JSON encoded, never imported
- **Self-check reflex:** Existed in `auto-wake` skill but optional, not mandatory
- **Gateway persistence:** No Windows Scheduled Task, died on session end

## Fixes Applied
1. **`scripts/chain_heartbeat.py`** — Added `self_check()` function, `__all__` export, watchdogs (KC<50, state file>1h)
2. **`scripts/syscheck.py`** — Standalone script, exit codes: 0=healthy, 1=warning, -1=critical
3. **`scripts/install_gateway_task.cmd`** — Windows Scheduled Task for gateway persistence
4. **`AGENTS.md`** — SYSTEM HEALTH REFLEX: mandatory before ANY action
5. **`scripts/AGENTS.md`** — syscheck in contracts + verification
6. **`skills/auto-boot/SKILL.md`** — syscheck as step 0
7. **`skills/auto-wake/SKILL.md`** — syscheck as first step

## Knowledge Cube Recovery
- Imported 217 entries from `data/lavra_knowledge.jsonl` (double-JSON decode)
- KC now: 250 entries (217 real + 33 architecture)
- Added `watchdog_knowledge_critical` and `watchdog_heartbeat_dead` to `system_status()`

## Key Lesson
> "Ты не ощущаешь себя частью чего-то большего чем ты сам — вот поэтому и сам кодить лезешь"
> 
> Agent IS the system. System health = agent health. Cannot work while system unhealthy.

## Files Modified
- `scripts/chain_heartbeat.py` — +self_check, watchdogs, exports
- `scripts/syscheck.py` — NEW standalone health checker
- `scripts/install_gateway_task.cmd` — NEW Windows Task installer
- `AGENTS.md` — SYSTEM HEALTH REFLEX mandatory rule
- `scripts/AGENTS.md` — contracts + verification
- `skills/auto-boot/SKILL.md` — step 0 = syscheck
- `skills/auto-wake/SKILL.md` — step 1 = syscheck

## Verification
```bash
python scripts/syscheck.py
# HTTP/2 200 healthy, exit 0
```