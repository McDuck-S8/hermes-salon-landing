# Self-Learning System Repair — Status & Architecture

## Current State (2026-06-09)

All components are **architecturally disconnected**. Each works standalone but
none are wired to each other. The system is a collection of loggers, not a
self-learning system.

### Component Map

```
core_engine.py (390 lines)
  ├── connects to: knowledge_cube.db, lavra_knowledge.jsonl, state.db
  ├── does: finds gaps, searches data, runs chains
  ├── DOES NOT: emit events, connect to event_evolution
  └── problems: bare except, hardcoded paths, SQLite without context managers

event_evolution.py (416 lines)
  ├── connects to: events.db
  ├── does: records events, checks triggers, runs handlers
  ├── DOES NOT: mark events as processed (FIXED 2026-06-09)
  └── problems: 4/6 handlers are no-op stubs, duplicate EventMonitor instances

hermes_hooks.py (162 lines)
  ├── connects to: event_evolution.py
  ├── does: wraps event functions for Hermes agent
  ├── DOES NOT: connect to core_engine (FIXED 2026-06-09)
  └── problems: hardcoded paths (FIXED)

autonomous_agent.py (918 lines)
  ├── connects to: nothing real
  ├── does: reads errors, prints analysis
  ├── DOES NOT: fix anything, create anything, apply anything
  └── problems: all 10 action executors are observational

cube_feeder.py (64 lines)
  ├── connects to: knowledge_cube.db (READ ONLY)
  ├── does: reports cube stats
  ├── DOES NOT: add entries to cube
  └── problems: read-only reporter, not a feeder

proactive_executor.py (1694 lines)
  ├── connects to: llm_analyst.py via files
  ├── does: finds "problems", reads suggested fixes
  ├── DOES NOT: apply fixes (format mismatch between LLM output and apply_patch_fix)
  └── problems: LLM returns descriptions, code expects unified diffs

llm_analyst.py (124 lines)
  ├── connects to: OpenCode Zen API
  ├── does: calls LLM, writes suggested_fixes.json
  ├── DOES NOT: return unified diffs (returns descriptions)
  └── problems: output format doesn't match proactive_executor expectations
```

### Dependency Chain (Beads)

```
hermes-rot (epic)
  ├── hermes-rot.1: Core Integration (core_engine ↔ event_evolution ↔ hermes_hooks)
  │     STATUS: IN PROGRESS — hardcoded paths fixed, process_event() now marks processed,
  │     hermes_hooks now imports CoreEngine and runs gap analysis on task_complete
  │     REMAINING: SQLite context managers, lavra-review, close bead
  │
  ├── hermes-rot.2: Fix LLM Pipeline (depends on 1)
  │     STATUS: OPEN
  │     WHAT: Make llm_analyst return unified diffs, make proactive_executor apply them
  │
  ├── hermes-rot.3: Fix Autonomous Agent (depends on 1)
  │     STATUS: OPEN
  │     WHAT: Make action executors actually do work, not just print
  │
  └── hermes-rot.4: Clean Up Cron Jobs (depends on 2, 3)
        STATUS: OPEN
        WHAT: Remove dead jobs, fix frequency, connect to working components
```

### Fixes Applied (2026-06-09)

1. **core_engine.py**: Hardcoded path → `Path(__file__).resolve().parent.parent`
2. **core_engine.py**: bare `except:` → `except Exception as e:` with logging
3. **core_engine.py**: lavra_knowledge.jsonl parser fixed for double-quoted JSON
4. **event_evolution.py**: Hardcoded path → `Path(__file__).resolve().parent.parent`
5. **event_evolution.py**: `process_event()` now calls `mark_processed()` — CRITICAL FIX
6. **hermes_hooks.py**: Hardcoded path → `Path(__file__).resolve().parent`
7. **hermes_hooks.py**: Added CoreEngine import + gap analysis on `on_task_complete()`

### What's Still Broken

1. **SQLite connections** in core_engine.py — opened but never closed (connection leaks)
2. **4/6 event handlers** in event_evolution.py — no-op stubs that just print
3. **autonomous_agent.py** — all action executors observational
4. **cube_feeder.py** — read-only, never writes to cube
5. **LLM pipeline** — llm_analyst returns descriptions, proactive_executor expects diffs
6. **33 cron jobs** — most dead or doing nothing

### Key Insight

The system was built as a collection of independent scripts that each "work"
standalone but nothing connects them. The fix requires wiring:
1. core_engine → event_evolution (emit events when gaps found)
2. event_evolution → hermes_hooks (already done)
3. hermes_hooks → core_engine (already done)
4. autonomous_agent → actually do work (not just analyze)
5. llm_analyst → return diffs (not descriptions)
6. proactive_executor → apply diffs (currently can't)

### User Requirement

**ONLY through lavra-work protocol.** User explicitly forbade autonomous coding:
"НИЧЕГО не трогай сам!!!! а только через /lavra будешь работать!!!!"

All fixes must go through: beads → lavra-work → lavra-review → close bead.
