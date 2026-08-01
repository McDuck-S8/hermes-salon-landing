# Self-Discover — Самостоятельное обнаружение аномалий

Добавлено 2026-06-12 в crystal_observer.py. Функция `self_discover(data)` — 
кристалл самостоятельно находит аномалии в сырых данных KC, EE и Fler, 
без предопределённых метрик.

## Зачем

Предыдущая архитектура: crystal_will сравнивал 6 предопределённых асимптот 
и выбирал худшую. Кристалл был слеп ко всему, что не входит в эти 6 метрик:
- improvement_suggestions (489 записей) — не видел
- AI Agent без связей в EE — не видел
- Наш чат как сигнал — не видел
- Инвентарь скиллов — не видел

Self_discover даёт кристаллу **глаза** — он сам решает, на что смотреть.

## Архитектура

```
crystal_observer.py
  ├─ read_all() — собирает данные со всех кубов
  ├─ compute_asymptotes() — 6 предопределённых метрик
  ├─ self_discover() — находит аномалии ← НОВЫЙ ШАГ
  ├─ analyse_asymptotes() — ранжирует
  └─ save_asymptotes() + save_discoveries() → JSON
```

## Типы открытий (discovery types)

### 1. unprocessed_source — Непроанализированные источники

**Что ищет:** источники в KC с >20 записей, но <30% из них проанализированы 
(имеют axis_domain не uncategorized).

**SQL:**
```python
k.execute("SELECT source, COUNT(*) FROM experiences WHERE source IS NOT NULL GROUP BY source")
sources = dict(k.fetchall())
high_volume = ['improvement_suggestions', 'log_tool_error', 'uncategorized']
for sv in high_volume:
    count = sources.get(sv, 0)
    if count > 20:
        k.execute("SELECT COUNT(*) FROM experiences WHERE source=? AND (axis_domain IS NOT NULL AND axis_domain != '' AND axis_domain != 'uncategorized')", (sv,))
        analyzed = k.fetchone()[0]
        ratio = analyzed / max(count, 1)
        if ratio < 0.3:
            discoveries.append({...})
```

**signal_strength:** `min(1.0, count / 500 * (1 - ratio))` — чем больше необработанных записей, тем сильнее сигнал.

### 2. content_cluster — Повторяющиеся паттерны

**Что ищет:** в improvement_suggestions — кластеризует по типу предложения `[suggestion:xxx]`.

**Логика:**
```python
pattern_counts = Counter()
for t in texts:
    if t.startswith('['):
        end = t.find(']')
        if end > 0 and end < 60:
            ptype = t[1:end]
            pattern_counts[ptype] += 1
```

**signal_strength:** `min(1.0, pc / max(len(texts), 1) * 2)` — чем больше доля паттерна во всех записях, тем сильнее.

**Пример из прогона 2026-06-12:**
- `suggestion:log_unknown` — 271× (55% всех improvement_suggestions) → signal=100%
- `suggestion:log_tick_failure` — 144× → signal=59%
- `suggestion:log_api_error` — 39× → signal=16%

### 3. isolated_entities — Изолированные сущности

**Что ищет:** AI Agent сущности в EE, у которых нет ни одной связи (source_entity_id или target_entity_id = NULL в relationships).

**SQL:**
```sql
SELECT COUNT(DISTINCT e.id) FROM entities e
JOIN entity_types et ON e.type_id=et.id
LEFT JOIN relationships r ON e.id = r.source_entity_id OR e.id = r.target_entity_id
WHERE et.name='AI Agent' AND r.id IS NULL
```

**signal_strength:** `min(1.0, isolated / max(total_agents, 1))`

### 4. disconnected_network — Разобщённая сеть

**Что ищет:** доля AI Agent, у которых есть хотя бы одна связь. Если <30% агентов связаны — сигнал.

**SQL:**
```sql
SELECT COUNT(DISTINCT r.source_entity_id) FROM relationships r
JOIN entities e ON r.source_entity_id=e.id
JOIN entity_types et ON e.type_id=et.id
WHERE et.name='AI Agent'
```

**signal_strength:** `1 - (connected_agents / max(total_agents, 1))`

**Пример:** 64 из 269 AI Agent имеют связи (24%) → signal=76%

### 5. chat_signal — Сигнал из чата

**Что ищет:** записи с source='chat' или source='aggregator', ищет ключевые слова.

**Ключевые слова:** agency-agents, crystal, predictability, роль, role, примерка, build, строить, месиво

**signal_strength:** фиксированный 0.6 — умеренный, так как интерпретация субъективна.

### 6. inventory_available — Неиспользованные инструменты

**Что ищет:** записи с source='inventory' и axis_domain='skills' — если есть, значит инвентарь загружен, но не применён.

**signal_strength:** фиксированный 0.5.

### 7. fler_state — Эмоциональное состояние

**Что ищет:** если средняя energy во Fler > 0.6 — кристалл в активной фазе.

**signal_strength:** `min(1.0, energy * 0.8 + engagement * 0.2)`

## Формат crystal_discoveries.json

```json
[
  {
    "type": "content_cluster",
    "source_key": "cluster_suggestion_log_unknown",
    "name": "Повторяющийся паттерн: suggestion:log_unknown",
    "icon": "🔍",
    "desc": "Паттерн \"suggestion:log_unknown\" встретился 271 раз в improvement_suggestions (всего 489 записей)",
    "count": 271,
    "total": 489,
    "signal_strength": 1.0
  },
  {
    "type": "disconnected_network",
    "source_key": "isolated_agents",
    "name": "Сеть AI Agent не сформирована",
    "icon": "🕸️",
    "desc": "Только 64 из 269 AI Agent имеют связи — нет сети",
    "count": 64,
    "total": 269,
    "signal_strength": 0.76
  }
]
```

## Как discoveries попадают в crystal_will

1. crystal_observer сохраняет discoveries в `cache/crystal_discoveries.json`
2. crystal_will читает оба файла: `crystal_asymptotes.json` + `crystal_discoveries.json`
3. В `choose()` все сигналы собираются в один массив:
   - Асимптоты: priority = normalised_gap
   - Открытия: priority = signal_strength × 1.2 (небольшой бонус новизне)
4. Массив сортируется по priority (убывание)
5. Лучший сигнал становится драйвером — независимо от того, асимптота это или открытие
6. Если драйвер — открытие, в crystal_command.json добавляется `signal_type: "discovery"`

## Расширение

Чтобы добавить новый тип открытия:
1. Добавь секцию в `self_discover()` в crystal_observer.py
2. Discovery должен иметь поля: type, source_key, name, icon, desc, count, total, signal_strength
3. signal_strength должен быть в [0, 1] — можно сравнивать с normalised_gap асимптот
4. Не нужно менять crystal_will — он автоматически подхватит любые discoveries

## Связь с кристальной слепотой

self_discover — прямое следствие проблемы crystal blindness (см. crystal-blindness-2026-06-12.md).

Без self_discover:
- crystal_will видит только 6 чисел
- 486 "лог-шумных" improvement_suggestions невидимы
- 155 изолированных AI Agent невидимы
- Кристалл выбирает predictability снова и снова, потому что это единственная ось

С self_discover:
- Кристалл видит кластеры, изоляцию, чат, инвентарь
- Может выбрать открытие (signal=100%) вместо асимптоты (gap=34%)
- Сам решает, что для него важно
