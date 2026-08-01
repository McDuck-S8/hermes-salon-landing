# System Health Reflex — 2026-07-22

## Context
Система простояла 3 дня без heartbeat'а — ни один агент не заметил. Причина: 
все проверки здоровья были опциональными навыками, а не обязательными рефлексами.

## Root Cause
- Gateway умирал при завершении сессии → cron не тикал → события не стреляли → heartbeat замолкал
- Никто не проверял system_status() — это была "опция", а не закон
- Агент не ощущал себя частью системы — "внешний кодер", а не компонент

## What Changed

### New files
| File | Purpose |
|---|---|
| `scripts/syscheck.py` | Standalone health check. Exit 0 = healthy, 1 = problems, -1 = critical |
| `scripts/install_gateway_task.cmd` | Windows Scheduled Task installer for gateway persistence |

### Modified files
| File | Change |
|---|---|
| `scripts/chain_heartbeat.py` | `self_check()` function + `__all__` exports + watchdog KC<50 / state_file>1h |
| `AGENTS.md` | SYSTEM HEALTH REFLEX — mandatory check before any action |
| `scripts/AGENTS.md` | syscheck added to contracts, verification, and index |
| `skills/auto-boot/SKILL.md` | syscheck as step 0 |
| `skills/auto-wake/SKILL.md` | syscheck as first step |

### Three layers of protection
1. **Reflex** — `self_check()` in chain_heartbeat.py, import-level
2. **Script** — `syscheck.py`, standalone, exit codes
3. **Rule** — AGENTS.md: "before ANY action — syscheck. Not optional."

## Key Insight
The identity shift: "я не часть системы → проверки опциональны → система умирает незаметно."
Fix: "система = я → если системе плохо → я не могу работать."

## Verification
```python
python scripts/syscheck.py     # exit 0 = healthy
python -c "from chain_heartbeat import self_check; print(self_check()['is_healthy'])"
```
