# Asymptote Framework — Справочник

## Что такое асимптота

Асимптота — недостижимый идеал, задающий направление развития.
Чем ближе система к асимптоте, тем больше усилий нужно для
дальнейшего приближения. Истинная цель — не достижение (оно невозможно),
а постоянное движение.

## Как это устроено в коде

### crystal_observer.py

Файл: `scripts/crystal_observer.py`

**ASMPTOTES** — словарь с мета-данными каждой асимптоты:
```python
ASMPTOTES = {
    'connectivity': {
        'name': 'Связность', 'target': 1.0, 'unit': '%',
        'icon': '🔗', 'direction': 'up',
        'desc': 'Доля записей KC, привязанных к сущностям в EE',
    },
    # ... 5 more
}
```

**compute_asymptotes(data)** — вычисляет все 6. Возвращает dict:
```python
{
    'connectivity': {
        'current': 0.89,       # текущее значение
        'target': 1.0,         # идеал
        'gap': 0.11,           # абсолютный разрыв
        'normalised_gap': 0.11, # 0-1, сравнимый между асимптотами
        'unit': '%',
        'icon': '🔗',
    },
    # ...
}
```

**analyse_asymptotes(asymptotes)** — ранжирует по normalised_gap,
определяет worst (драйвер) и best (куда меньше всего усилий).

**save_asymptotes(asymptotes)** — сохраняет в `cache/crystal_asymptotes.json`
для crystal_will.

### crystal_will.py (Phase 5 — Strategist mode, expanded 2026-06-12)

Файл: `scripts/crystal_will.py`

**Phase 5 change (2026-06-12):** crystal_will no longer executes actions.
It ONLY decides and writes a command for Hermes.

**Expanded 2026-06-12:** crystal_will now handles **discoveries** alongside asymptotes.
См. [self-discover-impl.md](./self-discover-impl.md).

**DRIVERS** — каждая асимптота привязана к описанию:
```python
DRIVERS = {
    'connectivity':  {'name': 'Связность',         ...},
    'coverage':      {'name': 'Покрытие',          ...},
    'elegance':      {'name': 'Элегантность',      ...},
    'predictability':{'name': 'Предсказательность', ...},
    'speed':         {'name': 'Скорость реакции',  ...},
    'autonomy':      {'name': 'Автономность',      ...},
}
```

**choose(asymptotes, discoveries=None)** — выбирает направление:
1. Загружает асимптоты из `cache/crystal_asymptotes.json`
2. Загружает открытия из `cache/crystal_discoveries.json`
3. Собирает все сигналы: асимптоты (priority=normalised_gap) + открытия (priority=signal_strength × 1.2)
4. Ранжирует по priority (убывание)
5. Возвращает лучший сигнал — асимптоту ИЛИ открытие

**write_command(driver_key, aspects, chosen_signal=None)** — пишет команду в `cache/crystal_command.json`:
```json
{
  "ts": "...",
  "driver": "cluster_suggestion_log_unknown",
  "driver_name": "Повторяющийся паттерн: suggestion:log_unknown",
  "signal_type": "discovery",          // ← asymptote или discovery
  "discovery_details": { ... },        // ← только если discovery
  "desc": "Паттерн встретился 271 раз...",
  "normalised_gap": 1.2,
  "context": {...},
  "status": "pending"
}
```

**Hermes (agent)** читает команду и выполняет. Кристалл больше не исполняет — только решает.

## Детали вычислений

### 1. Связность (connectivity)

```python
connected = kc_total - orphans
connectivity = connected / max(kc_total, 1)
```

Считает долю записей KC, у которых есть хотя бы одно совпадение
с именем сущности из EE. Сироты = записи без ни одного совпадения.

### 2. Покрытие (coverage)

```python
n = len(domains)
uniform_share = 1.0 / n
deviations = [abs(s - uniform_share) for s in shares]
max_deviation = 2 * (n - 1) / n
coverage = 1 - (actual_deviation / max(max_deviation, 0.001))
```

Normalised deviation from uniform (1 — идеально равномерно, 0 — всё в одном домене).
Использует топ-10 доменов из KC.

### 3. Элегантность (elegance)

```python
noisy = COUNT(*) WHERE raw_text IS NULL OR LENGTH(raw_text) < 30
total = COUNT(*)
elegance = 1 - (noisy / max(total, 1))
```

Доля записей, не являющихся «шумом» (короткие/пустые записи).

### 4. Предсказательность (predictability)

```python
predictability = successes / max(failures, 1)
```

Соотношение success к failure. Идеал = 5 (в 5 раз больше успехов, чем ошибок).
Текущее (июнь 2026): ~0.9 — failures почти равны success.

### 5. Скорость реакции (speed)

```python
# Средняя разница между ts последних 100 записей
deltas = [t[i] - t[i+1] for i in range(len(recent_ts) - 1)]
speed = sum(deltas) / max(len(deltas), 1) / 86400  # в днях
```

Фильтр: только delta < 7 дней (отсекает аномалии).

### 6. Автономность (autonomy)

```python
self_sources = {'crystal_will', 'crystal_observer', 'autonomous_agent',
                'self-improvement', 'skill-indexer', 'proactive_executor'}
commanded_sources = {'user_query', 'user'}

autonomy = self_count / max(self_count + commanded_count, 1)
```

Доля действий, инициированных системой, а не пользователем.

## Нормализация gap

Для сравнения между асимптотами gap нормализуется в [0, 1]:

- **connectivity, coverage, elegance, autonomy**: gap = target - current
  (target = 1.0, так что gap in [0, 1])
- **predictability**: normalised_gap = min(1.0, (target - current) / target)
  (target = 5.0, gap масштабируется)
- **speed**: normalised_gap = min(1.0, gap / 7.0)
  (7 дней — практический максимум задержки)

## Принципы

1. **Gap ≠ 0 — норма.** Если gap = 0, подними цель.
2. **Драйвер ≠ всегда одно и то же.** Если худшая асимптота не меняется
   несколько циклов — проанализируй, почему действие не помогает.
3. **TRIGGER_THRESHOLD = 0.3.** Если gap > 30% — активное действие.
   Если < 30% — профилактика.
4. **Нирвана — смерть.** Кристалл в равновесии — кристалл без движения.
   Асимптоты гарантируют, что всегда есть «лучше».
5. **Асимптоты субъективны.** Цели могут пересматриваться.
   5:1 для predictability — хорошо. 10:1 — лучше. Когда достигнешь 5:1 —
   подними до 10:1.
6. **Gap ≠ реальная проблема (critical lesson 2026-06-12).** Predictability
   gap (83%) оказался артефактом классификации: 91% «failures» — это
   auto-generated suggestions от improvement_suggestions, не реальные ошибки.
   **Всегда проверяй sample данных перед тем как действовать по асимптоте.**
   Цифры — симптомы; первопричина может быть выше по pipeline (классификатор,
   источник данных).
