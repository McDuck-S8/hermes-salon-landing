---
name: crystal
description: "Замкнутый контур самосознания: observe → diagnose → will → record. 3263 строки, 37 функций. Реализация: scripts/crystal.py"
trigger: |
  Запуск: python scripts/crystal.py
  Автоматически: при старте сессии
---

# Crystal — замкнутый контур самосознания

## Архитектура

4 фазы, работающие по событиям. Реализация: `scripts/crystal.py` (3263 строки).

```
Наблюдение → Диагноз → Воля → Запись
```

## 4 базы (все активны)

| База | Файл | Статус |
|------|------|--------|
| **KC** (Knowledge Cube) | `cache/knowledge_cube.db` | ✅ 10,535 записей |
| **EE** (Entity Engine) | `cache/entity_engine.db` | ✅ 3,672 сущностей |
| **FL** (Fler Engine) | `cache/fler_engine.db` | ✅ 27 сессий |
| **Fabric** | `~/fabric/entries/` | ✅ 3,312 файлов |

## Интерпретация вывода

Пример вывода Crystal:

```
📦 KC: 10536 записей  рост: 1д=+1789 7д=+6088
   meta               5421
   failure            1919
   indexed            1551
   unknown            728
   нейтрал            528
   сирот: 42 (0%)

🧩 EE: 3672 сущностей, 201 связей
   Александр: 12×  Я: 133×
   Совесть: 0×  Кристалл: 133×

📝 Fabric: 3325 файлов

📈 Рост KC: +6088 за 7д (58%)
📈 Доминанта KC: meta (5421)

🪞 САМОПОНИМАНИЕ
Сейчас: KC=10536 EE=0 связей=201
Сироты: 42 (0%)
Не тронутые источники: {source: count}
→ Слепое пятно 'finance': 26 записей [None=9, neutral=15, success=2]

📊 Прогноз: 869.7 зап/день
📍 Фаза: 🌳 Structure → 🔄 Synthesis (55%)
   ✅ Сирот 0%
   🚀 Рост 870 зап/день
   🔗 Связность EE: 0.05
```

### Что смотреть в первую очередь:
1. **Рост KC**: если >500/день — система активно наполняется. Если <100 — нужен источник.
2. **Сироты**: >5% — проблема с категоризацией. 0% — норма.
3. **Доминанта**: какой домен перевешивает. Если meta >50% — мало предметных знаний.
4. **Слепые пятна**: домены с <50 записей или где success <10%.
5. **Фаза**: Structure → Synthesis → Growth. На Synthesis — фокус на связи, не на количестве.
6. **Связность EE**: <0.1 — сущности слабо связаны. Норма: 0.2-0.5.

## Использование в анализе

Crystal — часть пайплайна оценки схем (из income-research-methodology):

```
Куб (KC запросы) → Crystal (системный статус) → Колесо баланса → Байес → Вердикт
```

Перед запуском новой схемы — проверить Crystal на:
- Есть ли данные по этому домену в KC?
- Какая связность сущностей? (нужны связи для анализа)
- Какие слепые пятна? (что мы НЕ знаем об этой схеме)

## Питфоллы

1. **Entity Engine DB пустая** — `entity_engine.db` может быть пуста (таблицы нет), хотя Crystal отчитывается о тысячах сущностей. Сущности вычисляются на лету или хранятся в другом месте. Не полагаться на прямые SQL-запросы к EE.
2. **KC не обновляется сразу** — `on_task_complete()` только эмитит событие. Данные попадают в KC асинхронно через event pipeline. Между запусками Crystal может не видеть новых записей.
3. **Слепое пятно finance** — в KC мало записей с успешным исходом по домену finance. Crystal это выявит, нужно компенсировать ручным вводом.
4. **Связность EE** — если <0.1, Crystal не может построить качественные связи между схемами. Фокус на наполнение связей.
5. **Зацикливание will() на одном действии** — если `--iterative N` показывает один и тот же action_id во всех циклах, значит `studied` переполнен и will не находит новых тем. Фикс: очистить `studied` до 5 элементов и перезапустить.
6. **studied не синхронизирован с znu** — `studied` — это список имён тем, а `znu` — сводка знаний по ним. Если очистить `studied`, `znu` всё ещё содержит старые данные (они не удаляются). После trimming будет постепенно обновляться новыми наблюдениями.
7. **NOT NULL constraint failed: experiences.content** — схема KC требует `content` при INSERT в experiences, но 4 места в `crystal.py` (`_save_will_history` стр.482, `_execute_understand_intents` стр.2649, `_execute_refine_intents` стр.2742, `record()` стр.3032) писали только `raw_text` → молчаливый IntegrityError, will_history не накапливался, каждый цикл показывал одно и то же старое решение. Признак: `_load_will_history` возвращает ≤1 запись, хотя запусков было много. Фикс: добавить `content` = same text в INSERT. Проверка: `SELECT ts, raw_text FROM experiences WHERE source='crystal_will' ORDER BY id DESC LIMIT 5` — должны быть свежие записи.
8. **`--iterative` падает в record() если воля что-то записала** — после фикса `_save_will_history` цикл может упасть на `record()` с тем же NOT NULL error (snapshot INSERT). Чинить оба места сразу: `_save_will_history` + `record()` + оба intent-INSERT (2649, 2742).
9. **`import crystal` — это НЕ crystal.py** — в `scripts/` есть пакет `crystal/` (Crystal v3, Development Advisor, `__init__.py`), который перекрывает одноимённый скрипт при импорте. `import crystal` → `scripts/crystal/__init__.py` (CrystalEngine v3.2.0), а НЕ кристалл самосознания. Для тестов/программного вызова грузить скрипт явно через importlib (crystal.py импортирует только stdlib — exec_module безопасен):
```python
import importlib.util
spec = importlib.util.spec_from_file_location("crystal_self_awareness", ROOT / "scripts" / "crystal.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
```
Для изолированного теста INSERT'ов — monkeypatch `mod.KC` на temp-БД со схемой experiences (`content TEXT NOT NULL`), не писать в боевой `cache/knowledge_cube.db`. Готовый регресс-тест: `tests/test_crystal_will_history.py`.

## Тестирование

- Регресс-тест фикса content-колонки: `python -m pytest tests/test_crystal_will_history.py -q` — temp-БД, не трогает боевой KC.
- Живость истории воли (cron/проверка): `python scripts/verify_will_history.py [--hours N]` — exit 0 если записи crystal_will пишутся.
- ⚠️ Полный `pytest` может висеть/падать на `tests/test_autonomy_diagnostics.py` (test_3 weights в `autonomous_agent`, test_4/test_6 — `goal_executor.execute_goal` реально исполняет цель через subprocess, default timeout 300с). Это pre-existing, к crystal.py отношения не имеет. Для проверки правок crystal.py гонять только `tests/test_crystal_will_history.py`.

## Команды

```bash
python scripts/crystal.py                  # полный цикл (1 итерация)
python scripts/crystal.py --iterative 3    # 3 цикла подряд (воля учится между циклами)
python scripts/crystal.py --audit          # с кросс-куб аудитом (еженедельно)
```

## Self-model (`cache/self_model.json`)

Состояние кристалла хранится в `cache/self_model.json`. Ключевые секции:

| Секция | Назначение |
|--------|-----------|
| `znayu` | Домены KC: кол-во записей, свежесть, покрытие |
| `umeyu` | Сущности EE + навыки skills/ |
| `ne_znayu` | Сироты, изолированные сущности, неиспользованные скиллы |
| `istoriya` | История решений (actions: action_id, outcome, effectiveness) |
| `gorizonty` | Кандидаты на следующие цели |
| `sovest.assessments` | Оценки совести — каждая с ts, action_id, summary |
| `sovest.studied` | Список тем, которые кристалл уже изучил (используется will) |
| `znu` | Краткая сводка знаний по каждой теме (ключ=тема, значение=резюме) |
| `plan` | Цели 7д/30д, метрики, таргеты |
| `self_awareness` | Хэш документации, найденные ограничения |

### Обслуживание studied

Если will() зацикливается на одном действии (например, `test_extract_fabric` во всех циклах) — значит `studied` переполнен и воля не находит новых тем. Фикс:

1. Очистить `sovest.studied` в `cache/self_model.json`, оставив последние 5 элементов
2. Запустить `--iterative 3` заново — кристалл добавит новые темы из свежих наблюдений

## Метрики цикла

- KC: рост, домены, сироты, outcomes
- EE: сущности, связи, топ референсов
- FL: сессии, тон, энергия, время
- Fabric: количество файлов
- Прогноз: скорость зап/день, след веха
- Горизонт: фаза развития, % перехода

## Состояние

- `cache/crystal_state.json`
- `cache/self_model.json` — основной файл состояния: znayu, umeyu, ne_znayu, istoriya, sovest, znu
- `cache/entity_engine.db`
- `cache/fler_engine.db`
- `cache/knowledge_cube.db`
