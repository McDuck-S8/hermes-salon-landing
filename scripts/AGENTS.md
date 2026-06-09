# scripts/ — Core Hermes Scripts

## Purpose
Core automation, knowledge management, event tracking, and agent logic for the Hermes system.

## Ownership
This directory contains the main operational scripts. Most are standalone Python scripts invoked by cron jobs or the autonomous agent.

## Local Contracts
- All scripts use `sys.path.insert(0, "D:/Portable_Soft/hermes/scripts")` for imports
- Scripts interact with the Knowledge Cube via `knowledge_cube.py`
- Event tracking goes through `event_evolution.py` → `hermes_hooks.py`
- LLM calls use `openrouter_client.py` or `llm_classifier.py`

## Work Guidance
- **Core modules**: `core_engine.py`, `event_evolution.py`, `hermes_hooks.py`, `auto_recall.py`
- **Knowledge Cube**: `knowledge_cube.py`, `cube_feeder.py`, `cube_categorizer.py`, `knowledge_brain.py`
- **Autonomous agent**: `autonomous_agent.py` — main decision loop
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
