---
name: crystal-self-learning
category: self-improvement
description: Crystal — self-learning loop: наблюдение → анализ → действия → эволюция. 22 модуля, 8 отделов, полный цикл самосознания агента.
usage: |
  Загрузи этот skill когда нужно:
  - Запустить полный цикл самосознания (crystal run)
  - Проанализировать недавние сессии, найти паттерны
  - Сгенерировать предложения по улучшению (proposals)
  - Получить краткую выжимку по ключевым словам (crystal brief)
  - Проанализировать ошибки из логов (crystal analyze-errors)
  - Проверить устаревшие знания и получить проактивные алерты
  - Обновить документацию модуля (AGENTS.md) после изменений
---

# Crystal Self-Learning Loop

Crystal v3.2.0 — система самосознания AI агента. Наблюдает, анализирует, предлагает улучшения, самоэволюционирует.

## Быстрый старт

```bash
# Полный цикл
python scripts/crystal/core.py --full-cycle

# Brief по ключевым словам
python scripts/crystal/brief.py --keywords "agent, memory, skill"

# Анализ ошибок
python scripts/crystal/error_analyzer.py

# Исполнение proposal
python scripts/crystal/executor.py --proposal-id <id>
```

## Архитектура

```
crystal/
├── core.py              # CrystalEngine — оркестратор полного цикла
├── config.py            # Конфигурация: 8 отделов, пути, константы
├── models.py            # 22 dataclass'а: Signal, Pattern, Need, Proposal и др.
├── AGENTS.md            # Полная документация

├── session_reader.py    # Модуль 1: Session Reader
├── pattern_detector.py  # Модуль 2: Pattern Detector
├── need_analyzer.py     # Модуль 3: Need Analyzer
├── priority_engine.py   # Модуль 4: Priority Engine
├── risk_assessment.py   # Модуль 7: Risk Assessment
├── dev_proposer.py      # Модуль 8: Development Proposer
├── staleness.py         # Модуль 9: Staleness Detector
├── alerts.py            # Модуль 10: Proactive Alerts
├── memory_integration.py# Модуль 11: Memory Integration
├── feedback_loop.py     # Модуль 12: Feedback Loop
├── versioning.py        # Модуль 13: Versioning
├── synergy.py           # Модуль 14: Cross-department Synergy
├── goals.py             # Модуль 15: Long-term Goals
├── intelligence.py      # Модуль 16: External Intelligence
├── testing.py           # Модуль 17: Automated Testing
├── rollback.py          # Модуль 18: Rollback
├── knowledge_base.py    # Модуль 19: Knowledge Base
├── communication.py     # Модуль 20: Communication Adapter
├── resources.py         # Модуль 21: Resource Monitor
├── self_evolution.py    # Модуль 22: Self-Evolution
├── executor.py          # ProposalExecutor
├── conversation_analyzer.py  # Полный анализ переписки
├── semantic_parser.py   # LLM-анализ намерений
├── error_analyzer.py    # Анализатор ошибок
├── growth_loop.py       # Growth Loop
├── brief.py             # Crystal Brief
```

## 6 фаз цикла

| Фаза | Файлы | Описание |
|------|-------|---------|
| 1. Наблюдение | `session_reader`, `pattern_detector` | Чтение сессий, поиск паттернов |
| 2. Анализ | `need_analyzer`, `priority_engine` | Формулировка потребностей, приоритизация |
| 3. Контекст | `memory_integration`, `semantic_parser` | USER.md, MEMORY.md, LLM-анализ |
| 4. Действия | `dev_proposer`, `synergy`, `risk_assessment`, `testing`, `executor`, `feedback_loop` | Генерация proposals, проверка, исполнение |
| 5. Мониторинг | `staleness`, `alerts`, `resources` | Проверка актуальности, уведомления, ресурсы |
| 6. Эволюция | `self_evolution`, `goals`, `intelligence`, `communication` | Самоулучшение, цели, внешние источники |

## 8 отделов

- `ai-core` (вес 1.2) — ядро AI
- `devops` (вес 1.1) — инфраструктура
- `crystal` (вес 1.0) — самосознание
- `telegram-bots` (вес 1.0) — Telegram
- `websites` (вес 0.9) — веб-проекты
- `youtube` (вес 0.8) — YouTube
- `user-needs` (вес 0.7) — потребности пользователя
- `testing` (вес 0.6) — тестирование

## Детальный план по Crystal задачам

Когда нужно выполнить задачу из backlog'а связанную с Crystal:

1. Проверить AGENTS.md для понимания текущей архитектуры
2. Определить какой модуль/фазу трогаешь
3. Внести изменения
4. Запустить `python scripts/crystal/core.py --full-cycle` и проверить что не сломалось
5. Обновить AGENTS.md если менял структуру, модули, или контракты
6. Запустить `python scripts/crystal/versioning.py --bump` если значимые изменения

## Pitfalls

- **AGENTS.md живёт в `scripts/crystal/`, не в корне проекта** — не потеряй его
- **После изменений AGENTS.md** — обнови секцию "Last touched" вверху файла
- **Модули 5-6 (Energy, Dependency Map)** — dataclass'ы в models.py, отдельных .py файлов нет
- **crystal/core.py** — не импортирует напрямую модули crystal.* (использует динамический импорт)
- **executor.py** — может создавать/патчить skills через skill_manage API

## Связанные навыки

- `self-improvement` — общие протоколы самоулучшения
- `skill-evolution` — автоэволюция skills из Knowledge Cube
