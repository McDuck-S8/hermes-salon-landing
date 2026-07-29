# scripts/ — Core Hermes Scripts

## Purpose
Core automation, knowledge management, event tracking, and agent logic for the Hermes system.

## Ownership
This directory contains the main operational scripts. Most are standalone Python scripts invoked by cron jobs or the autonomous agent.

## Local Contracts
- All scripts use `sys.path.insert(0, "D:/Portable_Soft/hermes/scripts")` for imports
- Scripts interact with the Knowledge Cube via `knowledge_cube.py` or `kc_rag.py`
- Event tracking goes through `event_evolution.py` → `hermes_hooks.py`
- **System monitoring**: `chain_heartbeat.py` — 5-level event-driven monitoring (no daemons). Events fire at data mutation points: `kc_rag.upsert()` → `knowledge_added`, `self_improvement_loop.main()` → `new_suggestions_ready`
- LLM calls use `openrouter_client.py` or `llm_classifier.py`

## Work Guidance
- **Event-driven monitoring**: `chain_heartbeat.py` — Level 1 (events), Level 2 (modules), Level 3 (pipelines), Level 4 (external services), Level 5 (`system_heartbeat.json`)
- **Core modules**: `core_engine.py`, `event_evolution.py`, `hermes_hooks.py`, `auto_recall.py`
- **Knowledge Cube**: `knowledge_cube.py`, `kc_rag.py` (primary data entry via `upsert()`), `cube_feeder.py`, `cube_categorizer.py`, `knowledge_brain.py`
- **Autonomous agent**: `autonomous_agent.py` — main decision loop
- **Self-improvement**: `self_improvement_loop.py` (generates suggestions, fires `new_suggestions_ready`), `suggestion_consumer.py`, `self_system.py`
- **Proactive executor**: `proactive_executor.py` — self-healing, white-spot detection, knowledge gap filling, skill auto-evolution, LLM analysis, fix verification feedback loop
- **Cron scripts**: `*_cron.py` files — run on schedule via `cron/jobs.json`
- **Telegram**: `telegram_bridge.py`, `tg_client.py` — Telegram integration
- **Utilities**: `utilities/` — helper scripts, fixes, launchers
- **Archive**: `_archive/` — deprecated scripts, keep for reference
- **Proactive DOER**: `proactive_doer.py` — autonomous cron-run fix executor; cleans stale locks, repairs broken JSON, restarts failed jobs, clears stale cache. Runs every 15 min.

## Verification
- Run `python scripts/health_check.py` to verify system health
- Run `python scripts/test_llm_analyst.py` to test LLM integration

## Child DOX Index
| File/Dir | Purpose |
|---|---|
| `chain_heartbeat.py` | 5-level event-driven system monitoring (events → modules → pipelines → services → JSON) |
| `kc_rag.py` | Primary Knowledge Cube data entry via `upsert()` — fires `knowledge_added` event |
| `self_improvement_loop.py` | Suggestion generation loop — fires `new_suggestions_ready` event |
| `suggestion_consumer.py` | Consumes and applies improvement suggestions |
| `self_system.py` | Proactive system analysis — fires `new_suggestions_ready` |
| `core_engine.py` | Central engine, state management |
| `event_evolution.py` | Event tracking, hooks, evolution triggers |
| `hermes_hooks.py` | Unified hooks API for agents |
| `auto_recall.py` | Knowledge Cube recall/search |
| `autonomous_agent.py` | Main autonomous decision loop |
| `knowledge_cube.py` | Knowledge Cube operations |
| `proactive_executor.py` | Self-healing, white-spot detection, knowledge gap filling, skill auto-evolution |
| `openrouter_client.py` | LLM API client |
| `posting/` | Social media posting scripts |
| `utilities/` | Helper scripts, fixes |
| `*_cron.py` | Scheduled task scripts |
