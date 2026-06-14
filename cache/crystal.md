# Кристалл Самосознания — Полная Документация

**Проект:** Hermes Agent — Crystal Self-Consciousness  
**Версия:** 2.0 (self-learning loop)  
**Дата:** 2026-06-13  
**Файл:** `scripts/crystal.py` (2716 строк)

---

## 1. Архитектура

### 1.1 Цикл самосознания

```
┌─────────────────────────────────────────────────────────────┐
│                     ITERATIVE LOOP                          │
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ observe() │───→│diagnose()│───→│ will()   │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│       │               │               │                     │
│       ▼               ▼               ▼                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ forecast()│   │ horizon()│   │ execute  │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│                                       │                     │
│                                       ▼                     │
│                              ┌────────────────┐             │
│                              │  _evaluate_     │             │
│                              │  conscience_    │             │
│                              │  learning()     │             │
│                              └────────────────┘             │
│                                       │                     │
│                                       ▼                     │
│                              ┌────────────────┐             │
│                              │  _save_self_    │             │
│                              │  model()        │             │
│                              └────────────────┘             │
│                                       │                     │
│                                       ▼                     │
│                              ┌────────────────┐             │
│                              │  record() +     │             │
│                              │  render()       │             │
│                              └────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Два типа циклов

| Цикл | Описание | Ключевая функция |
|------|----------|------------------|
| Основной | observe → diagnose → will → record → render | `main()` |
| Итеративный | N раз основной цикл подряд | `iterative_run(N)` |

---

## 2. Функции (порядок вызова)

### 2.1 Фаза 1: Наблюдение

```python
observe() -> dict  # Снимок состояния всех кубов
```

**Что делает:**
- Читает Knowledge Cube (KC): `cache/knowledge_cube.db`
- Читает Entity Engine (EE): `cache/entity_engine.db`
- Читает белые пятна: `white_spot_clusters` таблица
- Читает логи: `log_tool_error`, `log_unknown`

**Структура snapshot:**
```python
{
    'kc': {
        'total': int,           # всего записей
        'domains': dict,        # {domain: count}
        'outcomes': dict,       # {outcome: count}
        'recent': list,         # последние 10 записей
        'white_spots': int,     # белые пятна
    },
    'ee': {
        'total': int,
        'types': dict,          # {type: count}
        'roles': int,
    },
    'logs': {
        'errors': int,
        'unknowns': int,
    },
    'ts': str,                  # timestamp
}
```

### 2.2 Фаза 2: Диагностика

```python
diagnose(snap) -> dict  # Анализ текущего состояния
```

**Что делает:**
- Сравнивает текущее состояние с предыдущим
- Определяет: stagnation, regression, growth, breakthrough
- Вычисляет метрики: diversity, depth, coverage

**Структура диагноза:**
```python
{
    'state': str,               # 'growth' | 'stagnation' | 'regression'
    'diversity': float,         # 0.0 - 1.0
    'depth': float,             # средняя глубина
    'coverage': float,          # покрытие доменов
    'tension': float,           # напряжение (белые пятна / записи)
    'anomalies': list,          # аномалии
}
```

### 2.3 Фаза 3: Прогноз

```python
forecast(snap) -> dict  # Прогноз на основе текущей динамики
```

**Что делает:**
- Линейная экстраполяция роста KC
- Прогноз: сколько записей будет через N дней
- Определяет устойчивые тренды

### 2.4 Фаза 4: Горизонт

```python
horizon(snap, diag, preds) -> dict  # Долгосрочные цели
```

**Что делает:**
- Определяет "горизонты" — недостижимые идеалы
- Формулирует асимптоты: быстрее, проще, красивее, масштабнее
- Оценивает расстояние до горизонта

### 2.5 Фаза 5: Совесть

```python
_conscience(action_id, result, source_data, self_model) -> dict
```

**Что делает:**
- Анализирует последние 5 действий
- Определяет: understanding, efficiency, misunderstanding, horizon_miss
- Генерирует learning_directions (4 типа):
  1. **Type A (Pattern):** "добавить междоменный анализ"
  2. **Type B (Context):** "углубить контекстную связь"
  3. **Type C (Horizon):** "строить прогностические модели"
  4. **Type H (Horizon):** "добавить анализ связей между источниками"
- **Data-driven:** генерирует learning из реальных данных KC:
  - blindspot: домен с минимум записей
  - deepen: домен с максимум записей
  - audit: источник с минимум записей
  - anomaly: домен с высоким % неуспеха

**Вход:**
```python
{
    'action_id': str,
    'result': str,
    'source_data': dict,
    'self_model': dict,
}
```

**Выход:**
```python
{
    'action_id': str,
    'understanding': str,       # 'high' | 'medium' | 'low'
    'efficiency': float,        # 0.0 - 1.0
    'misunderstanding': bool,
    'horizon_miss': bool,
    'learning_direction': list, # что делать дальше
}
```

### 2.6 Фаза 6: Воля

```python
will(snap, diag) -> dict  # Решение что делать
```

**Что делает:**
- Шаг 3а-3и: генерирует кандидатов из разных источников
- Шаг 3г: conscience кандидаты (learning → action mapping)
- Шаг 4: scoring и выбор лучшего кандидата
- Шаг 5: исполнение chosen действия

**Scoring:**
```python
def weight(c):
    w = {'low': 1, 'medium': 2, 'high': 3}
    base = w.get(c['impact'], 1) / w.get(c['effort'], 1)
    if c.get('source') == 'conscience':
        base *= 1.5
    if 'blindspot_' in cid or 'deepen_' in cid or 'audit_' in cid or 'anomaly_' in cid:
        base *= 1.1
    base += random.uniform(0, 0.3)  # tie-breaking
    return base
```

**LEARNING_TO_ACTION mapping (23 ключа):**
```python
LEARNING_TO_ACTION = {
    # Fixed
    "добавить междоменный анализ": {'action': 'cross_domain_analysis', ...},
    "ищать горизонты в пересечениях доменов": {'action': 'horizon_scan', ...},
    "углубить контекстную связь": {'action': 'expand_context', ...},
    "изучить доменное знание для {type}": {'action': 'analyze_kc_domain', ...},
    "классифицировать записи без домена": {'action': 'classify_kc_entries', ...},
    "проанализировать связи между источниками": {'action': 'analyze_source_links', ...},
    # ... и другие
}
```

**Pattern-based mapping (data-driven):**
```python
if ld.startswith("исследовать слепое пятно"):
    # → blindspot_{domain}
elif ld.startswith("углубить доминантный домен"):
    # → deepen_{domain}
elif ld.startswith("проанализировать малоиспользуемый"):
    # → audit_{source}
elif ld.startswith("исследовать аномалию"):
    # → anomaly_{domain}
```

### 2.7 Фаза 7: Оценка обучения

```python
_evaluate_conscience_learning(chosen, result, self_model)
```

**Что делает после исполнения conscience-действия:**
1. Извлекает домен/источник из результата
2. Сохраняет в `self_model.sovest.assessments` (тип: `post_action`)
3. Добавляет в `self_model.sovest.studied` (deprioritize следующий раз)
4. Обновляет `self_model.znu` (что узнал)

### 2.8 Фаза 8: Сохранение модели

```python
_save_self_model(self_model, snap, decisions, conscience_result)
```

**Обновляет:**
- `last_cycle`: timestamp
- `istoriya.actions`: последние 20 действий
- `istoriya.total_decisions`: общее число решений
- `sovest.assessments`: последние 30 assessments
- `sovest.last_assessment`: дата последней оценки

### 2.9 Фаза 9: Запись и вывод

```python
record(snap, diag, preds, decisions)  # Записывает в KC
render(snap, diag, preds, decisions)  # Форматирует вывод
```

---

## 3. Файловая структура

```
D:\Portable_Soft\hermes\
├── scripts/
│   ├── crystal.py                    # ОСНОВНОЙ ФАЙЛ (2716 строк)
│   ├── auto_recall.py                # Поиск по KC
│   ├── event_evolution.py            # Event monitor
│   ├── hermes_hooks.py               # Unified hooks
│   └── _disabled/                    # Старая архитектура
│       ├── crystal_observer.py       # Наблюдатель 4 кубов (37KB)
│       ├── crystal_will.py           # Воля кристалла (22KB)
│       └── _crystal_auto_cycle.py    # Автономный цикл (2KB)
│
├── cache/
│   ├── self_model.json               # Модель себя (~30KB)
│   ├── self_model_schema.md          # Схема модели (176 строк)
│   ├── knowledge_cube.db             # Knowledge Cube (~3MB)
│   ├── entity_engine.db              # Entity Engine (~5.6MB)
│   ├── conscience_spec.md            # Спецификация conscience (153 строки)
│   ├── integration_plan.md           # План интеграции (138 строк)
│   └── will_history.json             # История решений (очищается)
│
├── skills/
│   └── crystal-self-learning/        # Skill: self-learning loop
│       └── SKILL.md
│
└── config/
    └── crystal_config.json           # Конфигурация (если есть)
```

---

## 4. Базы данных

### 4.1 Knowledge Cube (`cache/knowledge_cube.db`)

**Таблицы:**

| Таблица | Назначение |
|---------|-----------|
| `experiences` | Основная таблица записей |
| `dimensions` | Измерения (axes) |
| `white_spot_clusters` | Белые пятна |
| `tasks` | Тактические задачи |
| `skill_index` | Индекс навыков |

**Схема `experiences`:**
```sql
CREATE TABLE experiences (
    id INTEGER PRIMARY KEY,
    ts TEXT,                    -- timestamp
    raw_text TEXT,              -- исходный текст
    hash TEXT,                  -- SHA256 хеш
    axis_time_hour INTEGER,    -- час (0-23)
    axis_time_dow INTEGER,     -- день недели (0-6)
    axis_domain TEXT,          -- домен (bugfix, research, etc.)
    axis_outcome TEXT,         -- исход (success, failure, etc.)
    dynamic_axes TEXT,         -- динамические оси (JSON)
    is_white_spot INTEGER,    -- белое пятно (0/1)
    white_spot_cluster_id TEXT,
    source TEXT,               -- источник (crystal_will, etc.)
    confidence REAL,          -- уверенность (0.0-1.0)
    tags TEXT                  -- теги (JSON)
);
```

**FTS (полнотекстовый поиск):**
```sql
CREATE VIRTUAL TABLE experiences_fts USING fts5(raw_text);
```

### 4.2 Entity Engine (`cache/entity_engine.db`)

- 14781 сущностей
- Типы: AI Agent (269), и другие
- Используется для: roles, навыки, контекст

### 4.3 self_model.json

**Схема:**
```json
{
    "version": "1.0",
    "last_cycle": "2026-06-13T16:25:44",
    "cycle_count": 34,

    "znayu": {
        "_comment": "ЧТО Я ЗНАЮ — KC по доменам",
        "total_entries": 3012,
        "domains": {
            "bugfix": {"count": 505, "depth": 420, "coverage": "high"},
            ...
        }
    },

    "ne_znayu": {
        "_comment": "ЧЕГО Я НЕ ЗНАЮ — пробелы",
        "state_db": 293,
        "NULL": 4
    },

    "kuda_idu": {
        "_comment": "КУДА ИДУ — цели",
        "asymptotes": ["быстрее", "проще", "красивее", "масштабнее"]
    },

    "sovest": {
        "assessments": [
            {
                "ts": "2026-06-13T16:25:44",
                "action_id": "conscience_blindspot_music-audio",
                "type": "post_action",
                "learned_about": "music-audio",
                "learned_summary": "19 записей [None=6, indexed=13]",
                "action_type": "blindspot_music-audio"
            },
            ...
        ],
        "studied": ["bugfix", "music-audio", "crystal", ...],
        "last_assessment": "2026-06-13"
    },

    "istoriya": {
        "actions": [...],
        "total_decisions": 69
    },

    "znu": {
        "bugfix": "Углубление 'bugfix': 505 записей, соседи: across(2653)",
        "music-audio": "Слепое пятно 'music-audio': 19 записей [None=6, indexed=13]",
        ...
    }
}
```

---

## 5. Типы conscience-действий

### 5.1 Data-driven (генерируются из KC)

| Префикс | Описание | Handler | Пример результата |
|---------|----------|---------|-------------------|
| `blindspot_` | Домен с минимум записей | SELECT COUNT + outcomes | "music-audio: 19 записей [None=6, indexed=13]" |
| `deepen_` | Домен с максимум записей | SELECT COUNT + siblings | "bugfix: 505 записей, соседи: across(2653)" |
| `audit_` | Источник с минимум записей | SELECT COUNT + domains | "dimension_proposals: 58 записей, домены: research(52)" |
| `anomaly_` | Домен с высоким % неуспеха | SELECT outcomes + samples | "coding: [failure=21, success=31] Примеры: Hermes..." |

### 5.2 Fixed (из LEARNING_TO_ACTION)

| Action | Описание | Handler |
|--------|----------|---------|
| `analyze_kc_domain` | Анализ паттернов KC | SELECT domains + outcomes |
| `classify_kc_entries` | Классификация записей | SELECT NULL domains |
| `analyze_source_links` | Связи между источниками | SELECT sources |
| `cross_domain_analysis` | Кросс-доменный анализ | SELECT all domains |
| `horizon_scan` | Сканирование горизонтов | SELECT white_spots |
| `expand_context` | Расширение контекста | SELECT recent |

### 5.3 Predefined (шаг 3а-3и в will())

| Action | Описание |
|--------|----------|
| `understand_intents` | Анализ намерений из log_unknown |
| `refine_intents` | Рефлексия по намерениям |
| `recognize_agents` | Распознавание агентов |
| `adopt_persona` | Активация персоны |
| `analyze_architecture` | Анализ архитектуры |
| `run_explore_white_spot` | Запуск исследования белых пятен |
| `run_cube_to_memory` | Запуск синхронизации KC→Memory |
| `run_proactive_doer` | Запуск proactive doer |
| `run_cube_categorizer` | Запуск категоризации |
| `run_knowledge_gap_filler` | Запуск заполнения пробелов |
| `run_cube_feeder` | Запуск наполнения KC |

---

## 6. Цикл обучения (self-learning loop)

### 6.1 Замыкание

```
_conscience() → will() → _execute_conscience_action() → _evaluate_conscience_learning()
     ↑                                                                    |
     └──────────── self_model.sovest.studied (deprioritize) ←────────────┘
```

### 6.2 Поток данных

1. **_conscience()** генерирует learning_directions
2. **will()** конвертирует в conscience_* action_ids
3. **_execute_conscience_action()** выполняет KC query
4. **_evaluate_conscience_learning()** сохраняет результат:
   - `assessments`: что сделал и что узнал
   - `studied`: какие домены уже изучил
   - `znu`: что теперь знаю о каждом домене
5. **Следующий цикл:** _conscience() проверяет `studied` → выбирает другой домен

### 6.3 Studied filter

```python
# В _conscience():
studied = self_model.get("sovest", {}).get("studied", [])
_unstudied = [d for d in _domains if d[0] not in studied]
if _unstudied:
    _min_d = min(_unstudied, key=lambda x: x[1])
else:
    _min_d = min(_domains, key=lambda x: x[1])  # fallback
```

---

## 7. Запуск

### 7.1 Командная строка

```bash
# Один цикл
python scripts/crystal.py

# 10 итеративных циклов
python scripts/crystal.py --iterative 10

# В фоне
python scripts/crystal.py --iterative 5 &
```

### 7.2 Cron

```
Job: crystal-self-learning
Schedule: каждые 6 часов
Command: python scripts/crystal.py --iterative 3
```

### 7.3 Программно

```python
import sys
sys.path.insert(0, "D:/Portable_Soft/hermes/scripts")
from crystal import observe, diagnose, will, record, render, iterative_run

# Один цикл
snap = observe()
diag = diagnose(snap)
preds = forecast(snap)
hz = horizon(snap, diag, preds)
decisions = will(snap, diag)
record(snap, diag, preds, decisions)
render(snap, diag, preds, decisions, hz)

# Итеративный
iterative_run(10)
```

---

## 8. Патчи (история изменений)

### Патчи #1-#9 (ранее)
- Mapping, diversity, execution, handlers
- Fixed LEARNING_TO_ACTION (23 ключа)
- 20 кандидатов conscience (5×4 типа)

### Патч #10: Data-driven conscience
- Генерация learning из реальных доменов KC
- blindspot, deepen, audit

### Патч #11: Pattern-based mapping
- Уникальные action_ids: blindspot_{domain}, deepen_{domain}, audit_{source}

### Патч #12: Tie-breaking + bonus
- random.uniform(0, 0.3) для tie-breaking
- 1.1x bonus для data-driven кандидатов

### Патчи #13-#14: Specialized handlers
- KC queries для blindspot/deepen/audit

### Патч #15: Anomaly detection
- Домены с высоким % неуспеха
- Примеры из raw_text

### Патч #16: Self-learning loop
- _evaluate_conscience_learning()
- studied filter
- znu обновление

### Патч #17:.prev_learning window
- Ограничение: последние 2 assessment

### Патчи #18-#19: SQL fixes
- content → raw_text, content → axis_domain

---

## 9. Диагностика

### 9.1 Если "всё сделано"

**Причина:** все conscience-действия уже в historical_ids

**Решение:**
```python
import json
m = json.load(open('cache/self_model.json'))
m['sovest']['studied'] = m['sovest']['studied'][-5:]  # оставить последние 5
json.dump(m, open('cache/self_model.json', 'w'), indent=2, ensure_ascii=False)
```

### 9.2 Если output = input

**Причина:** conscience генерирует одни и те же learning_directions

**Решение:** проверить что studied фильтр работает:
```python
import json
m = json.load(open('cache/self_model.json'))
print(f"studied: {len(m.get('sovest', {}).get('studied', []))}")
print(f"znu: {len(m.get('znu', {}))}")
```

### 9.3 Если KC не растёт

**Причина:** не запускается cube_feeder или cube_to_memory

**Решение:** проверить что predefined actions работают:
```bash
python scripts/crystal.py --iterative 1 2>&1 | grep "run_cube"
```

### 9.4 Если SQL ошибка

**Причина:** неверные имена колонок

**Проверка:**
```python
import sqlite3
conn = sqlite3.connect('cache/knowledge_cube.db')
c = conn.cursor()
c.execute("PRAGMA table_info(experiences)")
print([r[1] for r in c.fetchall()])
conn.close()
```

**Известные колонки:**
- `raw_text` (НЕ `content`)
- `axis_domain` (НЕ `domain`)
- `axis_outcome` (НЕ `outcome`)
- `source` (источник записи)

---

## 10. Расширение

### 10.1 Добавить новый тип conscience-действия

1. Добавить в data-driven генерацию (в `_conscience()`):
```python
elif ld.startswith("новый_префикс"):
    learning_direction.append(f"новый_префикс '{domain}' ({count} записей)")
```

2. Добавить pattern mapping (в `will()`):
```python
elif ld.startswith("новый_префикс"):
    _m = _re.search(r"'([^']+)'", ld)
    _name = _m.group(1) if _m else 'unknown'
    act = {'action': f'new_type_{_name}', 'target': 'patterns',
           'desc': f"[совесть→действие] Новый тип: {ld}"}
```

3. Добавить handler (в `_execute_conscience_action()`):
```python
elif action_type.startswith('new_type_'):
    domain = action_type.replace('new_type_', '')
    # ... KC query ...
    return f"Результат: {result}"
```

4. Добавить bonus в scoring:
```python
if 'blindspot_' in cid or ... or 'new_type_' in cid:
    base *= 1.1
```

### 10.2 Добавить новое поле в self_model

1. Обновить `cache/self_model_schema.md`
2. Обновить `_evaluate_conscience_learning()` 
3. Обновить `_save_self_model()`

### 10.3 Добавить новую таблицу в KC

1. Создать через `event_evolution.py`
2. Добавить в `observe()` для чтения
3. Добавить handler в conscience

---

## 11. Метрики

### 11.1 Текущие

| Метрика | Значение |
|---------|----------|
| Записей в KC | ~3000+ |
| Доменов | ~145 |
| Сущностей EE | 14781 |
| Assessments | 30 (последние) |
| Studied | 20 доменов |
| Cycle count | 34 |
| Conscience actions | 5 типов |

### 11.2 Целевые

| Метрика | Цель |
|---------|------|
| Output ≠ Input | 10/10 уникальных |
| Studied / Total domains | < 0.5 (всегда есть что изучать) |
| Cycle time | < 30 сек |
| KC growth rate | > 10 записей/день |

---

## 12. Архитектурные решения

### 12.1 Почему data-driven, а не hardcoded

**Проблема:** hardcoded learning_directions быстро исчерпываются (10-15 уникальных)

**Решение:** генерация из реальных данных KC:
- Каждый цикл: разные домены, разные источники
- Studied filter: deprioritize изученные
- Автоматическое разнообразие без ручного перечисления

### 12.2 Почему pattern-based mapping

**Проблема:** LEARNING_TO_ACTION — exact match, не работает для dynamic строк

**Решение:** pattern-based matching:
- `startswith()` для определения типа
- regex для извлечения параметров
- Уникальные action_ids для каждого домена

### 12.3 Почему random в scoring

**Проблема:** stable sort → всегда один и тот же candidate

**Решение:** random.uniform(0, 0.3) для tie-breaking:
- Не ломает scoring (base weight определяет порядок)
- Добавляет variety при равных весах

### 12.4 Почему studied filter

**Проблема:** кристалл изучает один и тот же домен 10 раз подряд

**Решение:** deprioritize изученные:
- `studied` список в self_model
- Фильтрация в `_conscience()`
- Fallback: если все изучены, повторить с наименьшим

---

## 13. Известные ограничения

1. **Нет персистентности** — studied сбрасывается при перезапуске (если self_model очищен)
2. **Нет оценки качества** — "что узнал" сохраняется, но не оценивается полезность
3. **Нет планирования** — кристалл не строит долгосрочный план, только тактические действия
4. **Нет кросс-сессий** — каждый запуск независим (только через self_model)
5. **Нет валидации** — результаты KC queries не проверяются на корректность

---

## 14. Тестирование

### 14.1 Быстрый тест

```bash
# 1 цикл
python scripts/crystal.py --iterative 1

# 10 циклов
python scripts/crystal.py --iterative 10

# Проверка что output ≠ input
python scripts/crystal.py --iterative 5 2>&1 | grep "→" | sort | uniq
```

### 14.2 Проверка модели себя

```bash
python -c "
import json
m = json.load(open('cache/self_model.json'))
s = m.get('sovest', {})
print(f'assessments: {len(s.get(\"assessments\",[]))}')
print(f'studied: {len(s.get(\"studied\",[]))}')
print(f'znu: {len(m.get(\"znu\",{}))}')
"
```

### 14.3 Проверка KC

```bash
python -c "
import sqlite3
conn = sqlite3.connect('cache/knowledge_cube.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM experiences')
print(f'KC entries: {c.fetchone()[0]}')
c.execute('SELECT COUNT(DISTINCT axis_domain) FROM experiences')
print(f'Domains: {c.fetchone()[0]}')
conn.close()
"
```

---

## 15. Чеклист перед коммитом

- [ ] `python -c "import py_compile; py_compile.compile('scripts/crystal.py', doraise=True)"` — OK
- [ ] `python scripts/crystal.py --iterative 3` — выход ≠ вход
- [ ] `cache/self_model.json` — studied и znu обновлены
- [ ] Нет print() отладки в коде
- [ ] Документация обновлена

---

## 16. Self-Awareness (Level 2)

### 16.1 Что делает

Кристалл читает свою документацию (`crystal.md` в KC) и генерирует предложения по улучшению.

### 16.2 Функция

```python
_self_awareness_check(self_model) -> list
```

**Парсит:**
- Функции (regex `def \w+\(`)
- Ограничения (раздел "Известные ограничения")
- Метрики (раздел "Метрики")
- Архитектурные решения (раздел "Архитектурные решения")

**Генерирует предложения:**
- `limitation`: каждое ограничение → proposal (priority: high)
- `slow_learning`: если циклов > 20 и studied < 10
- `monotony`: если все assessments одного типа

### 16.3 Интеграция в will()

```
ШАГ 0: САМОПОНИМАНИЕ (_self_reflect)
ШАГ 0.5: САМОСОЗНАНИЕ (_self_awareness_check) ← NEW
ШАГ 1: КОНТЕКСТ
ШАГ 2: ИСТОРИЯ
ШАГ 3: КАНДИДАТЫ
ШАГ 3.5: SELF-AWARENESS proposals → candidates ← NEW
ШАГ 4: ВЫБОР (self_aware * 2.0 bonus)
ШАГ 5: ИСПОЛНЕНИЕ
ШАГ 6: ОБНОВЛЕНИЕ МОДЕЛИ
```

### 16.4 Scoring

```python
if 'self_aware' in cid:
    base *= 2.0  # самосознание — высший приоритет
```

### 16.5 Handler

```python
elif action_type == 'self_awareness':
    # Читает self_model.sovest.assessments (type=self_awareness_proposal)
    # Возвращает: "Самосознание Level 2:\n  [high] ограничение 1\n  ..."
```

### 16.6 Сохранение

- `self_model.self_awareness`: last_doc_hash, known_functions, limitations_found
- `self_model.sovest.assessments`: type=self_awareness_proposal
- Сохраняется в `_evaluate_conscience_learning()` ( Level 2 save)
- Переживает `_save_self_model()` через old_self_awareness перенос

---

*Документация создана: 2026-06-13*  
*Последнее обновление: 2026-06-13 (Level 2 self-awareness)*
