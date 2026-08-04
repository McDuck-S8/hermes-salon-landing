# scripts/ — Core Hermes Scripts

## Purpose
Core automation, knowledge management, event tracking, and agent logic for the Hermes system.

## Ownership
This directory contains the main operational scripts. Most are standalone Python scripts invoked by cron jobs or the autonomous agent.

## Local Contracts
- All scripts use `sys.path.insert(0, "D:/Portable_Soft/hermes/scripts")` for imports
- Scripts interact with the Knowledge Cube via `knowledge_cube.py` or `kc_rag.py`
- Event tracking goes through `event_evolution.py` → `hermes_hooks.py`
- **System monitoring**: `chain_heartbeat.py` — 5-level event-driven monitoring (no daemons). Events fire at data mutation points: `kc_rag.upsert()` → `knowledge_added`, `self_improvement_loop.main()` → `new_suggestions_ready`. **Heartbeat поддерживается крон-задачей `heartbeat-fixer` (`system_heartbeat_fixer.py`, каждые 15 мин) — не бить руками.** `fix_heartbeat.py` защищает `chain_heartbeat.json`/`system_heartbeat.json` от удаления.
- LLM calls use `openrouter_client.py` or `llm_classifier.py`

## Work Guidance
- **Event-driven monitoring**: `chain_heartbeat.py` — Level 1 (events), Level 2 (modules), Level 3 (pipelines), Level 4 (external services), Level 5 (`system_heartbeat.json`)
- **Core modules**: `core_engine.py`, `event_evolution.py`, `hermes_hooks.py`, `auto_recall.py`
- **Knowledge Cube**: `knowledge_cube.py`, `kc_rag.py` (primary data entry via `upsert()`), `cube_feeder.py`, `cube_categorizer.py`, `knowledge_brain.py`
- **Autonomous agent**: `autonomous_agent.py` — main decision loop
- **Self-improvement**: `self_improvement_loop.py` (generates suggestions, fires `new_suggestions_ready`), `suggestion_consumer.py`, `self_system.py`. **Фильтр знаний**: `suggestion_filter.py` — классифицирует записи KC от `improvement_suggestions`/`self_improvement_loop` как LOG_COPY (мусор) или STRUCTURAL (ценность). LOG_COPY архивируются в `experiences_log_archive` (обратимо), не удаляются. `self_improvement_loop.py` НЕ пишет log-копии в KC — только структурные `recurring_fixes` (consumer читает из `improvement_suggestions.json`, auto-skills не зависят от KC).
- **Proactive executor**: `proactive_executor.py` — self-healing, white-spot detection, knowledge gap filling, skill auto-evolution, LLM analysis, fix verification feedback loop
- **Cron scripts**: `*_cron.py` files — run on schedule via `cron/jobs.json`
- **Telegram**: `telegram_bridge.py`, `tg_client.py` — Telegram integration
- **Utilities**: `utilities/` — helper scripts, fixes, launchers
- **Archive**: `_archive/` — deprecated scripts, keep for reference
- **Proactive DOER**: `proactive_doer.py` — autonomous cron-run fix executor; cleans stale locks, repairs broken JSON, restarts failed jobs, clears stale cache. Runs every 15 min. Этап 3: `check_feelings()` считывает `compute_feelings()` (байесовские чувства граней), при harmony<0.3/restart>0.4 пишет `cache/rebalance_note.json` (маячок). Шаг 2 решений: `_top_facet()` определяет перегруженную грань (по self_model grani), счётчик `overload_runs` в state, при 3+ подряд — алерт «ПЕРЕГРУЗКА». Шаг 3 режимов: `current_phase()` (night 22–07 / day), `is_phase_expected()` — перегрузка грани, ожидаемой для фазы (ночь=Обучение/Рефлексия, день=Исполнение/Реакция), сбрасывает счётчик и не эскалирует.

## Verification
- Run `python scripts/health_check.py` to verify system health
- Run `python scripts/test_llm_analyst.py` to test LLM integration

## Child DOX Index
| File/Dir | Purpose |
|---|---|
| `chain_heartbeat.py` | 5-level event-driven system monitoring (events → modules → pipelines → services → JSON). `compute_feelings()` — Байес-чувства граней (`harmony`/`tension`/`intensity`/`stagnation`/`refinement`/`restart`), пишутся в `system_status()["feelings"]` |
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
| `skill_indexer.py` | Self-improvement: indexes all SKILL.md files into Knowledge Cube (source `skill-indexer`) |
| `latent_domain_detector.py` | Self-improvement: detects latent domains + logical gaps, `--seed` inserts knowledge-gap seeds (source `latent-domain-detector`) |
| `skill_evolution_v2.py` | Self-improvement: read-only audit of installed skills, usage events, KC state (cron 4am) |
| `crystal.py` | Crystal v-prefix анализ самосознания: `_load_self_model` пишет `grani` — распределение Куба по 6 граням (Мысль/Реакция/Рефлексия/Исполнение/Обучение/Управление), маппинг доменов → грани. Запуск: `python scripts/crystal.py --iterative 3` (cron). НЕ конфликтовать с пакетом `crystal/` (v3 CrystalEngine) — это отдельный модуль. **ШАГ 5 исполняет ВСЕ кандидатные воли за цикл**, не одну: аналитика (anomaly_/blindspot_/deepen_/audit_/analyze) — сразу все; тяжёлые (extract_, self_mod_, init_, script, task_for_agent) — по одной за цикл (флаг `heavy_done`). Не менять на `chosen=candidates[0]` — это оставляло backlog аномалий навсегда (2026-08-04). Вернёт пробег ~4x медленнее (20с→83с), это цена разбора всего backlog. |
| `boot.py` | Session restore: `cube_state()` читает Knowledge Cube при старте (total/domains/last_24h), Step 5.3 boot |
