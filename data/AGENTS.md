# data/ — Knowledge Base & Data Storage

## Purpose
Persistent data: knowledge cube database, patterns, plans, session data, dream-memory, and domain-specific data files.

## Ownership
Data files used by scripts and agent processes.

## Local Contracts
- `knowledge_cube.db` — SQLite knowledge cube (primary knowledge store)
- `knowledge_gap_tasks.json` — Knowledge gap tracking
- `patterns/` — Detected behavioral patterns
- `plans/` — Stored execution plans
- `sessions/` — Session data dumps
- `tasks/` — Task tracking data
- `memory/` — Memory data files
- `dream-memory/` — Dream memory consolidation data
- `lavra-knowledge.jsonl` — Lavra knowledge entries
- `lavra-memory/` — Lavra memory data
- `notes/` — Stored notes

## Work Guidance
- Do not edit `knowledge_cube.db` directly — use scripts (analyze_cube.py, event_evolution.py)
- Patterns are auto-generated from session analysis
- Plans are created by the planning system
- This directory is for durable data, not temp files (use `cache/` for that)

## Verification
- Check `knowledge_cube.db` exists and is not corrupt
- `python scripts/analyze_cube.py` for health check
