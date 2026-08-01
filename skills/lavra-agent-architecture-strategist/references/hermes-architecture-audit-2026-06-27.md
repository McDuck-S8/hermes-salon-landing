# Hermes Architecture Audit — 2026-06-27

## System Overview
- 241 Python files, ~28,000 lines of code
- 30 modules in crystal/, 211 in scripts/
- 11 SQLite databases
- 44+ cron jobs

## HERMES_HOME Inconsistency (CRITICAL)
3 different strategies for path resolution across scripts:
```python
# Strategy 1: Environment variable (auto_recall.py)
HERMES_HOME = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))

# Strategy 2: Relative to script (autonomous_agent.py, chain_executor.py)
HERMES_HOME = Path(__file__).resolve().parent.parent

# Strategy 3: Hardcoded fallback (self_system.py, kc_feeder.py)
PORTABLE_HERMES = Path("D:/Portable_Soft/hermes")
if not (HERMES_HOME / "cache" / "event_bus.json").exists() and (PORTABLE_HERMES / "cache" / "event_bus.json").exists():
    HERMES_HOME = PORTABLE_HERMES
```
**Risk**: Script behavior changes depending on where it's run from. Fix: single `hermes_config.py` with canonical HERMES_HOME resolution.

## File Complexity (God Objects)
| File | Lines | Methods | Risk |
|------|-------|---------|------|
| proactive_executor.py | 2799 | ? | SRP violation |
| autonomous_agent.py | 2615 | 49 | God object |
| crystal/core.py | 583 | 31 | Moderate |
| curiosity_engine.py | 506 | ? | OK |
| sensor_array.py | 496 | ? | OK |

## SOLID Violations
- **SRP**: autonomous_agent.py has 49 methods doing decisions, execution, state collection, logging, graph analysis
- **OCP**: EVENT_JOB_MAP hardcoded in event_bus.py; 316 direct DB accesses without abstraction
- **ISP**: No interface definitions between components
- **DIP**: 316 direct sqlite3.connect / json.load calls across all scripts; no repository pattern

## Database Fragmentation
11 SQLite files with no unified schema management:
```
state.db (98MB) — main state
knowledge_cube.db — knowledge storage
kanban.db — task management
lcm.db — unknown
cache/events.db — event system
cache/core_engine.db — core engine state
cache/unified.db — unknown
cache/sessions.db (0 bytes) — EMPTY
cache/state.db (0 bytes) — EMPTY
knowledge_cube.db (0 bytes) — stale placeholder
scripts/salon_bookings.db — salon-specific
```

## Shared State Patterns
- No HERMES_HOME constant in any shared module
- Each script resolves paths independently
- No connection pooling for SQLite
- No migration system for schema changes
- Data sharing via file system (JSON files in cache/, logs/)

## Audit Checklist (Reusable)
When analyzing a Python codebase:
1. `wc -l` per file — find God objects (>500 lines)
2. `grep -c 'def '` per file — count methods
3. `grep 'HERMES_HOME\|Path(' *.py` — check path resolution consistency
4. `grep 'sqlite3.connect\|json.load' *.py` — count direct DB accesses
5. `grep 'sys.path' *.py` — find sys.path hacks (dependency smell)
6. `grep 'subprocess' *.py` — find inter-script coupling
7. Check for interface definitions (ABC, Protocol)
8. Check for dependency injection patterns

## Resolution (2026-06-27)
All 3 issues fixed via Lavra bead hermes-3wg:
- Created `scripts/hermes_config.py` — unified HERMES_HOME, get_db(), log()
- Updated 5 files: autonomous_agent.py, self_system.py, auto_recall.py, crystal/config.py, event_bus.py
- Verified: all components OK, all files pass py_compile

**Workflow used:** analysis → bd create → delegate_task(lavra-work-single) → commit
**Lesson:** ALWAYS create bead + run lavra-work after analysis. Never propose manual fixes.
