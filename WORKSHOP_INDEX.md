---
name: workshop-index
description: "Auto-generated from WORKSHOP_INDEX.md"
trigger: "When user asks about WORKSHOP_INDEX concepts"
usage: workshop-index
Revisit: 2026-07-31
---

# WORKSHOP_INDEX.md — Индекс мастерской

**Обновлено:** 2026-06-23
**Всего скриптов:** 165
**Активных cron:** 35

---

## СТРУКТУРА

```
hermes/
├── ARBITRAGE_WORKSHOP.md    — каталог кирпичей (77 КБ)
├── ARBITRAGE_IDEAS.md       — схемы с математикой
├── ARBITRAGE_FINDS.md       — результаты разведки
├── HACKER_LOG.md            — обходы барьеров
├── REFERENCES.md            — лучшие ресурсы
├── WORKSHOP_INDEX.md        — ЭТОТ ФАЙЛ
└── scripts/
    ├── CATALOG.json         —分类 всех скриптов (subagent)
    └── ... (165 .py файлов)
```

---

## КАТАЛОГ ПО ОТДЕЛАМ

### Core (ядро системы) — 7 файлов
| Скрипт | Что делает | Когда запускается |
|--------|-----------|-------------------|
| session_boot.py | Загрузка контекста при старте | Каждая сессия |
| session_bridge.py | Сохранение состояния | Конец сессии |
| session_context.py | Контекст из решений/целей | Стар сессии |
| auto_recall.py | Поиск в Knowledge Cube | Перед задачами |
| hermes_hooks.py | Запись событий | После каждого действия |
| event_log.py | Лёгкое логирование | Когда hooks тяжёлые |
| goal_queue.py | Очередь целей | Перед работой |

### Event (событийная система) — 12 файлов
| Скрипт | Что делает | Когда запускается |
|--------|-----------|-------------------|
| event_evolution.py | Ядро: EventMonitor, EvolutionEngine | Авто |
| event_daemon.py | Демон событий | Каждые 2 мин (cron) |
| event_reactor.py | Реакция на KC/ошибки/цели | Авто |
| event_classifier.py | Классификация событий | Авто |
| event_trigger.py | Триггер по сообщениям | На сообщение |
| event_bridge.py | Мост между событиями | Авто |
| event_registry.py | Реестр обработчиков | Авто |
| event_sense.py | Детектирование изменений | Авто |
| event_bus.py | Шина событий | Авто |
| event_autostart.py | Автозапуск | Авто |
| process_events_cron.py | Обработка очереди | Cron |
| _event_daemon.py | Старая версия | Deprecated |

### Knowledge (база знаний) — 15 файлов
| Скрипт | Что делает | Когда запускается |
|--------|-----------|-------------------|
| knowledge_cube.py | Хранение опыта | После задач |
| cube_feeder.py | Наполнение KC | Cron 04:15 |
| cube_categorizer.py | Автокатегоризация | При добавлении |
| cube_to_memory.py | Синхронизация с памятью | Каждые 6 ч |
| classify_entries.py | Классификация записей | Ручное |
| conversation_ingester.py | Извлечение из диалогов | Новые дампы |
| session_dump_ingester.py | Импорт метаданых сессий | Новые дампы |
| explore_domain.py | Исследование домена | Ручное |
| explore_design_domain.py | Исследование дизайна | Ручное |
| explore_white_spot.py | Поиск белых пятен | Ручное |
| latent_domain_detector.py | Скрытые домены | Ручное |
| knowledge_surfacer.py | Поверхностный анализ | Cron 360 мин |
| seed_creative_knowledge.py | Засев творческих знаний | Одноразово |
| seed_tools_knowledge.py | Засев инструментов | Одноразово |
| _analyze_cube_zen.py | Deprecated | Deprecated |

### Telegram (боты и каналы) — 10 файлов
| Скрипт | Что делает | Когда запускается |
|--------|-----------|-------------------|
| telegram_bot.py | Основной бот | Ручное |
| telegram_bridge.py | Мост Telegram | Авто |
| telegram_daily_report.py | Дневной отчёт | Cron 21:00 |
| telegram_delivery_report.py | Отчёт доставки | При результате |
| tg_channel_poster.py | Постинг в каналы | Ручное |
| tg_client.py | Клиент Telegram | Авто |
| salon_booking_bot.py | Бот салона | Broken (aiogram) |
| salon_reminders_wrapper.py | Напоминания салона | Каждый час |
| test_bot.py | Тест бота | Тест |
| test_bot2.py | Тест бота v2 | Тест |

### Web (разведка и парсинг) — 5 файлов
| Скрипт | Что делает | Когда запускается |
|--------|-----------|-------------------|
| web_surfer.py | Скрапинг через playwright | Ручное |
| curiosity_engine.py | Мониторинг HN | Cron 09:00 |
| yt_pipeline.py | YouTube → транскрипт | Ручное |
| auto_fetch_cron.py | Автозагрузка | Disabled |
| market_research.py | Исследование рынка | Cron пн 08:00 |

### Cron (автозадачи) — 10 файлов
| Скрипт | Что делает | Когда запускается |
|--------|-----------|-------------------|
| morning_report_cron.py | Утренний отчёт | Cron 08:00 |
| nightly_brain_scan.py | Ночной скан | Cron 03:00 |
| self_analysis_cron.py | Самоанализ | Cron 02:00 |
| self_assessment_cron.py | Самооценка | Cron 01:00 |
| self_improvement_loop.py | Улучшение | Cron 05:00 |
| skill_evolution_v2.py | Эволюция скиллов | Cron 04:00 |
| skill_evolution_cron.py | Cron эволюции | Deprecated |
| daily_knowledge_report.py | Дневной отчёт знаний | Cron 360 мин |
| dream_memory_cron.py | Консолидация памяти | Event |
| unified_cron.py | Единый cron | Deprecated |

### Proactive (автономия) — 8 файлов
| Скрипт | Что делает | Когда запускается |
|--------|-----------|-------------------|
| autonomous_agent.py | Ядро автономии (2562 строки) | Ручное |
| proactive_doer.py | Проактивный исполнитель | Disabled |
| proactive_executor.py | Исполнитель целей | Event: goal_updated |
| chain_executor.py | Цепочки действий (648 строк) | Ручное |
| action_executor.py | Исполнитель действий | Авто |
| result_producer.py | Продюсер результатов | Event |
| self_healing_monitor.py | Самовосстановление | Event: error |
| self_improvement_loop.py | Улучшение | Cron 05:00 |

### System (мониторинг) — 8 файлов
| Скрипт | Что делает | Когда запускается |
|--------|-----------|-------------------|
| reality_gate.py | Проверка состояния | Session boot |
| system_metrics.py | Метрики системы | Каждые 6 ч |
| system_watcher.py | Наблюдатель | Event: file_changed |
| file_watcher.py | Наблюдатель файлов | Ручное |
| session_manifest.py | Манифест сессий | Session boot |
| recovery_baseline.py | База восстановления | Ручное |
| error_alerter.py | Алерты об ошибках | Авто |
| provider_guard.py | Защита провайдеров | Авто |

### AI/LLM — 6 файлов
| Скрипт | Что делает | Когда запускается |
|--------|-----------|-------------------|
| llm_analyst.py | Анализ через LLM | Disabled |
| llm_classifier.py | Классификатор | Авто |
| llm_filter.py | Фильтрация | Авто |
| openrouter_client.py | Клиент OpenRouter | Авто |
| prompt_compressor.py | Сжатие промптов | Авто |
| switch_provider.py | Переключение провайдеров | Ручное |

### Deprecated / Test — 20+ файлов
Все файлы с префиксом `_`, `test_*`, `check_*`, старые версии (v1, v2).

---

## CRON РАСПИСАНИЕ

### Ночные (00:00-06:00)
- 01:00 — self-assessment
- 02:00 — nightly-self-analysis
- 03:00 — nightly-brain-scan
- 04:00 — skill-evolution
- 04:15 — cube-feeder
- 04:30 — update-runtime-context
- 04:45 — dimension-discovery
- 05:00 — self-improvement-loop

### Дневные (06:00-22:00)
- 08:00 — morning-report
- 09:00 — curiosity-engine
- 10:00 — Trend Scout (все категории)
- 18:00 — Trend Scout (салон)
- 21:00 — daily-report

### Периодические
- Каждые 2 мин — event-heartbeat
- Каждый час — hermes-heartbeat, salon-reminders
- Каждые 6 ч — cube-to-memory, system-metrics, knowledge-surfacer
- Каждые 6 ч — free-api-health-check
- Каждые 2 ч — JARVIS Security Monitor

### По событиям
- session_completed → subconscious-loop, cube-session-ingester, dream-memory
- file_changed → system-watcher
- user_message → event-trigger
- goal_updated → proactive-executor
- error_logged → self-healing-monitor
- action_completed → result-producer
- knowledge_added → cube-categorizer
- result_available → telegram-delivery

---

## ЗАВИСИМОСТИ

```
session_boot.py
├── reality_gate.py (проверка состояния)
├── session_context.py (контекст)
├── auto_recall.py (Knowledge Cube)
├── goal_queue.py (цели)
└── SELF_IDENTITY.md (самосознание)

event_daemon.py (каждые 2 мин)
├── event_reactor.py
├── event_classifier.py
└── process_events_cron.py

chain_executor.py
├── action_executor.py
├── autonomous_agent.py
└── result_producer.py
```

---

## ЧТО НУЖНО СДЕЛАТЬ

1. ✅ Скрипты проиндексированы (165 шт)
2. ✅ Cron расписание задокументировано (45 jobs)
3. ⏳ CATALOG.json создаётся (subagent)
4. ⏳ Дедупликация deprecated файлов
5. ⏳ Интеграция watchdog с file_watcher.py
6. ⏳ Восстановление salon-bot venv
