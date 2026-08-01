---
name: crystal-v3-implementation
description: "Auto-generated from crystal-v3-implementation.md"
trigger: "When user asks about crystal-v3-implementation concepts"
usage: crystal-v3-implementation
Revisit: 2026-07-31
---

# Crystal v3 — План реализации

## Цель
Персональный Development Advisor: наблюдает пользователя → паттерны → потребности → развитие системы → feedback.

## Архитектура
22 модуля, 8 отделов. Полная дока: `skills/crystal-self-learning/AGENTS.md`

## Структура файлов

```
scripts/crystal/
  __init__.py           — экспорт
  config.py             — конфигурация, пути, настройки
  models.py             — dataclasses для всех сущностей
  core.py               — CrystalEngine — главный цикл
  
  # Наблюдение
  session_reader.py     — модуль 1
  pattern_detector.py   — модуль 2
  
  # Анализ
  need_analyzer.py      — модуль 3
  priority_engine.py    — модуль 4
  risk_assessment.py    — модуль 7
  
  # Контекст
  memory_integration.py — модуль 11
  knowledge_base.py     — модуль 19
  
  # Действия
  dev_proposer.py       — модуль 8
  synergy.py            — модуль 14
  testing.py            — модуль 17
  
  # Обратная связь
  feedback_loop.py      — модуль 12
  versioning.py         — модуль 13
  rollback.py           — модуль 18
  
  # Мониторинг
  staleness.py          — модуль 9
  alerts.py             — модуль 10
  resources.py          — модуль 21
  
  # Эволюция
  self_evolution.py     — модуль 22
  
  # Связь
  communication.py      — модуль 20
  
  # Внешний мир + цели
  intelligence.py       — модуль 16
  goals.py              — модуль 15
  energy.py             — модуль 5
  dependencies.py       — модуль 6
```

---

## Фаза 1: Фундамент

### Что делаем
- `models.py` — все dataclasses (Signal, Pattern, Need, Proposal, Assessment, и т.д.)
- `config.py` — пути, настройки, дефолты
- `core.py` — CrystalEngine — загрузка модулей, главный цикл

### Модели данных
```python
@dataclass
class Signal:
    type: str          # request, correction, frustration, workflow, unmet
    content: str       # текст
    source: str        # session_id
    timestamp: str     # ISO
    severity: float    # 0.0 - 1.0

@dataclass
class Pattern:
    type: str          # correction_loop, missing_knowledge, etc.
    frequency: int
    severity: float
    signals: list[str] # signal IDs
    description: str

@dataclass
class Need:
    pattern_type: str
    description: str
    priority: float    # 0.0 - 1.0
    impact: str        # low, medium, high, critical
    department: str    # youtube, social-media, etc.

@dataclass
class Proposal:
    action: str        # create_skill, patch_skill, etc.
    description: str
    risk_level: str    # safe, moderate, risky, critical
    priority: float
    estimated_impact: str
    department: str
    auto: bool         # можно ли автоматически

@dataclass
class Assessment:
    metric: str
    before: float
    after: float
    delta: float
    success: bool
```

---

## Фаза 2: Наблюдение

### Session Reader
- Читает JSONL сессии из `~/.hermes/sessions/`
- Извлекает сигналы: запросы, поправки, фрустрацию, паттерны
- Записывает в `cache/crystal/signals.json`

### Pattern Detector
- Берёт signals, находит повторения
- Типы: correction_loop, missing_knowledge, frustration_spike, workflow_success, unmet_need
- Записывает в `cache/crystal/patterns.json`

---

## Фаза 3: Анализ

### Need Analyzer
- Из patterns формулирует needs
- Приоритизирует по frequency × severity
- Записывает в `cache/crystal/needs.json`

### Priority Engine
- Берёт needs + proposals, сортирует по urgency × impact / effort
- Учитывает dependencies
- Записывает в `cache/crystal/priority.json`

### Risk Assessment
- Для каждого proposal определяет risk_level
- safe → автоматически, moderate →提议, risky → подтверждение, critical → стоп
- Записывает в proposals.json (risk_level поле)

---

## Фаза 4: Контекст

### Memory Integration
- Читает USER.md + MEMORY.md
- Понимает предпочтения, историю, окружение
- Пишет новые предпочтения

### Knowledge Base
- Хранит решённые проблемы, рабочие подходы, провалы
- При proposal проверяет: "это уже решалось?"
- Записывает в `cache/crystal/knowledge_base.json`

---

## Фаза 5: Действия

### Development Proposer
- Из needs + priority + risk генерирует proposals
- Типы: create_skill, patch_skill, update_dox, update_memory, new_tool, architecture_change
- Записывает в `cache/crystal/proposals.json`

### Cross-department Synergy
- Находит связи между отделами
- Content Pipeline: YouTube → social-media → monetization
- Tech Stack: ai-core → devops → websites
- Записывает в `cache/crystal/synergies.json`

### Automated Testing
- Тест SKILL.md, Python кода, DOX, config
- Уровни: quick (syntax), standard (import), full (integration)
- Результат: pass/fail + details

---

## Фаза 6: Обратная связь

### Feedback Loop
- Сравнивает метрики до/после
- correction_count, frustration_signals, unmet_needs, workflow_success_rate
- Записывает в `cache/crystal/feedback.json`

### Versioning
- Каждое изменение → changelog entry
- Что, когда, почему, эффект
- Записывает в `cache/crystal/changelog.json`

### Rollback
- Snapshot перед изменением
- Автоматический откат при негативном feedback
- Ручной откат по версии
- Директория: `cache/crystal/snapshots/`

---

## Фаза 7: Мониторинг

### Staleness Detector
- Проверяет скиллы, зависимости, конфиг, доки, инструменты, провайдеры
- Автоматически или с предложением
- Записывает в `cache/crystal/staleness.json`

### Proactive Alerts
- API изменился, dependencies устарели, CVE, пользователь долго не работал
- Доставка: следующая сессия / crystal_tasks.json / memory
- Записывает в `cache/crystal/alerts.json`

### Resource Monitor
- API-лимиты, бюджет, время, память
- Если бюджет на исходе → дешёвая модель
- Записывает в `cache/crystal/resources.json`

---

## Фаза 8: Эволюция

### Self-Evolution
- Отслеживает: модули с низким feedback, узкие места, устаревшие подходы
- Автоматически оптимизирует, предлагает новые модули
- Записывает в `cache/crystal/evolution.json`

### Long-term Goals
- Стратегические цели пользователя
- Достигнутые вехи, блокирующие факторы
- Записывает в `cache/crystal/goals.json`

### External Intelligence
- GitHub trending, PyPI, AI news, security feeds
- Новые инструменты, фреймворки, API
- Записывает в `cache/crystal/intelligence.json`

### Communication Adapter
- Язык, длина, техничность, тон, формат
- Адаптация по feedback
- Записывает в `cache/crystal/communication.json`

---

## Фаза 9: Интеграция

### CLI
- `python scripts/crystal.py` — полный цикл
- `--analyze-sessions` — анализ сессий
- `--check-staleness` — проверка актуальности
- `--propose` — предложение
- `--feedback` — оценка
- `--department X` — конкретный отдел
- `--intelligence` — внешний мир
- `--goals` — цели
- `--synergies` — синергия
- `--changelog` — история
- `--rollback <version>` — откат
- `--test` — тест
- `--knowledge` — база знаний
- `--communication` — стиль
- `--resources` — ресурсы
- `--evolve` — самоэволюция

### DOX
- Обновить `scripts/AGENTS.md` — crystal/ directory
- Обновить `skills/crystal-self-learning/AGENTS.md` — file structure

### Тесты
- `tests/crystal/` — юнит-тесты для каждого модуля

---

## Порядок выполнения

| Фаза | Модули | Ожидаемый результат |
|------|--------|---------------------|
| 1 | config, models, core | Рабочий каркас, импортируется |
| 2 | session_reader, pattern_detector | Читает сессии, находит паттерны |
| 3 | need_analyzer, priority_engine, risk_assessment | Формулирует needs, приоритизирует |
| 4 | memory_integration, knowledge_base | Понимает контекст пользователя |
| 5 | dev_proposer, synergy, testing | Предлагает изменения, тестирует |
| 6 | feedback_loop, versioning, rollback | Оценивает, версионирует, откатывает |
| 7 | staleness, alerts, resources | Мониторит актуальность и ресурсы |
| 8 | self_evolution, goals, intelligence, communication | Эволюционирует, понимает цели |
| 9 | CLI, DOX, tests | Полностью рабочий инструмент |

---

## Старт

Начинаем с Фазы 1: models.py + config.py + core.py
