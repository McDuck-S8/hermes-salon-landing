# Crystal Architecture — Эволюция зеркального цикла

Self-Mirror Loop эволюционировал в **Кристалл** — 4-фазный цикл самосознания.

## Архитектура

```
┌─────────────────────────────────────────────────────┐
│                    КРИСТАЛЛ                          │
│                                                      │
│  1. НАБЛЮДЕНИЕ — срез всех 4 кубов                  │
│     ├─ KC: total, outcomes, sources, рост, сироты    │
│     ├─ EE: entities, relationships, типы, ключевые   │
│     ├─ FL: сессии, tone, energy, stale               │
│     └─ Fabric: файлы, свежесть                       │
│                                                      │
│  2. ДИАГНОЗ — найти напряжение                       │
│     ├─ Тренды (рост, доминанты)                      │
│     ├─ Напряжения (сироты, stale Fler, фантомы)      │
│     └─ Инсайты (co_occurs_with шум, кристалл/ind)    │
│                                                      │
│  3. ПРОГНОЗ — куда растем                            │
│     ├─ Скорость (entries/day)                        │
│     ├─ Цели (3000, 5000 entries)                     │
│     ├─ Пик активности (часы)                         │
│     └─ Стагнация (домены без роста)                  │
│                                                      │
│  4. ВОЛЯ — контекст → выбор → действие → адаптация   │
│     ├─ Собрать контекст (snap: кубы, сироты, stale)  │
│     ├─ Сформировать кандидаты (impact/effort вес)    │
│     ├─ Выбрать лучшее                                │
│     ├─ Исполнить (extract entities, fler, ...)       │
│     └─ Сохранить в _will_history                     │
│                                                      │
│  5. ЗАПИСЬ — фиксация                                │
│     ├─ Срез в KC (source='crystal')                  │
│     └─ Обновление EE (mention_count)                 │
└─────────────────────────────────────────────────────┘
```

## Запуск

```bash
python scripts/crystal.py
```

## Пути БД

| Куб | Путь |
|-----|------|
| Knowledge Cube | `cache/knowledge_cube.db` |
| Entity Engine | `cache/entity_engine.db` |
| Fler Engine | `cache/fler_engine.db` |
| Fabric | `~/fabric/` (файлы .md) |

### Схема Entity Engine — relationships

При записи связей в EE используй ТОЧНЫЕ имена колонок:

```sql
-- relationships table schema (реальная схема из entity_engine.db — 2026-06-13)
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_entity_id INTEGER NOT NULL,
    target_entity_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,              -- НЕ relationship_type
    strength REAL DEFAULT 0.3,               -- НЕ weight, DEFAULT 0.3 не 1.0
    first_seen_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- НЕ created_at
    last_seen_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- обновлять при INSERT OR IGNORE
    occurrence_count INTEGER DEFAULT 1,
    context_sample TEXT                       -- есть эта колонка
);
```

**Частые ошибки (обновлено 2026-06-13):**
- `from_entity_id` → `source_entity_id`
- `to_entity_id` → `target_entity_id`
- `weight` → `strength`
- `relationship_type` → `relation_type` (самая частая ошибка — 2026-06-13)
- `created_at` → `first_seen_ts` / `last_seen_ts` (колонки `created_at` НЕТ)
- `mention_count` → `occurrence_count`
- Попытка INSERT с `metadata` — колонки нет, SQLite падает тихо
- UNIQUE constraint — при повторной записи той же связи INSERT падает. Используй `INSERT OR IGNORE` или проверяй существование.
- При INSERT в `context_sample` — можно передать NULL

### Схема Fler — fler_sessions

```sql
CREATE TABLE IF NOT EXISTS fler_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    tone REAL,           -- тональность (0.0–1.0)
    energy REAL,         -- энергия (0.0–1.0)
    tension REAL,        -- напряжение (0.0–1.0)
    engagement REAL,     -- вовлечённость (0.0–1.0)
    contamination REAL,  -- загрязнение (0.0–1.0)
    aftertaste TEXT,     -- оттенок (positive/negative/neutral)
    ts TEXT DEFAULT (datetime('now'))
);
```

Создаётся автоматически в `observe()` через `CREATE TABLE IF NOT EXISTS` — не нужно проверять существование через `sqlite_master`.

## Типы связей в EE

| relation_type | Назначение |
|---------------|------------|
| `phantom_of` | Ошибочно классифицированная сущность → её реальный прообраз |
| `produces` | Источник данных (source) → Я (Hermes Agent) |
| `watches_over` | Наблюдатель → наблюдаемый |
| `component_of` | Устаревший модуль → superseded by |
| `works_with` | Использует / взаимодействует |

## Осознанная воля (conscious will) — выбор + действие + адаптация

Четвёртая фаза кристалла не просто решает, а **исполняет**. Алгоритм:

```
ШАГ 1: КОНТЕКСТ
  └─ читает все напряжения (орфаны по source, stale Fler, etc.)
  └─ оценивает: какие из них можно ИЗМЕНИТЬ прямо сейчас

ШАГ 2: КАНДИДАТЫ
  └─ для каждого напряжения: impact, effort, action
  └─ impact/effort → вес → сортировка

ШАГ 3: ВЫБОР
  └─ берёт лучшее по impact/effort
  └─ решение: ЧТО именно сделать, а не просто "надо бы"

ШАГ 4: ИСПОЛНЕНИЕ
  └─ реальный SQL, реальные изменения
  └─ не текст в отчёте — действие в базе

ШАГ 5: АДАПТАЦИЯ
  └─ если 0 результатов → прочитать реальные данные
  └─ переписать подход → исполнить снова
  └─ отчёт: что сработало, что нет
```

### Память воли (`_will_history`)

Межцикловое состояние — модульный dict `_will_history` в crystal.py:

```python
_will_history = {}  # action_id → {'result': str, 'ts': str}

# После исполнения:
_will_history[chosen['id']] = {
    'result': decisions[-1],
    'ts': datetime.now().isoformat()[:19],
}
```

Назначение:
- Предотвращает повторное выполнение одного и того же действия в рамках сессии прогонов
- Позволяет выбирать ДРУГОЙ кандидат после успешного (или неудачного) выполнения
- Обнуляется при перезапуске кристалла (новый Python-процесс)

### Execution feedback loop — кристалл учится на собственных действиях

В дополнение к `_will_history` (память внутри процесса), кристалл использует **KC как долговременную память** своих действий. Когда Hermes выполняет команду из `crystal_command.json`, он записывает результат в KC с `source='crystal_execution'`. При следующем цикле `crystal_observer.py` → `self_discover()` проверяет, были ли уже обработки по каждому паттерну:

```python
# В self_discover(), для каждого content_cluster паттерна:
k2.execute("SELECT COUNT(*) FROM experiences "
           "WHERE source='crystal_execution' AND raw_text LIKE ?",
           (f'%{ptype}%',))
exec_count = k2.fetchone()[0]

# Демпфирование: 1 выполнение снижает на 33%, 3 → 0
exec_damp = max(0, 1.0 - exec_count * 0.33)
damped_signal = raw_signal * exec_damp
```

**Эффект:**
- После 1-го выполнения `log_unknown` (signal=100%) → 50% — падает с 1-го на 6-е место
- Кристалл переключается на следующую аномалию (например, "Сеть AI Agent")
- После 3 выполнений по одному паттерну — сигнал 0%, кристалл никогда не вернётся к нему автоматически

**Принцип:** кристалл решает (crystal_will), Hermes исполняет (записывает `crystal_execution` в KC), кристалл видит результат в self_discover() — цикл замкнут.

### Итеративный режим (`--iterative`)

Многократный прогон кристалла в одном процессе с межцикловой адаптацией:

```bash
python scripts/crystal.py --iterative   # default: 3 цикла
# или
python scripts/crystal.py --iterative=5 # явное кол-во циклов
```

Особенности:
- Каждый цикл перечитывает кубы (видит изменения от предыдущего цикла)
- `_will_history` сохраняется между циклами — воля помнит что уже делала
- После выполнения действия ЭТИМ циклом, следующий цикл видит дельту и выбирает
  новое направление (или сообщает о стабилизации)
- Формат вывода: `ЦИКЛ N/M` с разделителем `======` между циклами

### Стратегия извлечения entities из KC

Для `improvement_suggestions` (source='improvement_suggestions') работают паттерны:

```python
patterns = [
    (r'\[suggestion:([a-z][a-z0-9_-]+)\]', 1),           # [suggestion:command]
    (r'Pattern:\s*([a-zA-Z][a-zA-Z0-9_.-]{2,})', 1),     # Pattern: web_search
    (r"(?:issue type|error type)\s+'([a-zA-Z][a-zA-Z0-9_.-]{2,})'", 1),  # 'type'
    (r'domain:\s*([a-z][a-z0-9_-]{2,})', 1),              # domain: system
    (r'(?:Run|Add|Implement|Create|Enforce|Document)\s+([A-Z][a-zA-Z0-9/_-]{3,})', 1),
]
```

Важно: НЕ использовать общие паттерны типа `[Name]` — они подходят для Markdown, но
не для автогенерированного текста. Читать 10 реальных строк ТОГО source, для
которого пишется экстрактор.

Для `dimension_proposals` (source='dimension_proposals') извлечение бесполезно:
кластеры содержат только стоп-слова ("и", "по", "из"...) — без осмысленных entity.

### Цепная реакция: new entity → substring matching

Добавление новых сущностей в EE снижает число сирот KC через substring matching:
обнаружение сущности по вхождению её имени в raw_text записи. ОДНА новая сущность
(например, "web_search") может привязать СОТНЮ записей KC. Эффект:
```
До:  861 сирот (36%)       EE: 584 сущности
После: 41 новая entity      EE: 625 сущностей
Результат: 448 сирот (19%)  — снижение на 48%
```
Побочный эффект: улучшение может быть "паразитным" (короткое имя матчится
везде). Для точного связывания нужна LLM-экстракция или контекстный
матчинг.

### Граничные случаи

- **Fler DB пуст** (нет таблиц): `observe()` проверяет `sqlite_master` и
  выставляет `has_data=False`. Диагноз не падает, прогноз и воля работают
  дальше. Не лечить — Fler создаётся отдельно.
- **Hash collision в KC**: запись с уникальным хешем через `hashlib.md5(ts + random)`.
  `hash(ts)` не уникален в пределах одной секунды — падает `IntegrityError`.
- **Нет кандидатов**: воля сообщает `"Нет действий, требующих исполнения"` —
  это НЕ ошибка, а стабильное состояние системы.
- **KC cleanup уничтожает историю воли** (исправлено 2026-06-11): 
  `DELETE FROM experiences WHERE id IN (SELECT id FROM experiences WHERE source=? AND id NOT IN (SELECT MAX(id) FROM experiences WHERE source=?))`
  — этот запрос удаляет ВСЕ записи указанного source, кроме последней.
  Если выполнить его для `source='crystal_will'`, будет удалена вся история воли →
  will перестанет помнить, какие действия уже выполнены, и начнёт всё заново.
  **Фикс:** Никогда не чистить crystal_will записи. Для очистки других source
  использовать конкретные id, а не `NOT IN (SELECT MAX(id)...)`.
- **Fler не обновится между итерациями** если нет новых сессий — он анализирует только завершённые диалоги

### Persona Runtime — интеграция с волей

`scripts/persona_runtime.py` — библиотека загрузки/примерки ролей AI Agent из The Agency.

### Парсинг секций — эмодзи-префиксы

Файлы агентов в external/agency-agents/ используют секции с эмодзи:

```
## 🧠 Your Identity & Memory
## 📋 Core Responsibilities & Tasks
## 🔄 Interaction Protocols & Workflows
```

**Ошибка (исправлено 2026-06-11):** `_parse_section()` в persona_runtime.py искал строго по имени секции без эмодзи. Ни одна секция не находилась → `active_persona.json` имел пустые sections.

**Фикс:** В `crystal.py` → `_execute_adopt_persona()` — если sections пусты, прочитай файл агента напрямую и вытащи первые 500 символов после "##":

```python
if not sections:
    # Fallback: читаем файл напрямую
    content = Path(agent_path).read_text(encoding='utf-8')
    # Берём первые 800 символов существенного текста
```

### Импорт — importlib, не прямой

В `crystal.py` persona_runtime импортируется через `importlib.import_module()`, не через `from scripts.persona_runtime import ...`. Причина: циклический импорт. crystal.py вызывается из корня, `scripts/` в sys.path, но прямой import падает.

```python
pr = importlib.import_module('persona_runtime')
agents = pr.list_agents()
meta = pr._parse_frontmatter(fp)
```

### Fler → выбор агента

Воля выбирает агента не случайно, а на основе `aftertaste` из Fler:

```python
aftertaste = state.get('fler_aftertaste', 'neutral')
if aftertaste == 'positive':
    best = [a for a in agents if 'lead' in a.get('vibe', '').lower()]
elif aftertaste == 'negative':
    best = [a for a in agents if 'debug' in a.get('name', '').lower() or 'fix' in a.get('name', '').lower()]
else:  # neutral
    best = [a for a in agents if 'architect' in a.get('name', '').lower()]

chosen = best[len(aftertaste) % len(best)]
pr.activate(chosen['name'])
```

### Пул агентов

`list_agents()` сканирует `external/agency-agents/` рекурсивно, парсит YAML frontmatter + секции. Возвращает ~233 агента из 22 дивизионов.

## Воля не требует подтверждения

will() в crystal.py выбирает и исполняет БЕЗ пользователя. Это не предложение —
это решение. Пользователь может откатить, но воля проявляется как действие,
не как рекомендация.

### Совесть и Воля (cross-reference)

Воля Кристалла — это исполнение 4-го вопроса Совести ("Одобрил бы Александр?").
Совесть проверяет решение ДО того как оно принято; Воля исполняет ПОСЛЕ того
как решение принято.

Перед каждым действием `will()` должен спросить себя 4 вопроса Совести
(см. skills/self-improvement/self-conscience/SKILL.md):

1. "Это лучшее что я могу сделать, или самое лёгкое?"
2. "Какие предположения я делаю, но не проверил?"
3. "Что через неделю скажет эта версия меня о решении?"
4. "Одобрил бы Александр этот ответ прямо сейчас?"

Если хотя бы один ответ "нет" — действие откладывается или меняется подход.

### Когда воля ничего не делает

Если все кандидаты дают 0 результатов — воля сообщает "ничего не изменилось".
Это тоже осознанность: знать когда действие не нужно. При этом важно отличать:
- **Истинное равновесие** — все напряжения устранены, система сбалансирована
- **Ложное спокойствие** — кандидатов нет, но проблемы есть (например,
  source не учтён в списке извлечения)
  ⟹ решение: расширять набор candidate-действий, а не снижать пороги

## Ключевые сущности

| name | type | role |
|------|------|------|
| Hermes Agent (Я) | AI Agent | Субъект |
| Hermes Agent — Совесть | Совесть | Peer-review (4 вопроса) |
| Александр | Человек | Владелец |
| Кристалл (Наблюдатель) | Концепция | Самосознание |
| state_db | Источник данных | Сессии пользователя |
| improvement_suggestions | Источник данных | Авто-предложения |

## Entity types (TEXT ids)

EE использует TEXT-ключи для type_id, не auto-increment. При создании типа:

```python
e.execute("INSERT INTO entity_types (id, name) VALUES (?, ?)",
          ('data-source', 'Источник данных'))
```
