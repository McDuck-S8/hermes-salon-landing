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
- **Crystal v3** (`crystal.py` + `crystal/`) — Персональный Development Advisor. 22 модуля, 8 отделов. Наблюдает → Анализирует → Предлагает → Оценивает → Эволюционирует. ONE-WAY bridge: пишет в `cache/crystal/`, никогда не читает обратно. Не модифицирует код.

## Work Guidance
- **Core modules**: `core_engine.py`, `event_evolution.py`, `hermes_hooks.py`, `auto_recall.py`
- **Knowledge Cube**: `knowledge_cube.py`, `cube_feeder.py`, `cube_categorizer.py`, `knowledge_brain.py`
- **Autonomous agent**: `autonomous_agent.py` — main decision loop
- **Proactive executor**: `proactive_executor.py` — self-healing, white-spot detection, knowledge gap filling, skill auto-evolution, LLM analysis, fix verification feedback loop
- **Session context** (WP-1): `session_context.py` — assembles rich context at session start from bridge, decisions, goals, weights
- **Session ingestion** (WP-2): `session_dump_ingester.py` — ingests session dump JSONs into KC
- **Feedback loop** (WP-3): `action_feedback.py` — outcome tracking + weight learning; `learn_actions.py` — daily recalculation
- **MCP Memory** (WP-4): `mcp_memory_bridge.py` — KC → graph sync + query; `mcp_memory_setup.py` — one-shot setup
- **Goal queue** (WP-5): `goal_queue.py` — goal management; `goal_evaluator.py` — daily auto-evaluation
- **File watchers** (WP-6): `file_watcher.py` — event-driven triggers; `event_daemon.py` — persistent daemon
- **Cron scripts**: `*_cron.py` files — run on schedule via `cron/jobs.json`
- **Telegram**: `telegram_bridge.py`, `tg_client.py` — Telegram integration
- **Utilities**: `utilities/` — helper scripts, fixes, launchers
- **Archive**: `_archive/` — deprecated scripts, keep for reference
- **Proactive DOER**: `proactive_doer.py` — autonomous cron-run fix executor; cleans stale locks, repairs broken JSON, restarts failed jobs, clears stale cache. Runs every 15 min.

## Verification
- Run `python scripts/health_check.py` to verify system health
- Run `python scripts/test_llm_analyst.py` to test LLM integration
- Crystal v3: `python scripts/crystal.py --summary` — сводка
- Crystal v3: `python scripts/crystal.py --test` — тест модулей
- Crystal v3: `python scripts/crystal.py` — полный цикл

## Child DOX Index
| File/Dir | Purpose |
|---|---|
| `crystal.py` | **Crystal v3 CLI** — персональный development advisor, 22 модуля, 8 отделов |
| `crystal/` | **Crystal v3 Package** — models, config, core, 22 модулей |
| `crystal.py.BACKUP` | Old crystal v2.0 (3576 lines) — will(), conscience, self_model.json, EE. Reference only |
| `core_engine.py` | Central engine, state management |
| `event_evolution.py` | Event tracking, hooks, evolution triggers |
| `hermes_hooks.py` | Unified hooks API for agents (includes MCP memory bridge) |
| `auto_recall.py` | Knowledge Cube recall/search |
| `autonomous_agent.py` | Main autonomous decision loop (includes feedback loop + goal queue) |
| `knowledge_cube.py` | Knowledge Cube operations |
| `proactive_executor.py` | Self-healing, white-spot detection, knowledge gap filling, skill auto-evolution |
| `openrouter_client.py` | LLM API client |
| `session_context.py` | **WP-1**: Session context builder — assembles context from 5 sources |
| `session_recall.py` | Session recall with context prepend (modified for WP-1) |
| `session_bridge.py` | Cross-session state handoff (includes load_rich) |
| `session_dump_ingester.py` | **WP-2**: Ingests session dump JSONs into KC |
| `auto_fetch_cron.py` | Session fetch wrapper (fixed for WP-2) |
| `action_feedback.py` | **WP-3**: Outcome tracking + weight learning |
| `learn_actions.py` | **WP-3**: Daily action weight recalculation |
| `mcp_memory_bridge.py` | **WP-4**: KC → MCP Memory graph sync + query |
| `mcp_memory_setup.py` | **WP-4**: One-shot MCP Memory setup |
| `goal_queue.py` | **WP-5**: Goal management (create/update/evaluate) |
| `goal_evaluator.py` | **WP-5**: Daily goal evaluation cron |
| `file_watcher.py` | **WP-6**: File system event watcher |
| `event_daemon.py` | **WP-6**: Persistent watcher daemon |
| `posting/` | Social media posting scripts |
| `utilities/` | Helper scripts, fixes |
| `*_cron.py` | Scheduled task scripts |
