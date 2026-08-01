---
name: unknown-classification-by-source
description: "Классификация unknown записей Knowledge Cube не по содержанию (regex/keywords), а по source — трассировке происхождения. Превращает 660+ unknown в 0 за один прогон."
tags: [knowledge-cube, classification, unknown, source-trace]
---

# Unknown Classification by Source

## Проблема

В Knowledge Cube есть записи с `axis_outcome='unknown'`. `verify_outcomes.py` пытается классифицировать их по ключевым словам в `raw_text` — и терпит неудачу (1 из 661), потому что:

- 60-70% unknown — это **пользовательские запросы** (вопросы, команды, просьбы)
- 10-15% — **результаты работы скриптов** (каждый скрипт записал одну запись)
- 10-15% — **знания из Lavra** (факты, решения, паттерны)
- Остальное — dimension_proposals, auto_research, system_notes

Ни у одной из этих категорий нет success/failure ключевых слов. Не потому что они плохо написаны, а потому что **они про другое**.

## Решение: подняться на уровень выше

Не читать текст записи — смотреть **откуда она пришла**.

У каждой записи есть поле `source`. Это строка, которая показывает какой процесс/скрипт/источник создал эту запись.

`source` → автоматически → `axis_outcome`:

| Source | axis_outcome |
|--------|-------------|
| `state_db` | `user_query` |
| `script_*` | `script_result` |
| `lavra_*` (decision, fact, learned, pattern, investigation) | `lavra_knowledge` |
| `dimension_proposals` | `dimension_proposal` |
| `auto_research` | `auto_research` |
| `gap_filler`, `improvement_suggestions` | `system_note` |
| `agent_decisions` | `agent_decision` |
| `git:*` | `git_commit` |
| `file:*` | `file_import` |

## Как применять

```python
SOURCE_MAP = {
    'state_db': 'user_query',
    'dimension_proposals': 'dimension_proposal',
    'lavra_decision': 'lavra_knowledge',
    'lavra_learned': 'lavra_knowledge',
    'lavra_fact': 'lavra_knowledge',
    'lavra_pattern': 'lavra_knowledge',
    'lavra_investigation': 'lavra_knowledge',
    'auto_research': 'auto_research',
    'gap_filler': 'system_note',
    'agent_decisions': 'agent_decision',
    'improvement_suggestions': 'system_note',
}

c.execute("SELECT id, source FROM experiences WHERE axis_outcome='unknown'")
for eid, source in rows:
    source = source or ''
    if source in SOURCE_MAP:
        c.execute("UPDATE experiences SET axis_outcome=? WHERE id=?", (SOURCE_MAP[source], eid))
    elif source.startswith('script_'):
        c.execute("UPDATE experiences SET axis_outcome='script_result' WHERE id=?", (eid,))
    elif source.startswith('file:'):
        c.execute("UPDATE experiences SET axis_outcome='file_import' WHERE id=?", (eid,))
    elif source.startswith('git:'):
        c.execute("UPDATE experiences SET axis_outcome='git_commit' WHERE id=?", (eid,))
```

## Расширение: «failure» — тоже неправильный bucket

Тот же паттерн работает и для `axis_outcome='failure'`. В этой сессии обнаружено:

| Source | Было | Стало | Кол-во |
|--------|------|-------|--------|
| `improvement_suggestions` | failure | system_note | 329 |
| `cube_analysis` | failure | system_note | 52 |

Эти записи содержат слова "error", "fail", "problem" — поэтому keyword-классификатор `verify_outcomes.py` пометил их как failure. Но они не про сбои — они про **анализ сбоев** (suggestion, analysis). Разные вещи.

**Правило:** если source говорит что это за запись — source прав. Keyword-классификация может только подтвердить, но не опровергнуть source.

## Аксиома

**Никогда не смотреть в raw_text для классификации типа записи.**
Текст — это content. Source — это context. Content без context = шум.

Если запись пришла из state.db — это пользовательский запрос. Что бы в нём ни было написано. Даже если там слово "success" 100 раз — это не результат, это запрос пользователя.

## Вторичная классификация: ложный failure

После source-классификации, проверь что `failure` — это действительно failure.
Исторический precedent: **improvement_suggestions** (329 записей) и **cube_analysis** (52 записи) были помечены как failure, хотя они — system_note (предложения исправлений и аналитические отчёты).

Правило: если source говорит что запись — suggestion, analysis, proposal или note — она не может быть failure, даже если говорит об ошибках.

| Source pattern | Correct outcome |
|---------------|----------------|
| `improvement_suggestions` | `system_note` |
| `cube_analysis` | `system_note` |
| `suggestion:*` | `system_note` |
| `analysis:*` | `system_note` |

## Когда применять

- После массового импорта данных в Knowledge Cube
- Когда white_spots или unknown внезапно выросли
- После добавления нового источника данных (новый скрипт, новый плагин)
- Каждый раз перед verify_outcomes (сначала source-classification, потом keyword-классификация)

## Расширение на Entity Cube: phantom_of

Тот же принцип — **«не удаляй, а проследи происхождение»** — работает и для сущностей в Entity Engine.

Когда EE ошибочно классифицирует сущность (например, прокси-сервер `dc01.steelproxy.com` как «Человек», или ID сессии `0f8o` как личность):

**Не удаляй.** Удалишь — потеряешь сигнал.

**Создай связь `phantom_of`** от ошибочной сущности к её реальному прообразу:

```sql
INSERT INTO relationships (source_entity_id, target_entity_id, relation_type)
VALUES (<фантом_id>, <реальный_id>, 'phantom_of');
```

Пример из практики:

| Фантом | Реальность | phantom_of |
|--------|-----------|------------|
| `dc01` | steelproxy.com (прокси для TG) | `dc01 --phantom_of--> Прокси для TG ботов` |
| `0f8o`, `c65` | WSL encoding issue | `0f8o --phantom_of--> WSL encoding issue` |
| `ai_frontier_you` | TG-канал пользователя | `ai_frontier_you --phantom_of--> TG-каналы пользователя` |
| `hotelcrimeabot` | Telegram бот отеля | `hotelcrimeabot --phantom_of--> Telegram боты отелей` |
| `echo` | Команда echo | `echo --phantom_of--> Команда echo` |

**Правило:** если Entity Engine ошиблась — ошибка не в том, что сущность существует, а в том, что её тип не распознан. Исправь тип (или создай `phantom_of`), не удаляй строку.

### Как найти фантомов

```sql
-- Сущности с типом «Человек», но не являющиеся людьми
SELECT e.name, e.mention_count FROM entities e
JOIN entity_types t ON e.type_id = t.id
WHERE t.name = 'Человек'
AND e.name NOT IN ('Александр');
```

После очистки: для каждого найденного определи что это на самом деле (сервер, команда, ID, бот), создай реальную сущность нужного типа, и свяжи фантом → real через `phantom_of`.

Полный справочник: [references/phantom-tracing.md](./references/phantom-tracing.md)

## Инсайты

- У axis_outcome не 3 варианта (success/failure/unknown), а сколько нужно
- Пользовательские запросы не бывают success/failure — они user_query
- Результаты скрипта — script_result
- Знания из Lavra — lavra_knowledge
- **unknown должен быть = 0 всегда.** Каждая запись о чём-то. Найди её источник — и ты знаешь её тип.
- **То же самое для EE:** ни одна сущность не «мусор». Ошибочная классификация — не повод удалять, а повод проследить происхождение (`phantom_of`).
