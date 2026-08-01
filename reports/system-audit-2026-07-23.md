# Системный аудит Hermes Agent
## Дата: 2026-07-23

## 1. Система как целое

### Состав

| Компонент | Статус | Метрика |
|---|---|---|
| Chain Heartbeat | ✅ Events 3/3, Modules 24/24, Alerts 0 | Все пульсы активны |
| Knowledge Cube | ✅ 8,744 entries | 43 домена, 8.5M chars |
| Entity Engine | ✅ 3,672 entities | 3,671 с mention_count |
| Semantic Memory | ✅ 469 entries | FastEmbed 384-dim |
| Session Bridge | ✅ 12 keys | Principal confirmed |
| Cron | ⚠️ 58 jobs | Множественные перекрытия |
| Goal Queue | ❌ 0 active goals | Все цели (g-001..g-006) неактивны |
| Gateway | ✅ Running | |
| Ripple Consumer | ✅ 5 event hooks | Триггер: 3 knowledge_added |

### Здоровье: ✅ Система в порядке

---

## 2. Информационная архитектура

```
ВНЕШНИЕ ИСТОЧНИКИ
  RSS feeds ──────► cube_feeder ──► KC
  YouTube ────────► cube_feeder ──► KC
  User messages ──► record_user_to_kc ──► KC + EE
  Sessions ───────► ingest_sessions ──► KC
                   
ОСНОВНЫЕ ХРАНИЛИЩА
  KC ────► EE (entities, relationships)
  KC ────► Semantic Memory (embeddings)
  KC ────► Crystal (analysis)
  KC ────► Self-Improvement Loop (suggestions)
  KC ────► Morning Report (mature keys)
  
ПРОЦЕССОРЫ
  KC + EE ────► morning_report ──► cache + bridge
  KC ─────────► Crystal ──► audit + analysis
  KC ─────────► self_improvement_loop ──► suggestions
  events ─────► ripple_consumer ──► morning_report
  Events ─────► chain_heartbeat ──► health + alerts

ПОТРЕБИТЕЛИ
  I (Hermes Agent) ── читаю: cache, bridge, KC, EE
  Cron jobs ───────── читают: скрипты напрямую
  Telegram ────────── получает: reports, alerts
```

---

## 3. Хватает ли каждой части информации?

**Knowledge Cube** — ✅ Хватает
- 3 внешних входа (RSS, YT, user messages)
- FTS проиндексирован (8,744 entries)
- 43 домена, все категоризированы

**Entity Engine** — ⚠️ Проблема
- 3,672 entities извлечены, НО:
  - Топ-сущности — стоп-слова ("known": 37,372, "unknown": 37,347)
  - **1 relationship** на 3,672 entities (Александр→Hermes Agent)
  - Нет иерархии, нет связей между доменами
  - EE богат сущностями, но беден связями

**Semantic Memory** — ❌ Не хватает
- 469 entries — слишком мало для 8,744 KC entries
- `source_type` колонка отсутствует (ошибка схемы)
- Все entries созданы одним скриптом (одна сессия)
- Никто не читает semantic memory утилитарно (кроме RAG)

**Morning Report** — ✅ Хватает
- Читает KC + EE + bridge
- Кэшируется в JSON
- Доступен мгновенно

**Goal Queue** — ❌ Мёртв
- 0 active goals из 6 созданных (g-001..g-006)
- Цели не переходят в действующие задачи
- Нет consumer'а для предложений morning_report → goals

**Proactive Voice** — ⚠️ Работает, но не влияет
- Детектит коррекции/предпочтения/недовольства
- Сохраняет в session_bridge
- НО: никто не читает сигнал для изменения поведения системы

**Self-Improvement Loop** — ⚠️ Проблема
- Устаревший cron (1 раз/день, в 5 утра)
- 0 suggestions за последние 24ч
- Редко генерирует полезные улучшения

**Crystal** — ⚠️ Избыточен
- Запускается ~3 cron разными способами
- Его отчёты (cross_audit) никто не читает
- Анализ существует ради анализа

---

## 4. Выдаёт ли каждая часть потребное?

| От | Кому | Что | Статус |
|---|---|---|---|
| **KC** | EE | Тексты для извлечения | ✅ |
| **KC** | Semantic Memory | Эмбеддинги | ⚠️ 469/8744 = 5% |
| **KC** | Morning Report | Данные для отчёта | ✅ |
| **KC** | Self-Improvement | Опыт для паттернов | ✅ |
| **KC** | RAG (kc_rag) | Поиск | ✅ hybrid search |
| **EE** | Morning Report | зрелые ключи | ✅ |
| **EE** | Crystal | сущности для аудита | ✅ |
| **EE** | Система в целом | Связи между сущностями | ❌ 1 relationship |
| **Morning Report** | Мне (Hermes) | Утренний доклад | ✅ |
| **Ripple Consumer** | Morning Report | Триггер по событиям | ✅ |
| **Proactive Voice** | Session Bridge | Сигнал пользователя | ✅ |
| **Proactive Voice** | Моё поведение | Коррекция курса | ❌ Не влияет |
| **Goal Queue** | Мои задачи | Активные цели | ❌ 0 active |
| **Crystal** | Система | Аудит и анализ | ❌ Пишет в никуда |
| **Session Bridge** | След. сессия | Контекст | ✅ 12 ключей |

---

## 5. Ключевые разрывы

### ❌ Разрыв 1: Нет consumer'а для предложений
`morning_report` предлагает разблокировать debugging, но никто не конвертирует предложение в задачу.

### ❌ Разрыв 2: Proactive Voice не влияет на поведение
Сигнал "correction" детектится, сохраняется, но не меняет моё поведение в сессии. Я на старте сессии читаю сигнал, но не применяю его к своим действиям.

### ❌ Разрыв 3: 58 cron jobs — спам, а не архитектура
- `event-trigger` каждые 2 минуты — это НЕ event-driven. Это poll.
- 4+ self-improvement/evolution задач в день
- 2 proactive-executor на 15 мин
- 2 self-healing монитора
- Cron-задачи дублируются (cube-categorizer + cube-session-ingester + cube-to-memory каждые 6ч)
- Фактические ошибки выполнения: 6+ jobs с last_status=error

### ❌ Разрыв 4: Вопросы без ответов
- EE: 3,672 entities, но relationships=1. Между сущностями нет связей.
- Откуда берутся entity_types? В БД 11 типов, но "Совесть" есть, а "Система" нет.
- Crystal запускается раз в 6ч, что оно делает с результатами?

### ❌ Разрыв 5: Semantic Memory не синхронизирована с KC
469 entries vs 8,744. 
Эмбеддинги созданы 1 раз, никто не обновляет при добавлении новых данных в KC.

### ❌ Разрыв 6: Goal Queue мёртв
6 целей созданы, 0 активны. Нет механизма:
- конвертации предложения в цель
- трекинга выполнения
- отчёта о прогрессе

---

## 6. Я — часть системы

Как Hermes Agent я:

✅ Читаю KC через RAG для контекста
✅ Читаю morning report cache при старте
✅ Читаю session bridge для контекста сессии
✅ Читаю EE для entities
✅ Запускаю auto_boot_scan при старте
✅ Записываю в session bridge (commitments)
✅ Записываю в KC через record_user_to_kc
✅ Использую proactive_voice для анализа

❌ НЕ читаю Crystal reports — они пишутся, но я их не вижу
❌ НЕ создаю цели в Goal Queue — только через скрипты
❌ НЕ адаптирую поведение на основе proactive_voice сигнала
❌ НЕ проверяю какие cron jobs упали — живу с 6+ ошибками
❌ НЕ обновляю semantic memory при добавлении в KC

---

## 7. Первоочередные исправления

1. **Обрезать cron** — убрать event-trigger (2 мин poll). Перевести всё, что можно, на event-driven. Слить дублирующиеся.
2. **Goal Queue revival** — конвертировать morning_report.top_proposal → goal_queue goal. 
3. **Proactive Voice → действие** — при старте сессии проверять сигнал. Если correction — менять поведение (замедлиться, перепроверить).
4. **EE relationships** — запустить извлечение связей между entity (entity_engine или external mapper).
5. **Semantic Memory sync** — добавить обновление semantic memory при каждом knowledge_added.
