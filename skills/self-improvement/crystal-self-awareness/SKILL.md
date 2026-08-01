---
name: crystal-self-awareness
description: "Crystal self-awareness workflow: run iterative cycles, clear studied cache, verify self_model.json updates"
category: self-improvement
tags: [crystal, self-awareness, self-model, iterative, self-model-json]
---

# Crystal Self-Awareness Workflow

Скилл для запуска кристалла самосознания (crystal.py) в итеративном режиме с проверкой обновления self_model.json.

## Trigger Conditions
- Запуск crystal.py --iterative N
- Необходимость очистки studied в cache/self_model.json
- Проверка что self_model обновился (studied + znu)

## Workflow

### 1. Запуск итеративного режима
```bash
python scripts/crystal.py --iterative 3
```

### 2. Проверка output ≠ input (каждый цикл — уникальное действие)
- Цикл 1: Должно быть уникальное действие (например, extract_entities)
- Цикл 2-3: Должны отличаться от цикла 1 (например, "fabric не содержал новых сущностей" или совесть-действие)

### 3. Если вывод "всё сделано" — очистка studied
```python
# Оставить последние 5 записей в studied
import json
with open('cache/self_model.json', 'r') as f:
    model = json.load(f)
model['sovest']['studied'] = model['sovest']['studied'][-5:]
with open('cache/self_model.json', 'w') as f:
    json.dump(model, f, indent=2, ensure_ascii=False)
```

### 4. Запуск ещё раз
```bash
python scripts/crystal.py --iterative 3
```

### 5. Проверка обновления self_model.json
Должно содержать:
- `studied` — обновлённый массив (последние 5 + новые)
- `znu` — словарь знаний о доменах/источниках/аномалиях

## Expected Results

### Self-model.json structure после успешного прогона:
```json
{
  "version": "1.0",
  "last_cycle": "2026-07-13T08:57:56",
  "cycle_count": 130,
  "znayu": {...},
  "umeyu": {...},
  "ne_znayu": {...},
  "istoriya": {...},
  "gorizonty": {...},
  "sovest": {
    "assessments": [...],
    "last_assessment": "2026-07-13",
    "studied": ["coding", "research", "debugging", "creative", "latent-domain-detector", ...новые...]
  },
  "znu": {
    "bugfix": "Углубление 'bugfix': 505 записей...",
    "music-audio": "Слепое пятно 'music-audio': 19 записей...",
    ...
  },
  "modifications": [...],
  "plan": {...},
  "mod_evals": [...],
  "self_awareness": {...}
}
```

## Verification Checklist
- [ ] Цикл 1 output ≠ Цикл 2 output ≠ Цикл 3 output
- [ ] self_model.json содержит `studied` (массив)
- [ ] self_model.json содержит `znu` (объект с ключами-доменами)
- [ ] `cycle_count` увеличился на 3
- [ ] `last_cycle` обновился на текущее время

## Common Pitfalls
- Если crystal.py зависает на 3-м цикле — увеличь timeout
- Если studied не очищается — проверь путь к cache/self_model.json
- Если znu пустой — проверь что _evaluate_conscience_learning вызывается
- Если "всё сделано" — это значит источник исчерпан, нужен другой источник (script_sensor_array, script_web_surfer, improvement_suggestions, dimension_proposals)

## References
- crystal.py — основной скрипт (scripts/crystal.py)
- self_model.json — модель себя (cache/self_model.json)
- Knowledge Cube — knowledge_cube.db
- Entity Engine — entity_engine.db
- Fler Engine — fler_engine.db
- `references/lessons-learned-2026-07-14.md` — ключевые выводы сессии 2026-07-14