# Graph Report - scripts  (2026-06-18)

## Corpus Check
- 187 files · ~124,031 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2002 nodes · 5296 edges · 96 communities detected
- Extraction: 51% EXTRACTED · 49% INFERRED · 0% AMBIGUOUS · INFERRED: 2599 edges (avg confidence: 0.61)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 86|Community 86]]
- [[_COMMUNITY_Community 87|Community 87]]
- [[_COMMUNITY_Community 88|Community 88]]
- [[_COMMUNITY_Community 89|Community 89]]
- [[_COMMUNITY_Community 90|Community 90]]
- [[_COMMUNITY_Community 91|Community 91]]
- [[_COMMUNITY_Community 92|Community 92]]
- [[_COMMUNITY_Community 93|Community 93]]
- [[_COMMUNITY_Community 94|Community 94]]
- [[_COMMUNITY_Community 95|Community 95]]

## God Nodes (most connected - your core abstractions)
1. `Proposal` - 81 edges
2. `CrystalEngine` - 78 edges
3. `Paths` - 67 edges
4. `Pattern` - 67 edges
5. `Signal` - 66 edges
6. `Need` - 52 edges
7. `KnowledgeEntry` - 52 edges
8. `load()` - 49 edges
9. `ErrorAnalyzer` - 49 edges
10. `ProposalExecutor` - 49 edges

## Surprising Connections (you probably didn't know these)
- `auth_code()` --calls--> `load()`  [INFERRED]
  scripts\tg_client.py → scripts\session_bridge.py
- `Добавить новое решение` --uses--> `KnowledgeEntry`  [INFERRED]
  scripts\crystal\knowledge_base.py → scripts\crystal\models.py
- `Crystal v3 — Модуль 1: Session Reader Читает сессии из state.db, извлекает сигна` --uses--> `Signal`  [INFERRED]
  scripts\crystal\session_reader.py → scripts\crystal\models.py
- `Читает сессии из state.db, возвращает список Signal` --uses--> `Signal`  [INFERRED]
  scripts\crystal\session_reader.py → scripts\crystal\models.py
- `Извлечь сигналы из одной сессии` --uses--> `Signal`  [INFERRED]
  scripts\crystal\session_reader.py → scripts\crystal\models.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (179): AlertManager, Crystal v3 — Модуль 10: Proactive Alerts Проактивные уведомления, Генерирует проактивные уведомления, Проверить и сгенерировать уведомления, CommunicationAdapter, Crystal v3 — Модуль 20: Communication Adapter Стиль общения, Адаптирует стиль общения под пользователя, Адаптировать профиль по feedback (+171 more)

### Community 1 - "Community 1"
Cohesion: 0.02
Nodes (187): compute_weights(), get_adjusted_score(), _load_outcomes(), Compute and save weights to file., Apply learned weight to a base score.      Reads from cached weights file (updat, Print current weights for debugging., Record the outcome of an action., Compute per-action success rates and weights.      Returns dict keyed by action_ (+179 more)

### Community 2 - "Community 2"
Cohesion: 0.02
Nodes (180): count_recent_errors(), get_current_provider(), main(), Решение: нужно ли переключаться., Считает ошибки API за последние N минут из error.log., read_state(), should_switch(), write_state() (+172 more)

### Community 3 - "Community 3"
Cohesion: 0.02
Nodes (139): analyze_batch(), extract_json(), get_db(), Send a small batch to Zen, handle reasoning models., ConversationAnalyzer, Проверить, является ли сообщение мусором, Извлечь инсайты из сообщений, Анализатор полной переписки (+131 more)

### Community 4 - "Community 4"
Cohesion: 0.04
Nodes (57): alert(), AlertManager, check_hermes_process(), check_lm_studio(), check_log_anomalies(), generate_report(), get_cpu_usage(), get_disk_usage() (+49 more)

### Community 5 - "Community 5"
Cohesion: 0.04
Nodes (67): build_alert_message(), check_file_for_errors(), extract_error_summary(), extract_job_info(), get_last_files(), main(), Формирует Markdown-сообщение для отправки в Telegram., Возвращает последние n .md файлов в директории job-а,     отсортированных по вре (+59 more)

### Community 6 - "Community 6"
Cohesion: 0.05
Nodes (43): BACKGROUND RUNNER — Runs integration in background.  This actually works. Not a, Run integration in background., run_background(), CoreEngine, CORE ENGINE — Real System, Real Data, Real Benefits.  Connects to:   - Knowle, Load REAL Lavra knowledge., Connect to REAL Session Database., Find REAL knowledge gaps from actual data. (+35 more)

### Community 7 - "Community 7"
Cohesion: 0.04
Nodes (48): load_domain_definitions(), main(), normalize_text(), Main entry point for CLI usage, Load domain definitions from YAML config, Normalize text for keyword matching, Score an entry against all domains, return (domain, score), Tag all entries, return (tagged_entries, stats) (+40 more)

### Community 8 - "Community 8"
Cohesion: 0.05
Nodes (59): extract_dialog(), extract_knowledge_from_dialog(), ingest_conversations(), load_ingested(), Ingest full conversation content from session dumps., Show ingestion stats., Extract full dialog from session dump., Check if message is a cron prompt or boilerplate. (+51 more)

### Community 9 - "Community 9"
Cohesion: 0.06
Nodes (49): create_preventive_entry(), group_by_pattern(), main(), make_hash(), Read all verified fixes from the database., Group fixes by (issue_type, fix_type) pair., Create a unique hash for deduplication., Create a preventive Knowledge Cube entry for a recurring pattern. (+41 more)

### Community 10 - "Community 10"
Cohesion: 0.05
Nodes (45): check_all(), check_error_spikes(), check_goal_changes(), check_kc_new_entries(), check_session_context(), load_state(), log(), Detect spikes in error log and alert. (+37 more)

### Community 11 - "Community 11"
Cohesion: 0.07
Nodes (43): analyze_error_patterns(), auto_create_skills(), _connect(), _fetch_all(), _generate_skill_md(), generate_suggestions(), _get_existing_skills(), identify_cube_patterns() (+35 more)

### Community 12 - "Community 12"
Cohesion: 0.06
Nodes (21): ensure_dirs(), get_department(), Crystal v3 — Конфигурация Пути, настройки, дефолты, Определить отдел по тексту, Создать все необходимые директории, Crystal v3 — Модуль анализа переписки Анализирует ВСЮ историю сообщений для извл, Crystal v3 — Анализатор ошибок Читает реальные логи, находит конкретные проблемы, Crystal v3 — Модуль 11: Memory Integration Читает USER.md + MEMORY.md (+13 more)

### Community 13 - "Community 13"
Cohesion: 0.08
Nodes (24): auto_consult(), Skip consultation for trivial actions., Automatically consult the brain before a task.          Usage:         result, should_skip_consult(), Brain, consult(), get_brain(), Active decision-maker built on top of Knowledge Cube. (+16 more)

### Community 14 - "Community 14"
Cohesion: 0.09
Nodes (32): auto_recall(), auto_recall_with_lavra(), detect_domain(), extract_keywords(), format_experience(), get_db(), Search using FTS5 full-text search., Fallback search using LIKE when FTS is unavailable. (+24 more)

### Community 15 - "Community 15"
Cohesion: 0.09
Nodes (14): EverOSMemory, EverOS Memory Client — Hermes integration with cloud API.  Установка: pip instal, Проверить статус асинхронной задачи., Клиент EverOS для Hermes.      Поддерживает: добавление памяти, поиск, мониторин, Добавить сообщения в память EverOS.          Args:             user_id: идентифи, Поиск в памяти EverOS.          Args:             user_id: владелец памяти, _serialize(), EverOS (+6 more)

### Community 16 - "Community 16"
Cohesion: 0.11
Nodes (21): Aspect, check_depth(), decompose_request(), Depth, extract_keywords(), fill_aspect(), get_routing_report(), process_request() (+13 more)

### Community 17 - "Community 17"
Cohesion: 0.13
Nodes (13): UNIFIED SYSTEM — Everything connected, everything works.  All systems in one pla, Get a connection to the unified DB, creating if needed., Ensure connections are closed on garbage collection., Find REAL knowledge gaps., Learn something new. This is the self-learning part., Execute a chain action., Everything connected. Everything works., Get all self-learned insights. (+5 more)

### Community 18 - "Community 18"
Cohesion: 0.11
Nodes (23): activate(), _build_profile(), count_agents(), deactivate(), get_active(), get_agent(), list_agents(), list_divisions() (+15 more)

### Community 19 - "Community 19"
Cohesion: 0.15
Nodes (21): add_task_memory(), _ensure_entity(), _ensure_relation(), _extract_entities(), _load_graph(), _load_sync_state(), query_memory(), Add relation if not exists. (+13 more)

### Community 20 - "Community 20"
Cohesion: 0.2
Nodes (17): check_situation(), _ensure(), growth_stats(), init_from_analysis(), _load(), Growth Loop — замкнутый контур роста Crystal  Цикл:   Пользователь злится → Я за, Простое ключевое слово-матчинг, Инициализирую рост из семантического анализа — ОДИН раз.     Это НАЧАЛЬНАЯ ТОЧКА (+9 more)

### Community 21 - "Community 21"
Cohesion: 0.13
Nodes (9): JARVISReal, JARVIS — Real Integration with Existing Systems.  Connects to:   - Knowledge Cub, Get current system context from REAL data., Analyze what the user might need based on REAL data., Suggest based on REAL knowledge., Real status of connected systems., Real JARVIS — connected to actual data., Verify real data sources exist. (+1 more)

### Community 22 - "Community 22"
Cohesion: 0.18
Nodes (15): detect_type(), load_state(), main(), make_key(), parse_tags(), parse_ts(), process_experiences(), Парсит tags из JSON-строки. (+7 more)

### Community 23 - "Community 23"
Cohesion: 0.2
Nodes (15): check_broken_json(), check_dead_jobs(), check_stale_cache(), check_stale_locks(), fix_broken_json(), load_state(), main(), Proactive DOER — автономный исполнитель фиксов.  В отличие от self_healing_monit (+7 more)

### Community 24 - "Community 24"
Cohesion: 0.25
Nodes (15): build_context(), get_action_weights_context(), get_active_goals_context(), get_fix_success_rate(), get_recent_decisions_context(), get_session_bridge_context(), _load_json(), Load active goals from goal queue (WP-5). (+7 more)

### Community 25 - "Community 25"
Cohesion: 0.21
Nodes (8): compress_prompt(), PromptCompressor, Keep important parts (beginning, end, key markers), truncate middle., Hard truncate keeping first/last portions., Lightweight prompt compressor using token counting + heuristics., Convenience function., Compress prompt to target token count.                  Strategies (in order):, Find and compress repetitive blocks (logs, stack traces, repeated patterns).

### Community 26 - "Community 26"
Cohesion: 0.21
Nodes (13): fetch_knowledge(), format_timestamp(), get_db_path(), group_by_domain(), main(), parse_tags(), print_report(), Группирует записи по axis_domain. (+5 more)

### Community 27 - "Community 27"
Cohesion: 0.28
Nodes (12): check_for_changes(), handle_crystal_tasks(), handle_new_data_file(), handle_new_session_dump(), load_processed(), log(), main(), One-shot check for new files in watched directories. (+4 more)

### Community 28 - "Community 28"
Cohesion: 0.23
Nodes (12): get_schedule_interval_minutes(), load_state(), main(), parse_cron_list(), parse_datetime(), Self-Healing Monitor for Hermes cron jobs.  Checks all cron jobs via `hermes cro, Estimate interval in minutes from schedule string like 'every 15m' or '0 2 * * *, Parse a datetime string, handling multiple formats. (+4 more)

### Community 29 - "Community 29"
Cohesion: 0.22
Nodes (12): classify_action(), extract_output_type(), extract_triggers(), find_related_from_body(), index_all_skills(), parse_frontmatter(), Parse YAML-like frontmatter between --- markers., Determine primary action type from name, description, and tags. (+4 more)

### Community 30 - "Community 30"
Cohesion: 0.29
Nodes (11): _db_query(), detect_cron_anomalies(), detect_disk_anomaly(), detect_knowledge_anomalies(), detect_script_anomalies(), _load_json(), main(), Find domains with high failure rates or sudden drops. (+3 more)

### Community 31 - "Community 31"
Cohesion: 0.39
Nodes (11): check_recent_errors(), load_state(), main(), Проверяет логи за последние 5 минут на ошибки провайдера., Переключает на указанного провайдера., read_config(), run_once(), save_state() (+3 more)

### Community 32 - "Community 32"
Cohesion: 0.23
Nodes (11): Conflict, detect_conflicts(), FileScope, Multi-Agent File-Scope Conflict Detection.  Lavra pattern: detect when multiple, Files an agent intends to modify., A file targeted by multiple agents., Detect file-scope conflicts between parallel tasks.          Returns list of con, Suggest how to resolve conflicts. (+3 more)

### Community 33 - "Community 33"
Cohesion: 0.17
Nodes (6): Читает USER.md + MEMORY.md         Возвращает список записей, Безопасное чтение файла, Парсит USER.md в записи, Парсит MEMORY.md в записи, Записать новое предпочтение в USER.md, Краткая сводка из memory

### Community 34 - "Community 34"
Cohesion: 0.18
Nodes (4): Парсить один лог-файл, Оценка здоровья системы (0-100), Анализировать логи за последние N часов, Получить список лог-файлов

### Community 35 - "Community 35"
Cohesion: 0.29
Nodes (9): find_duplicates(), find_stale(), main(), normalize(), Parse memory file into individual entries (§-separated)., Normalize text for dedup comparison., Find exact and near-duplicate entries., Find entries that reference completed/obsolete items. (+1 more)

### Community 36 - "Community 36"
Cohesion: 0.31
Nodes (9): analyze_session_patterns(), generate_report(), get_recent_sessions(), load_state(), main(), Get sessions from last N hours., Analyze sessions for common failure patterns., Generate self-assessment report. (+1 more)

### Community 37 - "Community 37"
Cohesion: 0.27
Nodes (9): crystal_brief(), _find_patterns(), Crystal Brief — второй мозг Hermes.  Что делает:   1. Читает последние сессии из, Найти повторяющиеся паттерны в сообщениях пользователя, Краткая сводка по сессиям, Дать мне короткую выжимку: что происходит, что повторяется, что бесит., Прочитать последние сессии из state.db, _read_sessions() (+1 more)

### Community 38 - "Community 38"
Cohesion: 0.39
Nodes (7): extract_bigrams(), extract_words(), load_domain_definitions(), main(), Extract words from text, both English and Russian, Extract word bigrams for better matching, score_entry()

### Community 39 - "Community 39"
Cohesion: 0.32
Nodes (7): detect_domain(), import_to_cube(), parse_jsonl(), Import Lavra knowledge.jsonl into Knowledge Cube.  Reads 217 entries from OMP-Po, Parse a JSONL line, handling escaped JSON., Detect domain from content and tags., Import Lavra knowledge into Knowledge Cube.

### Community 40 - "Community 40"
Cohesion: 0.39
Nodes (7): evolve_skill(), find_skill_path(), load_state(), main(), Find SKILL.md for a skill name., Run simple_evolve on a skill. Returns summary dict., save_state()

### Community 41 - "Community 41"
Cohesion: 0.36
Nodes (7): calculate_risk(), main(), Scan a single file for vulnerability patterns., Scan a complete skill directory., Calculate risk score from findings., scan_file(), scan_skill()

### Community 42 - "Community 42"
Cohesion: 0.36
Nodes (6): auth_code(), create_channel(), get_client(), list_channels(), Telegram User Client - Telethon Управление каналами, группами, ботами от имени, send_message()

### Community 43 - "Community 43"
Cohesion: 0.48
Nodes (5): check_cron_jobs(), check_cube(), check_disk(), check_webui(), main()

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (1): Быстрая статистика по сессиям Hermes из state.db. Вывод: количество сессий, сооб

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (0): 

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): Diagnostic: check Knowledge Cube domain health

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (2): Dependency, Зависимость между компонентами

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (0): 

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (0): 

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (0): 

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (0): 

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (0): 

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (0): 

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): Преобразовать pydantic объект в dict рекурсивно.

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (0): 

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (0): 

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (0): 

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (0): 

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (0): 

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (0): 

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (0): 

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (0): 

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (0): 

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (0): 

### Community 65 - "Community 65"
Cohesion: 1.0
Nodes (0): 

### Community 66 - "Community 66"
Cohesion: 1.0
Nodes (0): 

### Community 67 - "Community 67"
Cohesion: 1.0
Nodes (0): 

### Community 68 - "Community 68"
Cohesion: 1.0
Nodes (0): 

### Community 69 - "Community 69"
Cohesion: 1.0
Nodes (0): 

### Community 70 - "Community 70"
Cohesion: 1.0
Nodes (0): 

### Community 71 - "Community 71"
Cohesion: 1.0
Nodes (0): 

### Community 72 - "Community 72"
Cohesion: 1.0
Nodes (0): 

### Community 73 - "Community 73"
Cohesion: 1.0
Nodes (0): 

### Community 74 - "Community 74"
Cohesion: 1.0
Nodes (0): 

### Community 75 - "Community 75"
Cohesion: 1.0
Nodes (0): 

### Community 76 - "Community 76"
Cohesion: 1.0
Nodes (0): 

### Community 77 - "Community 77"
Cohesion: 1.0
Nodes (0): 

### Community 78 - "Community 78"
Cohesion: 1.0
Nodes (0): 

### Community 79 - "Community 79"
Cohesion: 1.0
Nodes (0): 

### Community 80 - "Community 80"
Cohesion: 1.0
Nodes (0): 

### Community 81 - "Community 81"
Cohesion: 1.0
Nodes (0): 

### Community 82 - "Community 82"
Cohesion: 1.0
Nodes (0): 

### Community 83 - "Community 83"
Cohesion: 1.0
Nodes (0): 

### Community 84 - "Community 84"
Cohesion: 1.0
Nodes (0): 

### Community 85 - "Community 85"
Cohesion: 1.0
Nodes (0): 

### Community 86 - "Community 86"
Cohesion: 1.0
Nodes (0): 

### Community 87 - "Community 87"
Cohesion: 1.0
Nodes (0): 

### Community 88 - "Community 88"
Cohesion: 1.0
Nodes (0): 

### Community 89 - "Community 89"
Cohesion: 1.0
Nodes (0): 

### Community 90 - "Community 90"
Cohesion: 1.0
Nodes (0): 

### Community 91 - "Community 91"
Cohesion: 1.0
Nodes (0): 

### Community 92 - "Community 92"
Cohesion: 1.0
Nodes (0): 

### Community 93 - "Community 93"
Cohesion: 1.0
Nodes (0): 

### Community 94 - "Community 94"
Cohesion: 1.0
Nodes (0): 

### Community 95 - "Community 95"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **639 isolated node(s):** `Record the outcome of an action.`, `Compute per-action success rates and weights.      Returns dict keyed by action_`, `Compute and save weights to file.`, `Apply learned weight to a base score.      Reads from cached weights file (updat`, `Print current weights for debugging.` (+634 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 44`** (2 nodes): `session_stats.py`, `Быстрая статистика по сессиям Hermes из state.db. Вывод: количество сессий, сооб`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (2 nodes): `w()`, `_cube_report.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (2 nodes): `Diagnostic: check Knowledge Cube domain health`, `_diag_cube.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (2 nodes): `Dependency`, `Зависимость между компонентами`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `analyze_cube.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `auto_fetch_cron.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `check_indent.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `check_schema.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `dream_memory_cron.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `event_trigger.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `Преобразовать pydantic объект в dict рекурсивно.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `filter_needs.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `health_check.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `ingest_sessions.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `insert_mobile_mcp_kb.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `morning_report_cron.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `nightly_brain_scan.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `process_events_cron.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (1 nodes): `run_crystal_now.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `second_pass.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (1 nodes): `seed_creative_knowledge.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `seed_tools_knowledge.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (1 nodes): `self_analysis_cron.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (1 nodes): `show_data.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (1 nodes): `show_needs_report.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `subconscious_loop_cron.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (1 nodes): `system_watcher.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 71`** (1 nodes): `test_bot.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 72`** (1 nodes): `test_bot2.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 73`** (1 nodes): `unified_cron.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 74`** (1 nodes): `_analyze_unknown.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 75`** (1 nodes): `_domain_analysis.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 76`** (1 nodes): `_missing_domains.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 77`** (1 nodes): `_scan_stubs.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 78`** (1 nodes): `post_all.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 79`** (1 nodes): `post_debug.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 80`** (1 nodes): `post_debug2.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 81`** (1 nodes): `post_final.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 82`** (1 nodes): `post_final2.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 83`** (1 nodes): `post_frontier.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 84`** (1 nodes): `post_urls.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 85`** (1 nodes): `post_with_images.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 86`** (1 nodes): `read_posts.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 87`** (1 nodes): `send_test.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 88`** (1 nodes): `send_test2.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 89`** (1 nodes): `autonomous_test.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 90`** (1 nodes): `fix_bom.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 91`** (1 nodes): `fix_encoding.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 92`** (1 nodes): `_render_eevee.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 93`** (1 nodes): `_render_fixed.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 94`** (1 nodes): `_render_min.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 95`** (1 nodes): `_render_script.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ProposalExecutor` connect `Community 0` to `Community 1`, `Community 3`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `run()` connect `Community 2` to `Community 1`, `Community 3`, `Community 4`, `Community 5`, `Community 9`, `Community 23`, `Community 27`, `Community 28`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `main()` connect `Community 0` to `Community 1`, `Community 3`, `Community 12`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `Proposal` (e.g. with `CrystalEngine` and `Crystal v3 — Главный движок CrystalEngine — оркестрирует все 23 модуля`) actually correct?**
  _`Proposal` has 78 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `CrystalEngine` (e.g. with `Paths` and `Signal`) actually correct?**
  _`CrystalEngine` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 65 inferred relationships involving `Paths` (e.g. with `CrystalEngine` and `Crystal v3 — Главный движок CrystalEngine — оркестрирует все 23 модуля`) actually correct?**
  _`Paths` has 65 INFERRED edges - model-reasoned connections that need verification._
- **Are the 65 inferred relationships involving `Pattern` (e.g. with `AlertManager` and `Crystal v3 — Модуль 10: Proactive Alerts Проактивные уведомления`) actually correct?**
  _`Pattern` has 65 INFERRED edges - model-reasoned connections that need verification._