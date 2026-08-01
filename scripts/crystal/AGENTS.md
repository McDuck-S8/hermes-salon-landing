# Crystal DOX

# Revisit: when self-learning loop modules, departments, or cycle phases change. Last touched: 2026-07-02.

Crystal — self-learning loop для AI агента. v3.2.0. 22 пронумерованных модуля + 6 дополнительных.

## Core Contract

- Crystal изучает систему через: Наблюдение → Анализ → Контекст → Действия → Мониторинг → Эволюция
- Каждый цикл улучшает понимание и эффективность
- Результаты записываются в cache/crystal/ (JSON) и knowledge_cube.db

## Read Before Editing

1. Прочитай scripts/AGENTS.md (родитель)
2. Прочитай этот файл (crystal/AGENTS.md)
3. Определи какой модуль трогаешь
4. Проверь зависимости модуля

## Structure

```
crystal/
├── AGENTS.md                    # Этот файл
│
│   ── Инфраструктура ──
├── __init__.py                  # Пакет: CrystalEngine v3.2.0
├── config.py                    # Конфигурация: пути, отделы, DEFAULT_CONFIG
├── models.py                    # Все dataclass'ы (22 модуля) + save_json/load_json
├── core.py                      # CrystalEngine — оркестратор (583 строки)
│
│   ── Пронумерованные модули (из core.py) ──
├── session_reader.py            # Модуль 1: Session Reader — чтение сессий из state.db
├── pattern_detector.py          # Модуль 2: Pattern Detector — детекция паттернов
├── need_analyzer.py             # Модуль 3: Need Analyzer — формулировка потребностей
├── priority_engine.py           # Модуль 4: Priority Engine — приоритизация
│                                # Модуль 5: User Energy Model — EnergyState (в models.py)
│                                # Модуль 6: Dependency Map — DependencyGraph (в models.py)
├── risk_assessment.py           # Модуль 7: Risk Assessment — оценка рисков proposals
├── dev_proposer.py              # Модуль 8: Development Proposer — генерация actions
├── staleness.py                 # Модуль 9: Staleness Detector — проверка актуальности
├── alerts.py                    # Модуль 10: Proactive Alerts — уведомления
├── memory_integration.py        # Модуль 11: Memory Integration — чтение USER.md + MEMORY.md
├── feedback_loop.py             # Модуль 12: Feedback Loop — оценка эффективности
├── versioning.py                # Модуль 13: Versioning — changelog
├── synergy.py                   # Модуль 14: Cross-department Synergy — связи между отделами
├── goals.py                     # Модуль 15: Long-term Goals — трекинг прогресса
├── intelligence.py              # Модуль 16: External Intelligence — сканирование внешнего мира
├── testing.py                   # Модуль 17: Automated Testing — тест proposals
├── rollback.py                  # Модуль 18: Rollback — откат к версии
├── knowledge_base.py            # Модуль 19: Knowledge Base — база решённых проблем
├── communication.py             # Модуль 20: Communication Adapter — стиль общения
├── resources.py                 # Модуль 21: Resource Monitor — бюджет и лимиты
├── self_evolution.py            # Модуль 22: Self-Evolution — самоулучшение модулей
│
│   ── Дополнительные модули (без номера) ──
├── semantic_parser.py           # Семантический парсер — LLM-анализ намерений (OpenCode Zen)
├── conversation_analyzer.py     # Полный анализ переписки: намерения, цели, предсказания
├── error_analyzer.py            # Анализатор ошибок — чтение логов, паттерны ошибок
├── executor.py                  # ProposalExecutor — исполнение proposals (create/patch skills)
├── brief.py                     # Crystal Brief — краткая выжимка по ключевым словам
├── growth_loop.py               # Growth Loop — замкнутый контур роста (поведение)
```

## Correct Cycle (from core.py run_full_cycle)

```
Фаза 1: Наблюдение (Observation)
  → session_reader.py   — SessionReader.read() — чтение сессий из state.db
  → pattern_detector.py  — PatternDetector.detect() — нахождение повторяющихся паттернов

Фаза 2: Анализ (Analysis)
  → need_analyzer.py     — NeedAnalyzer.analyze() — формулировка потребностей из паттернов
  → priority_engine.py   — PriorityEngine.prioritize() — сортировка urgency × impact / effort

Фаза 3: Контекст (Context)
  → memory_integration.py — MemoryIntegration.read() — чтение USER.md + MEMORY.md
  → semantic_parser.py    — SemanticParser.parse() — LLM-анализ переписки (намерения, цели)

Фаза 4: Действия (Actions)
  → dev_proposer.py       — DevelopmentProposer.propose() — генерация proposals из needs
  → synergy.py            — SynergyFinder.find() — межотделовые связи
  → risk_assessment.py    — RiskAssessor.assess() — оценка безопасности
  → testing.py            — ProposalTester.test() — тест перед применением
  → executor.py           — ProposalExecutor — исполнение (create/patch skills, update dox)
  → feedback_loop.py      — FeedbackLoop.execute_and_evaluate() — оценка результата

Фаза 5: Мониторинг (Monitoring)
  → staleness.py          — StalenessDetector.check() — что устарело
  → alerts.py             — AlertManager.check() — проактивные уведомления
  → resources.py          — ResourceMonitor.check() — бюджет и дисковое пространство

Фаза 6: Эволюция (Evolution)
  → self_evolution.py     — SelfEvolution.evolve() — улучшение модулей
  → goals.py              — GoalTracker.update() — обновление прогресса целей
  → intelligence.py       — IntelScanner.scan() — внешние источники
  → communication.py      — CommunicationAdapter.adapt() — адаптация стиля общения
```

## Module Details

### Infrastructure

| Файл | Назначение |
|------|-----------|
| `__init__.py` | Экспорт CrystalEngine, Signal, Pattern, Need, Proposal, Assessment, ProposalExecutor, ConversationAnalyzer. Версия 3.2.0 |
| `config.py` | HERMES_HOME, Paths (JSON файлы), DEPARTMENTS (8 отделов), DEFAULT_CONFIG, get_department(), ensure_dirs() |
| `models.py` | 22 dataclass'а + save_json()/load_json(). Signal, Pattern, Need, PrioritizedItem, EnergyState, DependencyGraph, RiskAssessment, Proposal, StalenessItem, Alert, MemoryEntry, Assessment, ChangelogEntry, Synergy, Goal, IntelItem, TestResult, Snapshot, KnowledgeEntry, CommunicationProfile, ResourceState, EvolutionEntry |
| `core.py` | CrystalEngine: оркестратор, run_full_cycle(), run_department(), analyze_errors(), execute_with_feedback(), summary() |

### Module 1: Session Reader (`session_reader.py`)
- **Что делает**: Читает JSONL сессии из state.db, извлекает сырые сигналы
- **Вход**: messages из SQLite (role=user/assistant)
- **Выход**: list[Signal] — classified by type (request/correction/frustration/workflow/unmet)
- **Ключевые слова**: CORRECTION_KEYWORDS, FRUSTRATION_KEYWORDS, WORKFLOW_KEYWORDS, UNMET_KEYWORDS

### Module 2: Pattern Detector (`pattern_detector.py`)
- **Что делает**: Находит повторяющиеся паттерны из сигналов
- **Типы паттернов**: correction_loop, frustration_spike, missing_knowledge, workflow_success, unmet_need, department_focus
- **Вход**: list[Signal]
- **Выход**: list[Pattern]

### Module 3: Need Analyzer (`need_analyzer.py`)
- **Что делает**: Из паттернов формулирует потребности
- **Вход**: list[Pattern]
- **Выход**: list[Need] — отсортированы по приоритету

### Module 4: Priority Engine (`priority_engine.py`)
- **Что делает**: Определяет что делать первым (urgency × impact / effort)
- **Учет**: energy пользователя, вес отдела (ai-core=1.2, devops=1.1, etc.)
- **Вход**: needs, energy, dependencies
- **Выход**: list[PrioritizedItem]

### Modules 5-6: Energy & Dependencies (в `models.py`)
- **Module 5: User Energy Model** — EnergyState (level: low/medium/high, score)
- **Module 6: Dependency Map** — DependencyGraph (nodes, edges с типами blocker/enabler/coupled)
- Отдельных .py файлов НЕТ — это dataclass'ы в models.py

### Module 7: Risk Assessment (`risk_assessment.py`)
- **Что делает**: Оценивает безопасность каждого proposal
- **Уровни**: safe, moderate, risky, critical
- **Факторы**: tested (снижает), auto_apply (повышает), ai-core (повышает)

### Module 8: Development Proposer (`dev_proposer.py`)
- **Что делает**: Из потребностей генерирует конкретные действия (create_skill, patch_skill, update_dox)
- **Вход**: needs, knowledge
- **Выход**: list[Proposal] — max 5 за запуск

### Module 9: Staleness Detector (`staleness.py`)
- **Что делает**: Проверяет актуальность скиллов (>30 дней) и конфигов (>60 дней)
- **Проверяет**: SKILLS_DIR (mtime SKILL.md), CONFIG_PATH

### Module 10: Proactive Alerts (`alerts.py`)
- **Что делает**: Генерирует уведомления о проблемах
- **Триггеры**: frustration ≥ 5, corrections ≥ 3, нет активности, critical patterns

### Module 11: Memory Integration (`memory_integration.py`)
- **Что делает**: Читает USER.md + MEMORY.md для контекста
- **Методы**: read(), write_preference(), get_context_summary()

### Module 12: Feedback Loop (`feedback_loop.py`)
- **Что делает**: Оценивает помогло ли изменение (execute → measure → learn)
- **Вход**: proposal + engine state (before/after snapshot)
- **Выход**: Assessment + история в feedback_history.json

### Module 13: Versioning (`versioning.py`)
- **Что делает**: Управление changelog
- **Методы**: get_changelog(), add_entry(), get_recent(), get_by_version()

### Module 14: Cross-department Synergy (`synergy.py`)
- **Что делает**: Находит связи между отделами (content_pipeline, tech_stack, data_flow, skill_reuse)
- **Паттерны**: youtube↔social-media, youtube↔monetization, ai-core↔devops, ai-core↔telegram-bots, etc.

### Module 15: Long-term Goals (`goals.py`)
- **Что делает**: Отслеживает прогресс стратегических целей
- **Дефолты**: Стабильная работа AI, Автоматизация контента, Монетизация, Надёжная инфраструктура

### Module 16: External Intelligence (`intelligence.py`)
- **Что делает**: Сканирует внешний мир (GitHub trending, AI новости, инструменты)
- **Источники**: DuckDuckGo API

### Module 17: Automated Testing (`testing.py`)
- **Что делает**: Тест proposal перед применением
- **Уровни**: quick (валидация), standard (доп. проверки), full (syntax + зависимости)

### Module 18: Rollback (`rollback.py`)
- **Что делает**: Откат к указанной версии через снэпшоты
- **Методы**: create_snapshot(), rollback(), list_snapshots()

### Module 19: Knowledge Base (`knowledge_base.py`)
- **Что делает**: Хранит решённые проблемы, рабочие подходы
- **Методы**: find() (поиск по словам), add(), get_by_department(), get_confident()

### Module 20: Communication Adapter (`communication.py`)
- **Что делает**: Адаптирует стиль общения (length, tone, technicality)
- **Формат**: format_response() — обрезка, списки

### Module 21: Resource Monitor (`resources.py`)
- **Что делает**: Мониторит бюджет и лимиты (API calls, tokens, disk usage)
- **Методы**: check(), suggest_model() (deepseek/mimo/claude)

### Module 22: Self-Evolution (`self_evolution.py`)
- **Что делает**: Оценивает и улучшает модули (optimize, refactor, new_module)

### Semantic Parser (`semantic_parser.py`)
- **Что делает**: LLM-анализ переписки через OpenCode Zen (не ключевые слова!)
- **Вход**: сообщения пользователя из state.db (сэмплинг: последние 50 + равномерная выборка)
- **Выход**: goals, frustration, activities, context, relationship
- **Кэш**: semantic_analysis.json (TTL 1 час)

### Conversation Analyzer (`conversation_analyzer.py`)
- **Что делает**: Полный анализ переписки: insights, ideas, problems, workflows, intents, goals, predictions, frustration
- **Методы**: analyze_full() — comprehensive analysis с кэшированием

### Error Analyzer (`error_analyzer.py`)
- **Что делает**: Анализирует реальные логи ошибок (9 типов паттернов)
- **Типы**: model_not_supported, memory_overflow, api_timeout, lsp_failure, terminal_timeout, entry_not_found, file_blocked, tool_loop, non_retryable
- **Выход**: health_score (0-100)

### Proposal Executor (`executor.py`)
- **Что делает**: Исполняет proposals — создаёт/патчит скиллы, обновляет AGENTS.md/MEMORY.md
- **Действия**: create_skill, patch_skill, update_dox, update_memory + mappings из conversation_analyzer
- **Дополнительно**: генерирует контент из error_analyzer для новых скиллов

### Crystal Brief (`brief.py`)
- **Что делает**: Краткая выжимка по ключевым словам (frustration/correction/unfinished/positive)
- **Запуск**: `python -m crystal.brief` или `from crystal.brief import crystal_brief`

### Growth Loop (`growth_loop.py`)
- **Что делает**: Замкнутый контур роста — поведение, а не аналитика
- **Цикл**: frustration → record → behavior_change → check → verify
- **Файлы**: crystal/data/growth.json (lessons, behavior_changes, frustration_log)

## Key Methods

### CrystalEngine (core.py)
```python
engine = CrystalEngine()

# Основной цикл
result = engine.run_full_cycle()

# Чтение сессий
signals = engine.read_sessions()

# Семантический поиск
context = engine.recall_context("query", limit=5)

# Анализ разговоров
proposals = engine.analyze_conversation(days=7)

# Ошибки
errors = engine.analyze_errors(hours=48)

# Исполнение с feedback
results = engine.execute_with_feedback(proposals, dry_run=False)

# Статистика feedback
stats = engine.feedback_stats()

# Сводка
print(engine.summary())
```

## Integration

### Session Recall
- Crystal интегрирован с session_recall.py
- `engine.recall_context(query)` — семантический поиск по истории
- Автоматически обогащает анализ контекстом

### Knowledge Cube
- Результаты записываются в knowledge_cube.db
- Каждый цикл: experiences, patterns, proposals
- KC растёт с каждым запуском

### Event Bus
- Crystal эмитит события через emit_event: session_completed, error_logged
- Интегрирован с event_bus.py

### Autonomous Agent
- Crystal предоставляет контекст для решений
- `collect_system_state()` включает session_context

## Rules

### Не ломай цикл
- Наблюдение → Анализ → Контекст → Действия → Мониторинг → Эволюция
- Каждая фаза зависит от предыдущей
- Не пропускай фазы

### Интеграция
- Используй session_recall для поиска
- Записывай результаты в cache/crystal/ (JSON)
- Логируй в crystal.log

### Тестирование
```bash
# Summary
python scripts/crystal.py --summary

# Полный цикл
python scripts/crystal.py

# Brief (быстрый анализ)
python -m crystal.brief

# Growth Loop stats
python -m crystal.growth_loop
```

## Verification

- [x] core.py загружается без ошибок
- [x] recall_context() работает (через session_recall)
- [x] Результаты записываются в cache/crystal/
- [x] Логи пишутся в crystal.log
- [x] Все 30 .py файлов существуют и содержат валидный Python
