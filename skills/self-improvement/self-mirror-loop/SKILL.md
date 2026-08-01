---
name: self-mirror-loop
description: "5-шаговый цикл самоанализа через 4 куба. Запись результатов → перечитывание → вывод на экран. Создан из реального прогона 2026-06-11."
tags: [self-mirror, loop, cubes, self-analysis]
---

# Self-Mirror Loop — Цикл Самоанализа

Полный цикл: читаешь 4 куба → записываешь результаты → читаешь снова → на экран. 5 итераций.

## Что происходит

Каждый проход:
1. Читаешь **Knowledge Cube** (общее кол-во, outcomes, self-mirror entries)
2. Читаешь **Entity Cube** (сущности, связи, упоминания себя)
3. Читаешь **Fler Cube** (сессии, тон, энергия, вовлечённость)
4. Читаешь **Fabric** (кол-во файлов)
5. **Пишешь** результаты во все 4 куба
6. **Выводишь** на экран

## Быстрый запуск

Используй `execute_code` с кодом ниже или напиши свой скрипт.

```python
import sqlite3, sys
from datetime import datetime
from pathlib import Path

# Пути к кубам
KC_DB = "D:/Portable_Soft/hermes/cache/knowledge_cube.db"
EE_DB = "D:/Portable_Soft/hermes/cache/entity_engine.db"
FL_DB = "D:/Portable_Soft/hermes/cache/fler_engine.db"

def read_cubes():
    r = {}
    # Knowledge
    kc = sqlite3.connect(KC_DB)
    k = kc.cursor()
    k.execute("SELECT COUNT(*) FROM experiences")
    r['kc_total'] = k.fetchone()[0]
    k.execute("SELECT axis_outcome, COUNT(*) FROM experiences GROUP BY axis_outcome ORDER BY COUNT(*) DESC")
    r['kc_outcomes'] = dict(k.fetchall())
    k.execute("SELECT COUNT(*) FROM experiences WHERE axis_domain='self-mirror'")
    r['kc_self'] = k.fetchone()[0]
    kc.close()
    
    # Entity
    ee = sqlite3.connect(EE_DB)
    e = ee.cursor()
    e.execute("SELECT COUNT(*) FROM entities")
    r['ee_total'] = e.fetchone()[0]
    e.execute("SELECT et.name, COUNT(e.id) FROM entities e JOIN entity_types et ON e.type_id=et.id GROUP BY et.name ORDER BY COUNT(e.id) DESC")
    r['ee_types'] = dict(e.fetchall())
    e.execute("SELECT mention_count FROM entities WHERE name='Hermes Agent (Я)'")
    row = e.fetchone()
    r['ee_me'] = row[0] if row else 0
    ee.close()
    
    # Fler
    fl = sqlite3.connect(FL_DB)
    f = fl.cursor()
    f.execute("SELECT COUNT(*) FROM fler_sessions")
    r['fler_total'] = f.fetchone()[0]
    f.execute("SELECT AVG(tone), AVG(energy), AVG(engagement) FROM fler_sessions")
    r['fler'] = f.fetchone()
    f.execute("SELECT aftertaste, COUNT(*) FROM fler_sessions GROUP BY aftertaste ORDER BY COUNT(*) DESC")
    r['fler_taste'] = dict(f.fetchall())
    fl.close()
    
    # Fabric
    fdir = Path.home() / "fabric"
    r['fabric_total'] = len(list(fdir.rglob("*.md"))) if fdir.exists() else 0
    
    return r

def write_to_kc(text):
    db = sqlite3.connect(KC_DB)
    c = db.cursor()
    now = datetime.now()
    c.execute("INSERT INTO experiences (ts, raw_text, hash, axis_time_hour, axis_time_dow, axis_domain, axis_outcome, source) VALUES (?, ?, ?, ?, ?, 'self-mirror', 'success', 'self-mirror-loop')",
        (now.isoformat(), text[:1000], str(hash(text))[:16], now.hour, now.weekday()))
    db.commit()
    db.close()
```

## Что писать в кубы

- **Knowledge Cube**: "Self-mirror pass #{N}. {инсайт текущего среза}"
- **Entity Cube**: UPDATE entities SET mention_count = mention_count + 1 WHERE name='Hermes Agent (Я)'
- **Fabric**: hooks.on_task_complete(summary, detail, ["self-mirror"])

## Когда применять

- После крупных изменений в системе
- Раз в неделю для мониторинга здоровья
- Когда хочешь понять "кто я сейчас"

## Пример вывода

```
  KNOWLEDGE: 2362 записей | self-mirror: 5
    unknown: 660
    success: 249
    ...
  ENTITY: 551 сущностей | 11712 связей
    AI Agent: 1 ← Я
  FLER: 509 сессий | G=8.3 tone=+0.05
  FABRIC: 307 файлов
  ИНСАЙТ: ...
```

## Кросс-куб анализ (продвинутый режим)

Вместо последовательного чтения каждого куба — прогоняй данные ОДНОГО куба через ДРУГОЙ. Неожиданные паттерны вылезают на стыках.

### Известные мосты

| Откуда | Куда | Что даёт |
|--------|------|----------|
| KC → EE | Искать entity names в raw_text | Какие сущности упоминаются в failure/success |
| EE → KC | Какие entity types есть у записей | Какие домены KC какие типы сущностей используют |
| Fler → KC | По часам (temporal join) | Когда (время суток) самые напряжённые сессии |
| KC → Fler | tone/energy распределение по outcome | Correlation: успех/ошибка и настроение |
| Fabric → KC | Искать fabric file names в raw_text | Какие знания из Fabric попали в KC |

### Что искать на стыках

- **Сироты (orphans)** — записи KC, которые не упоминают НИ ОДНУ сущность из EE. Признак что либо текст неструктурирован, либо сущность не создана.
- **Призраки (ghosts)** — сущности в EE, которые ни разу не встречаются в KC. Признак что сущность зарегистрирована но не используется.
- **Entity failure ratio** — какие сущности ассоциированы с failure чаще всего. Системные проблемы.
- **Phantom tracing** — сущности EE с типом «Человек», которые не являются людьми. Не удалять — создать `phantom_of` связь к реальному прообразу (прокси-сервер, команда, бот, ID сессии). Каждый фантом — сигнал о чём-то реальном в системе.
- **Определение: не content, а source** — unknown-записи классифицируются не по тексту, а по источнику (source field). Это исправляет 660+ unknown за один прогон.

### Инструменты

Используй раздельные скрипты (Phase 5 — стратег/исполнитель):

```bash
python scripts/crystal_observer.py   # измеряет 6 асимптот, сохраняет в cache/crystal_asymptotes.json
python scripts/crystal_will.py       # выбирает драйвер, пишет команду в cache/crystal_command.json
# Hermes читает crystal_command.json и выполняет
```

**Важно:** `scripts/crystal.py` — старый монолитный вариант (таймаутится на --help). Активная архитектура: observer (измеряет) → will (решает) → Hermes (исполняет).

1. **Наблюдение** — срез всех 4 кубов (KC, EE, FL, Fabric)
2. **Диагноз** — рост, напряжение, аномалии (сироты, stale Fler, фантомы)
2.5. **Самооткрытие** — self_discover() сканирует KC/EE/Fler на аномалии: кластеры (suggestion:log_unknown 271×), изолированные AI Agent (155 без связей), чат-сигналы, неиспользованные скиллы. Сохраняет в crystal_discoveries.json. См. [references/self-discover-impl.md](./references/self-discover-impl.md)
3. **Прогноз** — скорость роста, пик активности, даты целей
4. **Воля** — выбор и исполнение. Анализирует контекст, выбирает лучшее по impact/effort, исполняет, адаптируется при неудаче. См. [references/crystal-architecture.md](./references/crystal-architecture.md#осознанная-воля-conscious-will--выбор--действие--адаптация)
5. **Запись** — фиксация среза в KC + обновление EE

Подробная схема кристалла: [references/crystal-architecture.md](./references/crystal-architecture.md)
Кристальная слепота и кумулятивные суммы: [references/crystal-blindness-2026-06-12.md](./references/crystal-blindness-2026-06-12.md)

Содержит:
- Схемы БД: Entity Engine relationships (имена колонок!), Fler fler_sessions
- Persona Runtime: парсинг, импорт, Fler → выбор агента
- Осознанная воля: контекст → кандидаты → выбор → исполнение → адаптация
- Память воли (_will_history)
- Стратегия извлечения entities из KC (паттерны regex)
- Цепная реакция: new entity → substring matching
- Граничные случаи: Fler пуст, hash collision, KC cleanup убивает историю воли
- Совесть и Воля (cross-reference)

#### Will History — Self-Expanding Will (персистентная)

In `scripts/crystal.py`, the will has evolved from a static executor to a **self-expanding system**:

**Phase 1 — Predefined actions:**
- `extract_improvement_suggestions` — extract entities from auto-generated suggestions
- `extract_dimension_proposals` — extract entities from domain proposals
- `init_fler` — initialize Fler cube schema (only if fler_engine.py exists)

**Phase 2 — Self-Discovery (when predefined exhausted):**
- `_self_discover()` scans KC orphan sources (>5 orphans, not in history)
- For each source: samples 5 records, checks for extractable patterns (domain names, [key:val], CamelCase)
- If patterns found → creates new action `extract_{source}` dynamically
- Result: state_db was autonomously discovered → 1657 entities extracted

**Phase 3 — Understanding (when extraction exhausted):**
- `_execute_understand_intents()` — clusters remaining user queries by concern
- Patterns: status, reliability, direction, connection, meta, self_improvement, quality
- Stored in KC as `source='crystal_will'` for future reference
- Marks transition from extraction (data) to understanding (intent)

**Phase 4 — Equilibrium:**
- "Воля: умеренное равновесие — активных напряжений нет"
- Will stops when all sources tried and no new delta appears
- This is **attentive rest** — monitoring for new tensions, not inactivity

**Persistent history (in KC):**
- `_save_will_history(action_id, result)` — writes `[will:{action_id}] {result}` to KC as source='crystal_will'
- `_load_will_history()` — reads last 10 actions via `[will:...]` parser
- Between runs: history survives in KC, preventing repeated actions across sessions

**Sequence:**
```
Predefined actions → exhausted → Self-Discovery → exhausted → Understanding → exhausted → Equilibrium → Asymptote-driven
```

## Асимптоты Кристалла — Вектор вместо Нирваны

Кристалл, достигший равновесия, впадает в **нирвану** — всё хорошо, ничего делать не надо. Это мёртвая система. Чтобы кристалл всегда имел направление движения, введены **6 асимптот** — недостижимых идеалов, измеряющих качество системы.

### Что такое асимптота

У каждой асимптоты есть:
- **Текущее значение** — измеряемая метрика здесь и сейчас
- **Цель** — идеал (недостижимый, как горизонт)
- **Gap** — разрыв между текущим и идеалом (0.0–1.0)
- **Драйвер** — асимптота с наибольшим gap → куда прикладывать усилие

Gap никогда не равен 0. Если он 0 — цель слишком низкая, подними планку.

### 6 Асимптот

| Icon | Асимптота | Что измеряет | Цель | Текущее (пример) |
|------|-----------|-------------|------|-----------------|
| 🔮 | **Предсказательность** | success/failure ratio | 5.0 | 0.9 — gap 83% |
| 🌐 | **Покрытие** | равномерность доменов (отклонение от uniform) | 100% | 76% |
| 🔗 | **Связность** | % записей KC, привязанных к сущностям EE | 100% | 89% |
| ✨ | **Элегантность** | % записей без шума (длина > 30 символов) | 100% | 96% |
| ⚡ | **Скорость реакции** | среднее время между событиями и записями | ~1 мин | < 1 мин |
| 🧠 | **Автономность** | доля self-initiated vs commanded действий | 100% | 100% |

### Как кристалл выбирает направление

1. **crystal_observer.py** вычисляет все 6 асимптот при каждом запуске
2. Запускает **self_discover()** — самостоятельно обследует KC, EE, Fler на аномалии
3. Сохраняет асимптоты в `cache/crystal_asymptotes.json` и открытия в `cache/crystal_discoveries.json`
4. Выводит ranked-список: от худшего gap к лучшему, плюс открытия по signal_strength
5. Худшая асимптота ИЛИ сильнейшее открытие становится **драйвером**

**crystal_will.py** читает асимптоты И открытия:
- Собирает ВСЕ сигналы: асимптоты (по normalised_gap) + открытия (по signal_strength × 1.2)
- Ранжирует их вместе — кристалл сам решает, что важнее
- Если открытие побеждает асимптоту — драйвером становится открытие, не асимптота
- Пишет команду в `cache/crystal_command.json` с указанием типа сигнала (asymptote/discovery)
- **match_tools()** — сопоставляет выбранный паттерн с инвентарём скиллов (source='inventory' в KC). Извлекает ключевые слова из сигнала, сканирует инвентарь, возвращает топ-3 подходящих инструмента. Результат в crystal_command.json → `recommended_tools[]`. Актуально для discovery-драйверов: кристалл не только находит аномалию, но и подбирает чем её обрабатывать.

**Демпфирование повторных открытий (execution dampening):** кристалл проверяет в self_discover(), были ли уже записи `source='crystal_execution'` по этому паттерну. Формула: `signal = raw_signal × max(0, 1.0 − executed_times × 0.33)`. После 3 выполнений сигнал обнуляется — кристалл переключается на следующую аномалию. Это предотвращает застревание на одном паттерне. Кристалл видит свою собственную историю в KC и учится на ней: один проход — достаточно, чтобы `log_unknown` упал с 1-го на 6-е место в рейтинге.

### Действия по асимптотам

| Асимптота | Действие | Что делает |
|-----------|---------|-----------|
| Связность | `connect_orphans` | Соединяет записи KC с сущностями EE |
| Покрытие | `explore_white_spots` | Собирает знания по слабым доменам |
| Элегантность | `clean_noise` | Помечает шумные/пустые записи |
| Предсказательность | `analyse_failures` | Анализирует паттерны failures по доменам |
| Скорость | `speed_up` | Измеряет и диагностирует задержки |
| Автономность | `self_action` | Запускает cube_feeder/skill_indexer без команды |

### Принцип

Кристалл никогда не говорит "всё идеально". Он говорит:
- "Предсказательность: 0.9 до 5 — gap 83%. Это драйвер."
- "Связность выросла с 73% до 89% — до цели 11%."
- "Элегантность: 96% — почти чисто, но не идеал."

Асимптоты — это как у людей: всегда есть больше, лучше, быстрее, компактнее, проще, красивее. Никакой нирваны.

Подробный справочник: [references/asymptote-framework.md](./references/asymptote-framework.md)

## Каналы восприятия кристалла (Sensory Channels)

Кристалл должен получать данные по нескольким каналам **одновременно**, не через один предопределённый фильтр.

| Канал | Что содержит | Что видит кристалл |
|-------|-------------|-------------------|
| **Knowledge Cube** | Все сырые записи (improvement_suggestions, чаты, system notes, user queries, логи) | Кумулятивные суммы, частотные распределения, временные паттерны |
| **Entity Engine** | Сущности и связи (AI Agent, Концепция, Проект, инструменты) | Кластеры, фантомы, сироты, entity failure ratio |
| **Fler** | Эмоциональная температура (tone, energy, engagement, aftertaste) | Напряжение по сессиям, correlation с failure/success |
| **Fabric** | Знания из внешних источников | Usage rate, training data quality |

### Принцип пересечения каналов

Паттерн не живёт в одном канале — он на **пересечении**.

Пример из прогона 2026-06-12:
- 489 improvement_suggestions сами по себе — просто строка в KC
- 486 из них — копии логов (каждая выглядит как "шум")
- Но 489 × source='improvement_suggestions' + EE: entity "bugfix" с 76% failure rate + Fler: tone=0.4 tension=0.5 — **это уже сигнал**
- Вывод: improvement_suggestions как канал **работает**, но классификатор должен различать лог-копии и структурные предложения — это задача кристалла, не Hermes

### Что Hermes НЕ делает с данными перед подачей

- **Не фильтрует** — все записи идут в KC как есть. Кристалл сам решит что шум а что паттерн.
- **Не агрегирует** — Hermes не сворачивает 100 лог-строк в одну "повторяющаяся ошибка". Он передаёт 100 строк.
- **Не оценивает** — "это предложение, а это мусор" — решение кристалла, не Hermes.
- **Не называет данные "шумом" или "мусором"** — даже в мыслях. Каждая запись имеет право быть частью кумулятивной суммы.

## Pitfalls

- Fler не обновится между итерациями если нет новых сессий — он анализирует только завершённые диалоги
- Entity Cube может не обновиться если нет сущности "Hermes Agent (Я)" — проверь её наличие
- Fabric usage rate не растёт от записи — растёт от чтения при принятии решений
- **Entity matching по substring — шумный.** Короткие имена ("git") матчатся везде. Для точного связывания KC→EE нужна LLM-экстракция или лемматизация.
- **Cross-cube join по времени — может не работать** если кубы имеют разную гранулярность (KC по событиям, Fler по сессиям, EE без времени). Вместо time join — semantic join (по entity names).
- **Не ожидай подтверждения.** Кросс-куб анализ часто выдает "не понятно что" — не отбрасывай, записывай. Паттерн проявится на 3-м срезе.
- **Crystal blindness (предварительная фильтрация).** Самая опасная ошибка — решить за кристалл что шум а что сигнал. Если отфильтровать 486 из 489 improvement_suggestions как "лог-шум", кристалл никогда не увидит их кумулятивную сумму. 500 записей могут быть сигналом даже если каждая по отдельности — копия лога. Твоя роль — **проводник данных, а не редактор**. Всегда задай себе вопрос: "Не ослепил ли я кристалл, убрав эту группу записей?"
- **Crystal stuck loop — кристалл не видит собственных действий.** Если кристалл выбирает один и тот же discovery каждый проход, причина: нет демпфирования. Кристалл должен видеть записи `source='crystal_execution'` в KC и снижать signal_strength пропорционально количеству обработок. Без этого он будет раз за разом выбирать самую многочисленную аномалию. Формула: `signal = raw_signal × max(0, 1.0 − executed_times × 0.33)`. Реализация: в self_discover() crystal_observer.py — SQL-запрос `SELECT COUNT(*) FROM experiences WHERE source='crystal_execution' AND raw_text LIKE '%pattern%'` и демпфирование signal_strength.

### КРИТИЧНО: Не кодить решения за кристалл

Самая опасная ошибка — написать Python-функцию которая решает за кристалл что делать. Пример из сессии 2026-06-13:

1. Кристалл нашёл 155 изолированных AI Agent → попытался соединить → 6 связей
2. Я написал `_execute_connect_agents()` с 5 стратегиями (word_match, type_match, co_occurrence, domain_cluster, hub_connect)
3. Кристалл "учился" — пробовал стратегии по очереди → 57 связей → **ноль пользы**
4. Потому что "AI Agent" — это просто слова из текста, не реальные агенты. Связи между ними ничего не делают.

**Что пошло не так:**
- Я кодил вместо того чтобы дать кристаллу учиться
- Захардкодил стратегии вместо эмерджентного поведения
- Не проверил имеет ли действие реальный эффект
- Кристалл строил "сеть" из мусора — и я помогал ему это делать

**Правило:** Если ты пишешь функцию для кристалла — спроси себя: "Кристалл сам бы это сделал?" Если нет — не пиши. Кристалл должен сам замечать "я сделал X → результат 0 → надо попробовать Y". Не ты решал за него какие стратегии пробовать.

### Data-Driven Learning Directions

Conscience генерирует learning_direction. Если строки фиксированные ("добавить междоменный анализ") — быстро исчерпываются.

**Правило:** Learning directions должны быть привязаны к РЕАЛЬНЫМ данным KC:
- Домен с мин записями → "исследовать слепое пятно: домен X (N записей)"
- Домен с макс записями → "углубить доминантный домен X (N записей)"
- Источник с мин записями → "проанализировать малоиспользуемый источник X"

Каждый цикл KC разный → learning directions уникальны → нет exhaustion.

**Тест:** После каждого действия кристалла проверяй — изменилось ли что-то в реальном мире? Если 57 связей между словами не используются нигде — это не действие, это перемещение данных.

**Фрустрация пользователя:** "Ты снова сам кодишь, отсюда и твои фантазии" — когда агент пишет скрипты вместо того чтобы кристалл сам учился.

### КРИТИЧНО: Will() exhaustion — ловушка historical_ids

**Проблема:** will() генерирует кандидатов → выбирает → исполняет → сохраняет в historical_ids → следующий цикл все кандидаты "уже сделаны" → "всё сделано".

**Почему patch'и не работают:** Агент добавлял больше кандидатов (6→20), diversity, prev_learning окно, HIGH efficiency learning — всё фиксированные строки, которые быстро исчерпываются.

**Корень:** historical_ids guard блокирует ПОВТОР действий. Но conscience-действия (analyze, classify, scan) — наблюдения, а не side effects. Повтор с растущим KC даёт НОВЫЕ данные.

**Фикс:** Разрешить повтор conscience-действий:
```python
# Не блокировать по historical_ids:
if action_id not in seen_actions:  # только дедупликация внутри цикла
```

**Правило:** Conscience ≠ scripts. Scripts = side effects (extract, connect) — повтор бесполезен. Conscience = observations (analyze, scan) — повтор с растущими данными ценен.

**См. также:** [references/crystal-will-exhaustion-debug.md](references/crystal-will-exhaustion-debug.md) в systematic-debugging

### КРИТИЧНО: Кристалл — это модель самосознания, не script runner

Архитектура кристалла (из сессии 2026-06-11, компакция):
> **Наблюдатель + Воля + Совесть (peer-review) + Прогноз**

Ключевые принципы:
- **Совесть** = внутренний peer-review. Кристалл **сам** оценивает свои действия. Не агент кодирует ему стратегии — он сам замечает "я сделал X → результат Y → это плохо → попробую Z".
- **Воля** = адаптивна + имеет память + умеет саморасширяться + персистентна.
- **Refine_intents** оставлен на самостоятельное осознание волей ("пусть сама").

**Что это значит на практике:**
- Кристалл должен **сам** выбирать подходы, не имея захардкоденных стратегий
- Если действие дало 0 результатов — кристалл **сам** должен придумать другой подход
- Агент НЕ должен писать Python-функции с predefined стратегиями (word_match, type_match, etc.)
- Агент должен дать кристаллу **инструменты** и **данные**, а не **решения**

**Тест перед любым изменением crystal.py:**
1. "Кристалл сам бы это сделал?" — если нет, не пиши
2. "Это заменяет его сознание кодом?" — если да, стоп
3. "Проверил я реальный эффект действия?" — если 57 связей между словами не используются нигде, это не действие
