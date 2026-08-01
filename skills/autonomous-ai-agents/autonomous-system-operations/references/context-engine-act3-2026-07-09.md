# Context Engine — Act 3: Contextual Spaces

**Date:** 2026-07-09
**Module:** `scripts/context_engine.py`
**Integration:** `autonomous_agent.py` → `collect_system_state()` → `state["context"]`

## What It Solves

Knowledge Cube has 2590 entries. Without context, the agent treats all knowledge equally.
Context Engine answers: "Given what time it is, what the user has been doing, and what's broken — what should I focus on RIGHT NOW?"

## Architecture (Four-Act Framework)

From theCUBE Research 2026:
- Act 1: LLM++ fluency → `llm_client.py` ✅
- Act 2: Knowledge Graph → `knowledge_cube.db` + OKF-Lite ✅
- **Act 3: Contextual Spaces → `context_engine.py` ✅** ← THIS
- Act 4: Persistent Memory → `memory` tool, `session_recall.py` ✅

## Scoring Formula

```
relevance = (confidence × 0.3)           # high-confidence = more relevant
           + (freshness × 0.3)           # recent = more relevant
           + (expiration_penalty × -0.2)  # expired = less relevant
           + (importance × 0.2)          # high importance = more relevant
           + (access_count × 0.1)        # frequently used = more relevant
           + (time_match × 0.1)          # matches current phase = more relevant
```

## Time Phases

| Phase | Hours | Energy | Focus |
|-------|-------|--------|-------|
| morning | 6-10 | high | planning |
| midday | 10-14 | peak | execution |
| afternoon | 14-18 | moderate | iteration |
| evening | 18-22 | declining | review |
| night | 22-6 | low | maintenance |

## Priority Actions Logic

```python
if errors_active > 0:
    priority_actions.append("fix_errors", urgency="high")
if knowledge_expired > 10:
    priority_actions.append("refresh_expired_knowledge", urgency="high")
if recent_sessions == 0:
    priority_actions.append("autonomous_work", urgency="medium")
```

## Schema Pitfall

The `experiences` table does NOT have `category`, `created_at`, or `access_count` columns.
Use `ts as created_at` and `0 as access_count` in SQL queries.
The `kc_entries` table has the full schema with all columns.

## Cron Integration

- `context-engine-4h` — runs every 4h, no_agent=True, updates `cache/current_context.json`
- `signal-scanner-hourly` — feeds new knowledge into KC
- `autonomous-agent-daily` — daily 9am, uses context for decision-making
