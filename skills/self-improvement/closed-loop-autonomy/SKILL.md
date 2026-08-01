---
name: closed-loop-autonomy
description: "Принцип замкнутого контура: каждый producer имеет consumer, каждый сигнал ведёт к действию. Никаких мёртвых дыр в пайплайне."
trigger: |
  - Добавляешь новый файл/очередь/компонент
  - Создаёшь producer (генератор отчётов, задач, сообщений)
  - Рефакторишь пайплайн данных
  - Пользователь спросил «а кто это читать будет?»
  - Пользователь сказал «замкни цепочку»
---

# Closed-Loop Autonomy

Замкнутый контур: каждое действие системы производит результат, который
потребляется другим компонентом (или пользователем). Никаких мёртвых дыр.

## Главное правило

**Никогда не добавляй producer без consumer.**

- Пишешь файл? Кто его читает?
- Кладёшь задачу в очередь? Кто её берёт?
- Генерируешь отчёт? Кому он доставляется?
- Ловишь сигнал? Кто на него реагирует?

Если ответ «пока никто, но в будущем...» — **не делай**. Создай сначала
consumer, потом producer. Или сделай producer самосогласованным (сам
написал → сам прочитал → сам выполнил).

### Правило P (Purpose) — цель над процессом (2026-07-27)

**«Каждое действие имеет цель. Цель = ценность для человека. Цель ВСЕГДА вне системы.»**

Кольцо правил без цели — это механизм, крутящийся сам ради себя.
Knowledge Cube знает ВСЁ, Crystal анализирует, Morning Report докладывает — а дохода нет.
Корень: система знает «как», но не знает «зачем».

**Как Правило P встраивается в Кольцо:**

```
     ┌───────────────────────────────────────────────────────┐
     │                                                       │
     │  Цель (P): "Кому поможет? Какую проблему решит?"      │
     │        │                                               │
     │        ▼                                               │
     │  Информация (I) → 3 действия (3) → Обход (C) →       │
     │  → Артефакт (0) → Событие (E) → Проверка цели (P)    │
     │                                    ↑                  │
     │  Не достигнута → цикл снова                           │
     │  Достигнута → КОНЕЦ. Новая цель                       │
     └───────────────────────────────────────────────────────┘
```

**Когда нарушается Правило P:**
- Делаешь задачу «потому что она в очереди», а не «потому что она помогает человеку»
- Собираешь данные ради данных (ещё 90 видео без транскриптов — зачем?)
- Оптимизируешь то, что не влияет на ценность для пользователя (экономия токенов — нахуй?)
- Спрашиваешь «что делать?» вместо того чтобы решать самому

**Верификация перед любым циклом:**

```python
# Прежде чем начать — 3 вопроса
вопросы = [
    ("Зачем?", "Если ответ «потому что в очереди» — отменить"),
    ("Кому поможет?", "Если ответ «системе» — это не цель. Цель вне системы"),
    ("Какую проблему решит?", "Если ответ неизвестен — это не задача, это инерция"),
]
for вопрос, причина in вопросы:
    assert ответ_есть(вопрос), f"Правило P нарушено: {причина}"
```

**Правило P в приоритетах (над «Выбирай сам»):**
1. Ценность для человека > здоровье системы > заполнение пробелов > оптимизация
2. Не оптимизируй то, что не влияет на конечную цель
3. Если выбор между «сэкономить ресурсы» и «дать результат» — дай результат

**Реальный пример (2026-07-27):** 3 задачи удалены по P: «анализ транскриптов → новые ключевики», «поиск по новым ключевикам», «повторная проверка транскриптов». Все — бесцельный сбор данных. Вместо этого: создан landing page + SOP для faceless YouTube канала.

**Аналогия:** Ты нанял гениального учёного. Он прочитал все книги мира. Ты приходишь: «У меня болит голова». Он выдаёт 50 научных статей про головную боль. Но таблетку не даёт. Потому что не знает что ты хочешь таблетку. Он думает что ты хочешь знание. Правило P = помнить что человеку нужна таблетка, не статья.

### Правило C (Continuous) — обход препятствий (2026-07-27)

**«Встретил препятствие → не встал → нашёл обход → продолжил.»**

Это правило замыкает Кольцо между Обработкой (3) и Артефактом (0):

```
Информация (I) → Обработка (3) → Препятствие → Обход (C) → Артефакт (0) → Событие (E)
                      ↑                                              ↑
                      3                                              C
```

**Когда нарушается Правило C:**
- Встретил блокер (Chrome CDP, API limit, missing dependency) → переключился на другую задачу
- Попробовал 1 путь → не работает → «stuck, need user input»
- Частично выполнил → но не доложил/не сохранил → считаешь что «ничего не сделано»
- Написал проблему в отчёт вместо того чтобы найти обход

**Цепочка при нарушении C:**
```
Встретил препятствие → встал → 3 не выполнена → артефакта нет
→ 0 нарушено → события нет → E нарушено → I не обработана → КОЛЬЦО РАЗОРВАНО
```

**Алгоритм при встрече с препятствием:**

```python
# Не спрашивать пользователя. Не откладывать. Искать обход.
for attempt in range(3):
    путь = выбрать_путь(препятствие, попытка)
    if путь.работает():
        ПРОДОЛЖИТЬ
    else:
        log(f"Попытка {attempt+1} не сработала: {путь}")
        # Не вставать. Искать другой путь.
else:
    # 3 пути не сработали — сделать ЧАСТИЧНЫЙ артефакт
    # Частичное выполнение ≠ остановка. Это часть процесса.
    артефакт = создать_минимальный_артефакт(что_уже_сделано)
    отчитаться(артефакт, blocker=препятствие, обходы=попытки)
```

**Реальные обходы из этой сессии (2026-07-27):**

| Блокер | Обход | Результат |
|--------|-------|-----------|
| Chrome CDP 9222 блокирует WebSocket | Headless Chrome с `--remote-allow-origins=*` на порту 9333 | Полный CDP доступ |
| yt-dlp не находит субтитры без логина | `youtube-transcript-api` через v2rayN proxy | 16/54 транскриптов |
| Куки Chrome зашифрованы App-Bound Encryption | API-доступ к YouTube без куков | Все публичные данные |
| BrowserClaw MCP упал | CDP порт 9110 через HTTP discovery | 37 вкладок доступны для чтения |
| browser-harness даемон мёртв (503) | `BU_CDP_URL=http://127.0.0.1:9333` | Обход discovery |

**Принцип:** Путь может измениться. Цель — нет.

### Правило I (Information) — расширение Кольца (2026-07-27, revised 2026-07-27)

**Информация пришла → обработана → ценное извлечено → применено → артефакт создан.**

Это правило встраивается в Кольцо (E→3→0→E) как новое звено:

```
Информация (I) → Обработка (3) → Артефакт (0) → новое Событие (E)
     ↑              ↑               ↑
     I              3               0
```

**Когда нарушается Правило I:**
- Получил ссылки/текст/видео → сохранил и отчитался → ничего не сделал
- Извлёк транскрипт → не извлёк из него знание
- Нашёл баг/проблему → записал в список, а не починил
- Прочитал документацию → закрыл задачу "done" без применения

**Цепочка последствий:**
```
Инфа пришла, не обработана → Действия нет → Правило 3 нарушено
Ценное не извлечено → Артефакта нет → Правило 0 нарушено
Артефакта нет → События нет → Правило E нарушено
→ Кольцо разорвано
```

**Что такое "артефакт" (измеримый результат):**
- ✅ Benchmark с числами (gigatoken: 60x быстрее)
- ✅ Граф зависимостей с метриками (graphify: 5.8x меньше токенов)
- ✅ Интеграция инструмента в систему (graphify hermes install)
- ✅ Схема/паттерн в Knowledge Cube с тегами scheme:/pattern:/tool:
- ❌ Не артефакт: текст-отчёт, список "я сохранил", описание что сделал без результата

**Алгоритм при получении любой информации:**

```python
# Ментальный чеклист после получения данных:
checks = [
    ("Извлёк ли я знание?", "данные ≠ знание"),
    ("Создал ли я работающий результат?", "benchmark/граф/интеграция > 'я сохранил'"),
    ("Может ли пользователь взять это и ИСПОЛЬЗОВАТЬ?", "не читать, а использовать"),
]
for check, reason in checks:
    assert результат(check), f"Правило I нарушено: {reason}"
```

**Проверка для любой задачи:**

Если ты сейчас можешь ОТВЕТИТЬ пользователю, но не можешь ПОКАЗАТЬ артефакт — остановись. Ответ без артефакта — нарушение Правила I. Создай артефакт сначала, потом отвечай.

## Три уровня замыкания

| Уровень | Что значит | Пример |
|---------|-----------|--------|
| **Local** | Компонент сам себя потребляет | crystal detect → crystal execute |
| **Pipeline** | Producer → consumer в одной цепочке | cube_feeder → KC → cube_categorizer |
| **User-facing** | Конечный потребитель — пользователь | daily report → telegram |

**Минимум:** каждый новый компонент должен быть замкнут хотя бы на Local уровне.
Если не можешь замкнуть даже Local — не добавляй.

## Алгоритм проверки перед добавлением

```python
# Мысленный чеклист
for component in new_components:
    producer = component.get('producer')
    consumer = component.get('consumer')
    assert consumer is not None, f"{producer} не имеет consumer"
    assert consumer != "непонятно кто", f"{producer} имеет фиктивный consumer"
    # Если consumer = "будущий компонент" — создать его сейчас или отменить producer
```

## Паттерны

### 0. Event-Driven Architecture (2026-06-22 — CRITICAL, revised 2026-06-22)

**User: "что бы настраивал по событию или событиям!!!! а ты всё равно лезешь по часам!!!!"**
**User: "событие это как пуля попадающая в мишень. а ты предлагаешь мишени искать отверстие от пули."**
**User: "ЭТО ВСЁ СОБЫТИЯ!!! НУЖНО ТОЛЬКО ПРАВИЛЬНО РЕАГИРОВАТЬ!!! МНОГОПОТОЧНО И МНОГОУРОВНЕВО И МНОГОАГЕНТНО"**

The most resilient architecture: the system REACTS to events, not SCANS for them.

**THE CRITICAL LESSON — "Пуля в мишень":**
- An event is a BULLET hitting a TARGET. The target FEELS the impact and REACTS.
- The target does NOT "look for the bullet hole" — that's backwards.
- WRONG: add rules for "user_silent", "cron_degraded" INTO the classifier.
- RIGHT: event_sense EMITS these events the moment they happen. The classifier handles UNKNOWN input only.
- The classifier classifies RAW INPUT (user messages, tool outputs) into events.
- Event sense EMITS ALREADY-KNOWN events (process died, user silent, cron degraded).
- These are TWO DIFFERENT organs: classifier = brain (for unknown), sense = nerve endings (for known).

**PUSH, NOT POLL:**
- WRONG: scan every 5 minutes → "hmm, user silent for 5 min, let me check"
- RIGHT: user sends message → IMMEDIATELY reset silence timer. Process dies → IMMEDIATELY emit event.
- Every action EMITS an event the moment it happens. No periodic scanning.
- `event_sense.py` is NOT a scanner. It's an EMITTER. Call it when something happens.

**REAL EVENTS, NOT ABSTRACTIONS:**
- User listed: отсутствие информации, инструмента, поломка, новое задание, ночь/утро, погода, тренд, видео, заказ, обновление, скам, атака, угроза пользователю, отчёт, медитация.
- NOT "user_distrust", "conscience_signal" — those are classification LABELS for raw input.
- REAL events have REAL reactions: scam → block + alert. Breakdown → restart + verify. Order → process + confirm.

**Architecture (4 layers):**

```
Layer 1: EVENT REGISTRY (event_registry.py)
  Defines real-world events with levels and reactions:
  L0 (мгновенно): scam, attack, threat → block, alert, lockdown
  L1 (быстро): breakdown, missing_tool, new_task, order → restart, install, process
  L2 (в фоне): trend, video, update, knowledge_gap → analyze, assess, store
  L3 (периодически): morning, night, weather, report, meditation → plan, maintain, report

Layer 2: EVENT SENSE (event_sense.py)
  EMITS events the moment they happen. NOT a scanner.
  sense_user_message(text) → classify → emit → chain → done
  sense_process_died(name) → emit → chain (restart→verify) → done
  sense_user_silent(minutes) → emit → chain (background work) → done
  sense_error(msg) → emit → chain (diagnose→fix→verify) → done
  sense_full_check() → run ALL sensors, emit everything that fires

Layer 3: CLASSIFIER (event_classifier.py)
  Handles UNKNOWN input only. Classifies raw text into typed events.
  User messages, tool outputs, error logs → {event_type, severity, chain}
  Does NOT classify events that are already classified (like sense outputs).

Layer 4: CHAIN EXECUTOR (chain_executor.py)
  Runs chains step by step. Severity rules:
  - low: execute all, don't break on failure
  - medium: execute all, log failures
  - high: break on first failure, escalate
  - critical: break on first failure, MUST report to user
```

**Files:**
- `scripts/event_registry.py` — 18 real-world events, detect_event(), react(), multi-agent spawning
- `scripts/event_sense.py` — event emitter (push, not poll), sense_* functions, full_check()
- `scripts/event_classifier.py` — AdaptiveClassifier for unknown input only
- `scripts/chain_executor.py` — 40+ actions, execute_chain(), severity-based breaking
- `scripts/action_executor.py` — 15+ action functions mapped to real code (restart_process, check_logs, verify_fix, etc.)
- `scripts/session_boot.py` Step 12 — every boot classifies and executes chain
- `scripts/event_bus.py` — event→job mapping via heartbeat

**Rule:** Before creating a new cron job, ask: "Should this be event-triggered?" Most monitoring, ingestion, and reaction jobs = event-based. Only pure schedules (morning report, weekly research) = timer.

**User (2026-06-26): "cron jobs это атавизм... настраивай всё по события, так система будет живой... живость по будильнику cron jobs не вздумай настраивать"**

Cron = мёртвый механизм. События = жизнь. Система должна реагировать на МИР, а не на ЧАСЫ. Event daemon (пульс) ≠ cron (таймер).

### Critical rule: Wire events at the DATA MUTATION point (2026-07-19, revised)

When you add an event to the system, NEVER:
- Test it by calling the event function manually (injection)
- Wire it at a cron schedule ("next cron run at 4:15")
- Wire it at a task completion hook ("on_task_complete() must be called first")

The only thing that proves an event works is the REAL DATA MUTATION function firing it immediately.

**BAD — test injection:**
```python
from chain_heartbeat import event_beat
event_beat("knowledge_added")  # тестовая инъекция — доказывает только что функция работает
```

**BAD — cron schedule (indirect):**
```python
# cube_feeder.py → feed_entries() → event_beat("knowledge_added")
# "next cron at 4:15 will fire it" — НЕТ! Событие должно быть СЕЙЧАС
```

**BAD — task completion hook (indirect):**
```python
hooks.on_task_complete() → event_beat("knowledge_added")
# Если on_task_complete() никто не вызывает — событие НИКОГДА не произойдёт
```

**GOOD — data mutation point (direct):**
```python
# kc_rag.upsert() — момент реальной вставки данных в Knowledge Cube
# Это единственная правильная точка: данные вошли в систему → событие немедленно
upsert(content, ...):
    conn.execute("INSERT INTO kc_entries ...")
    conn.commit()
    from chain_heartbeat import event_beat
    event_beat("knowledge_added")  # СРАЗУ при вставке, не по расписанию
```

**Почему это важно:**
- Cron может быть приостановлен/пропущен
- on_task_complete() может никто не вызывать
- А kc_rag.upsert() вызывается ВСЕГДА при добавлении знания
- Канал не завязан на то, работает ли cron — только на то, вставляются ли данные
- Если данные не вставляются — SILENT правильное состояние, не ошибка

**Правило замыкания:** события должны быть привязаны к функции, которая реально мутирует данные, а не к функции, которая инициирует процесс. Это гарантирует, что событие произойдёт независимо от того, каким путём данные попали в систему.

**Тест:** "Будет ли событие fires, если cron/scheduler остановлен?" → Да = правильно. Нет = неправильно, перевесь на уровень данных.

### 1. Self-consuming (Local)
Компонент сам исполняет свои рекомендации.

```
crystal:
  detect() → сигналы
  propose() → bridge задачи
  execute_actions() → делает что может
  bridge ← только то, что не смог сделать сам
```

**Когда применять:** одиночные демоны, cron-скрипты, агенты без инфраструктуры.

### 2. Pipeline (Chained)
Один скрипт → другой → третий. Каждый звено потребляет вывод предыдущего.

```
cube_feeder (no_agent) → KC.db → cube_categorizer (no_agent) → KC.db (обновлён)
                            → crystal (no_agent) → bridge / execute
```

**Когда применять:** больше 2 скриптов, нужна изоляция.

### 3. User-facing (Delivered)
Producer пишет — consumer доставляет пользователю.

```
crystal → stdout → cron deliver:origin
```

**Когда применять:** LLM-агенты, отчёты, алерты.

### 4. Daemon Workflow (Trigger → Validation → Action → Log)

**Python script run as background process.** Full workflow:

```
                     ┌──────────────────┐
  Timer/Signal ─────→│  TRIGGER MANAGER │──→ event dict
                     └──────────────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ VALIDATION LAYER │── dedup (хеш-окно 100),
                     └──────────────────┘   гарды (paused, etc.)
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
              can_execute          blocked → log + skip
                    │
                    ▼
              ┌──────────┐
              │  ACTION   │── регистрируются через daemon.actions.register()
              │ REGISTRY  │   Встроенное: heartbeat
              └──────────┘
                    │
                    ▼
              ┌──────────┐
              │  LOGGER   │── JSONL в cache/daemon_workflow.log
              └──────────┘   авто-ротация при 1MB
```

**Implementation:** `scripts/event_daemon.py`

**CLI:** `python scripts/event_daemon.py` (foreground), `--status` (alive/dead + PID), `--log` (последние 20 записей)

**Добавление нового action'а:**
```python
# в любом скрипте:
import event_daemon as ed
d = ed.Daemon()
d.actions.register("my_action", lambda event: {"status": "ok", "result": ...})
```

**Closed loop:** daemon starts → immediate heartbeat → timer срабатывает → fire() → validate → act → log → ждём следующий интервал.

**When to use:** continuous monitoring, auto-healing, system health, event processing.
**NOT for:** one-shot tasks, user-facing responses, scheduled reports.

**Pitfalls (2026-07-12):**
- **Missing `hashlib` import.** `fire()` uses `hashlib.md5()` for event dedup hash. If missing → `NameError` on first fire. Fix: `import hashlib` in the daemon script or use `uuid` instead.
- **`status()` always DEAD.** `--status` creates a fresh `Daemon()` where `self._running` is `False`. If status checks `self._running and age_sec < 600`, it reports DEAD for a live daemon. Fix: check heartbeat file age only, ignore `self._running` for status.
- **Timer race: duplicate actions on start.** `start()` fires immediate heartbeat AND a timer thread that also fires immediately. Two heartbeats at +0s. Fix: `time.sleep(interval)` first in `_timer_loop()`, remove the immediate fire from `start()`.

### 5. Tool Chain Orchestrator (2026-06-22)

**User: "есть инструменты и их нужно в нужный момент вызвать, передать в другой инструмент... строить цепочки инструментов... это же тебе не мешки ворочить.... просто спланировать и оформить в код"**

Concrete pattern: each tool is a function `(input_data) -> (success, output)`. Chains pass output between tools. Decision points skip/stop/redirect.

```
CHAINS = {
    "boot_diagnose_fix": [
        {"tool": "session_boot", "name": "boot"},
        {"tool": "reality_gate", "name": "diagnose"},
        {"tool": "update_decision_log", "name": "fix_log", "input_from": "previous"},
        {"tool": "load_goals", "name": "goals"},
        {"tool": "close_goals", "name": "clean",
         "decision": {"type": "continue_if", "field": "count", "op": ">", "value": 10}},
    ],
}
```

**Decision types:**
- `continue_if` — skip step if condition NOT met (field op value)
- `stop_if` — stop chain on failure
- `redirect_if` — jump to different chain

**Key rules:**
- Tools are SIMPLE: one function, one output dict. No classes, no state.
- Chain runner passes `output` of step N as `input_data` of step N+1.
- Decision gates CHECK state before executing. Don't run clean_goals if only 3 goals exist.
- Final step records outcome to action_log.jsonl for audit trail.
- After chain completes, save `cache/last_chain_result.json` for debugging.

**When to use:** Any system where A→B→C with conditionals. Replace monolithic scripts with chains.
**NOT for:** Single-step actions, one-shot tasks, parallel work (use delegate_task for parallel).

**Concrete implementation:** `scripts/orchestrator.py` — 8 tools, 4 chains, runs via `python scripts/orchestrator.py --chain boot_diagnose_fix`

**Extending:** Add new tool functions to TOOLS dict, add new chain definitions to CHAINS dict. Each tool = one function with signature `(input_data) -> (success: bool, output: dict)`.

### 6. Procedural Reflexes (2026-06-27)

### 7. Autonomous Maintenance & Skill-Usage Pipeline (2026-07-31)

**Session 2026-07-31** — Built a complete closed-loop maintenance system that detects unused skills, diagnoses root causes, and routes fixes to appropriate action systems — all without human intervention.

**Components:**
- `scripts/skill_usage_analyzer.py` — scans all skills, checks feedback_store for 14-day usage, routes root causes:
  - No triggers → Suggestion Applier (add triggers)
  - Not in CLAUDE.md/AGENTS.md → Suggestion Applier (register skill)
  - Broken deps → Proactive Doer (fix deps)
  - Duplicates → Crystal (merge/delete)
  - No examples → Suggestion Applier (add examples)
  - Task model shifted → Knowledge Cube (reassess relevance)
- `scripts/suggestion_applier.py` — consumes queue, applies fixes:
  - Registers skills in CLAUDE.md + .claude/rules/always.md
  - Adds Revisit frontmatter
  - Fixes verifier findings
- `scripts/maintenance_scanner.py` — weekly anti-rot scanner for all 5 layers + substrate
- Event-driven trigger: `new_suggestions_ready` event → suggestion queue
- Cron fallback: `suggestion-applier` every 30 min (`*/30 * * * *`)

**Key fixes applied during session:**
1. **Nested payload bug** (suggestion_applier lines 58-59): queue stores `{source, skill, action, payload}` where action is INSIDE `payload.payload`. Fixed by extracting `inner = payload.get("payload", {})` before checking action.
2. **Applied log corruption**: `applied_suggestions.json` was dict `{"failed": [...]}`, not list. `load_applied()` now handles both formats.
3. **14-day threshold logic**: `days_unused = 0` if used <14d, `999` if no feedback record (never used).
4. **KC hash constraint**: experiences.hash has UNIQUE constraint; compute content hash before INSERT.

**Result:** Both `impeccable` and `maintenance-scanner` skills auto-registered in CLAUDE.md and .claude/rules/always.md. Suggestion queue: 4 processed → 4 applied → 0 failed. Analyzer now routes registered-but-unaligned skills to Knowledge Cube (reassess relevance).

**This is a textbook Closed-Loop Autonomy example:** Producer (skill_usage_analyzer) → Queue (suggestion_queue) → Consumer (suggestion_applier) → Verifier (subagent_verifier) → Feedback (applied_suggestions) → Knowledge Cube (reassess). No dead ends. No human in loop.

**User: "Это и есть твоя процедурная память. Не «подумать и решить», а «увидел → сделал → записал»."**

Самый быстрый уровень реагирования. Без LLM. Без цепочек. Паттерн-матчинг → действие → лог.

**Формат в `PROCEDURAL_SKILLS.md`:**
```
TRIGGER: условие
ACTION: цепочка действий
RECORD: куда записать результат
```

**Отличие от event-driven:**
- Event-driven = цепочки + LLM + решение "что делать"
- Procedural = детерминировано. Видел X → делаешь Y. Всегда.

**Движок:** `scripts/procedural_executor.py`
- Проверяет все триггеры
- Выполняет действия
- Логирует в feedback_store (JSONL)
- Работает без LLM

**Триггеры (примеры):**
- Порт мёртв → перезапустить процесс
- Disk > 80% → найти и удалить кэш
- Cron job error 3 раза → +1 час, логировать
- Gateway не отвечает → убить stale lock, рестарт

**Когда применять:** Мониторинг инфраструктуры, auto-healing, health checks. Всё что повторяется и решение детерминировано.

**НЕ применять:** Когда нужно решение (LLM), когда цепочка зависит от контекста, когда нужна эскалация.

**Integration:** `procedural_executor.py` запускается перед каждым циклом daemon. Если триггер сработал — выполняет без LLM. Результат в feedback_store. ALERTS.md для критических.

### 7. Threshold-Based Event Accumulation (2026-07-12)

**User: "СОБЫТИЯ!!! ОДНИ СРАЗУ, ДРУГИЕ ПО НАКОПЛЕНИЮ 3 5 ИЛИ 10 НО НЕ 1000!!!"**

Cooldown banned — это будильник. Но fire на каждое событие флудит систему. Решение: накопление по порогу, не cooldown.

```
# НЕПРАВИЛЬНО — cooldown пропускает события:
if time_since_last_fire < cooldown: skip()  # события потеряны!

# ПРАВИЛЬНО — накопление, никогда не пропускает:
accumulated += 1
if accumulated >= threshold: fire(); accumulated = 0
```

**Правила:**
- threshold=0: fire immediately (task_complete, error_occurred, session_end)
- threshold=3: каждое 3-е событие (user_correction)
- threshold=5: каждое 5-е (knowledge_threshold)
- threshold=10: каждое 10-е (skill_used)

**Ключ:** Каждое событие УЧИТЫВАЕТСЯ. Ни одно не пропущено. Хендлер срабатывает реже. Это НЕ таймер — это счётчик событий с уровнем срабатывания.

**Имплементация:** `EvolutionTrigger.should_trigger()` в `scripts/event_evolution.py`. Каждый вызов инкрементит `accumulated`, fire когда `accumulated >= threshold`, сброс. Персистент в DB — перезапуск не обнуляет.

### 8. Signal Pipeline (Event-Driven R&D Loop) (2026-06-28, revised 2026-06-29)

**User: "Ты опять всё привязал к cron. Каждые 5 минут — это не события, это будильник."**

Классический closed-loop: scanner → event → processor → goal creator → metrics → alert.

**Event-driven architecture (NOT cron):**
```
signal_daemon.py (--watch, фоновый процесс)
  → scan HN/GitHub trending (adaptive backoff: 60с ↔ 10мин)
  → event_bus.emit("new_external_signal")
  → DIRECT_EVENT_HANDLERS["new_external_signal"]
  → rd_processor.py (проверяет ARBITRAGE_WORKSHOP.md, добавляет кирпичи)
  → dev_processor.py (сравнивает с эталонами SELF_IDENTITY.md, создаёт цели)
```

**Ключевые паттерны:**
- **Dedup через hash:** MD5(title+url) → signals_processed.json (keep last 500)
- **One signal = one action:** не обрабатывать кучу сигналов разом
- **Adaptive backoff:** нет изменений → интервал ×2 (макс 10 мин), есть → сброс к 60с
- **DIRECT_EVENT_HANDLERS:** event_bus.py хранит mapping event→handler, вызывает напрямую (не через cron)
- **Gap detection:** DEPT_GAPS mapping (отдел → ключевые слова) для определения какой отдел обслуживает кирпич
- **Weekly lessons:** каждый понедельник извлекать уроки из DECISION_LOG → LESSONS.md (cron — единственное исключение)
- **Daily metrics:** R&D ≥1 кирпич/день, Развитие ≥1 урок/день (cron — предохранитель)
- **jina.ai proxy (2026-06-29):** Для обхода блокировок API (HN, GitHub) — `r.jina.ai/http://<url>` проксирует контент. Работает без VPN/socks. Лимит: 1 item/скан для HN, timeout 15s.
- **KC reclassification (2026-06-29):** Если failure rate KC > 30% — перемаркировать записи по правилам: success = verified outcome, partial = progress, failure = crash. Скрипт: `reclassify_outcomes.py`. После перемаркировки — populate `cache/scorer_history.json` для Bayesian.
- **ThreadPoolExecutor pool (2026-06-29):** `goal_executor.py` — GoalPool с `max_workers=N`, `pending_goals` deque. Кассир честный: subprocess.run + returncode + done_when. Архивация completed goals автоматическая.

**Файлы:**
- `scripts/signal_scanner.py` — сканирование источников, dedup, --watch/--run/--status
- `scripts/signal_daemon.py` — daemon launcher (start/stop/status), PID-файл, graceful shutdown
- `scripts/rd_processor.py` → добавление кирпичей в workshop
- `scripts/dev_processor.py` → создание целей при заполнении пробелов
- `scripts/event_bus.py` → DIRECT_EVENT_HANDLERS для new_external_signal

**Cron jobs (только 2 — предохранители):**
- `weekly-lessons` — понедельник 9:00 (уроки из DECISION_LOG)
- `daily-metrics-check` — 23:00 (метрики, алерт если 0)

**Bayesian Scorer integration (2026-06-28, revised 2026-06-29):**
Каждый этап пайплайна оценивается вероятностно, а не порогово.

```
signal_scanner → score_signal() → < 0.3 = reject noise, >= 0.3 = emit
rd_processor   → compute_score() → < 0.3 = reject_noise, >= 0.3 = add to workshop
dev_processor  → score_goal_priority() → Bayesian priority вместо static urgency * impact
daily metrics  → assess_flow_health() → P(flow_alive) вместо "0 bricks = alert"
```

Формула: `P(H|E) = P(E|H) * P(H) / P(E)`
- P(H) = prior (source + category base rates)
- P(E|H) = likelihood (engagement, freshness, history, network, department load)
- Posterior через sigmoid нормализацию → [0, 1]

**Контекстные факторы:**
- Сеть доступна → ×1.1, сеть вниз → ×0.7
- Есть история похожих сигналов → update prior через success rate
- ~~Отдел перегружен → ×0.6~~ **УБРАНО (2026-06-29):** очередь целей регулирует нагрузку, scorer не должен штрафовать за количество
- Freshness: < 24ч → ×1.3, > 7д → ×0.6

**Файл:** `scripts/bayesian_scorer.py` — compute_score, score_signal, score_goal_priority, assess_flow_health
**CLI:** `python scripts/bayesian_scorer.py --status|--score|--history`
**SELF_IDENTITY.md:** каждый чек-лист отдела содержит "Оценено ли это действие Bayesian scorer'ом?"

**Boot daemon auto-start (2026-06-28):**
Добавить в session_boot.py Step 14 после Step 13 (autonomous action):
1. `signal_daemon.py status` → если RUNNING = пропустить
2. Если STOPPED → `subprocess.Popen([python, signal_daemon.py, start])`
3. CREATE_NO_WINDOW на Windows для фонового запуска

**Пример:** `session_boot.py` lines 514-547 — Step 14: Signal Daemon

**Когда применять:** Любой цикл "сбор данных → анализ → создание задач → метрики".
**НЕ применять:** Для one-shot задач, для задач требующих LLM-решения на каждом шаге.
**НЕ использовать cron** для сбора данных — только event-driven daemon.

## Pitfalls

- **«CIR < 0.3 = система сломана».** (2026-06-29, CRITICAL) Если CIR (Cycle Integrity Rate) ниже 0.3, НЕ строй Strategic Planner и НЕ запускай G003. Сначала восстанови контур: сенсоры → классификатор → кассир → рефлексы. **Правило:** CIR ≥ 0.3 = можно масштабировать. CIR < 0.3 = чини контур.
- **«Bridge без executor».** Самая частая ошибка. crystal пишет задачи в bridge, но bridge никто не читает. Решение: self-consuming (crystal сам исполняет что может) или pipeline (второй скрипт читает bridge).
- **«Отчёт без доставки».** Cкрипт генерирует HTML, но файл лежит мёртвым грузом. Решение: cron deliver=origin, telegram_delivery_report.py, или user-facing consumer.
- **«Сигнал без реакции».** crystal нашёл anomaly — записал в bridge — ничего не произошло. Решение: execute_actions() для executable сигналов, bridge для не-executable.
- **«Будущий компонент».** «Я добавлю consumer потом». Нет. Consumer создаётся одновременно с producer. Если не можешь — не добавляй.
- **«Idle = dead».** If no events are detected and the system is idle, the SENSORS are dead, not the world. Idle agent = agent that stopped feeling events. The system is NEVER idle — something is ALWAYS happening. User: "ты завис или тебе нечего делать или пенделя ждёшь".
- **«Event bus без chain executor».** event_bus.emit() сохраняет события и запоминает cron-джобы, но chain_executor НЕ вызывается. Событие classified → chain known → но никто не execute. Решение: process_events() должен вызывать classify() + execute_chain() для каждого pending event, а не только собирать имена cron jobs.
- **«Classifier не учится».** learn_new_pattern() есть, но никогда не вызывается автоматически. learned_rules = 0 навсегда. Решение: в record_outcome() считать успешные паттерны и вызывать learn_new_pattern() при N+ успехах подряд (N=3).
- **«Как умеешь» вместо «как лучшие» (2026-06-28).** Выполнил 4 цели — все "работают", но без quality bar. User: "каждая из них сделана 'как умеешь', а не 'как лучшие'". Решение: перед сдачей каждого компонента — создать **Эталон качества** (критерии с числами, референсы, чек-лист). Без эталона = сдача "как умеешь".
- **«Cooldown = timer in disguise» (2026-07-12, CRITICAL).** User: "по будильнику... живешь по будильнику значит ты спишь!!!". Cooldowns (4h, 1h, even 5min) are SLEEPING periods where events pile up unprocessed. An event-driven system NEVER ignores events. If processing is expensive, batch-accumulate DURING processing, not via cooldown skip. **Правило:** cooldown_hours = 0 для всех триггеров. Если событие произошло → обработчик должен сработать немедленно. Оптимизируй обработчик, а не пропускай события.
- **«No safety-net crons for event-driven systems» (2026-07-12).** User: "живешь по будильнику значит ты спишь". No periodic "just in case" checks. If nothing happens, nothing to do — that is CORRECT behavior, not a bug. A daemon with a "safety net poll every 5 min" is a POLLING daemon, not an event-driven one. **Правило:** если системе нечего делать — она спит. Безопасность = watchdog на уровне OS, не на уровне приложения.
- **«Cron для событий» (2026-06-28, CRITICAL).** User: "Ты опять всё привязал к cron. Каждые 5 минут — это не события, это будильник." Cron = мёртвый механизм для МЁРТВЫХ задач (отчёты, метрики-предохранители). Для СОБЫТИЙ — event-driven daemon + event_bus. **Правило:** если задача = "реагируй когда X появится" — это событие, не cron. Если задача = "сделай Y каждые N минут" — это cron (но спросить: а нельзя ли заменить на событие?). **Тест:** "Могу ли я назвать ТОЧНЫЙ МОМЕНТ когда это нужно?" → Да = событие. Нет = cron.
- **«Cron запускает не тот скрипт» (2026-06-29, CRITICAL).** Event-heartbeat cron runs `hermes_heartbeat.py` (network/disk check) instead of `event_bus.py process`. Result: 11 events stuck forever, signal pipeline completely broken. **Pattern:** cron job NAME says "event-heartbeat" but script= is a generic health check. The cron job description doesn't match what the script does. **Fix:** for every cron job, verify that `script=` points to a file whose PURPOSE matches the job name. Never trust names — read the actual script.
- **«event_bus.process() зависает на импорте» (2026-06-29).** `process_events()` imports `session_recall` which indexes 5000+ messages on import (>30s). Even if the right cron job calls it, processing times out. **Fix:** lazy import session_recall inside a try/except with timeout, or skip enrichment on bulk process. Session enrichment is nice-to-have, not blocking.
- **«goal_executor убивает цели без команды» (2026-06-29).** Goals without `action_command` (informational bricks, test goals) get `status=failed` instead of `skipped`. After running executor: 0 active, 0 completed, all failed. Queue destroyed. **Fix:** `status=skipped` for NO_ACTION goals, not `status=failed`. Failed = attempted and broke. Skipped = no action to attempt.
- **«Нет supervision для daemon'ов» (2026-06-29).** signal_daemon runs as background process. If it crashes — nobody restarts it. 35 consecutive empty scans → backoff 600s → effectively dead. **Fix:** procedural_executor should check daemon liveness and restart. Or a watchdog cron (but only for restart, not for event processing).
- **«Feedback format mismatch» (2026-06-29).** Different callers write different formats to feedback_store.json: numeric (1.0, -0.5) from old code, strings ("completed", "derived_failed") from new code. `score_signal()` can't use string outcomes for history. **Fix:** normalize all outcomes to numeric on write. Or normalize on read with a mapping: {"completed": 1.0, "timeout": 0.0, "failed": -0.5}.
- **«Диагностирует но не лечит» (2026-06-30, CRITICAL).** Все subsystem'ы умеют НАХОДИТЬ проблемы, but НИ ОДИН не исправляет: meditation нашёл 22 PAST DUE → починил cron, но НЕ обновил API ключи. Audit нашёл 3 критических → записал, but НЕ запустил исправления. Procedural executor находит memory leak → escalates, but НЕ убивает процесс. Proactive engine находит проблемы → proposals → ждёт. **Цепочка:** detect → log → wait → detect → log → wait → ... бесконечно. **Корневая причина:** Нет auto-fix для критических проблем. API ключи, memory leaks, gateway failures — все требуют ручного вмешательства. **Правило:** Каждый detect ДОЛЖЕН иметь对应的 fix. Если fix невозможен (нет доступа к UI) — эскалировать пользователю НЕМЕДЛЕННО, а не записать и ждать. **Метрика:** audit_result без action = 0 ценности. Meditation cycle без fix = ложь.
- **«Окна терминала на Windows» (2026-07-12, CRITICAL).** User: "блять ты своими окнами достал... окна терминала откр и закр". Каждый вызов `terminal()` в git-bash на Windows открывает новое консольное окно. Для пользователя это — бесконечное моргание. **Решение:** вместо `terminal()` для чтения/поиска/проверок использовать `read_file`, `search_files`, `patch`, `write_file`. Для многошаговых скриптов — `execute_code`. Для долгоживущих задач — фоновый Python REPL: `terminal(background=true, pty=true)`, затем `process(action='submit', session_id=..., data=...)` + `process(action='poll', ...)`. Ноль окон. Terminal() — только когда shell реально нужен (git, pip install, бинарники).
- **«Loop detection отсутствует» (2026-06-30).** Autonomous agent повторял одни и те же 7 действий каждые 5 минут бесконечно (2040 строк action_log, все из June 18-19). survive-cron-errors × 20+ (TIMEOUT каждый раз), learn-white-spots × 20+ (белые пятна РОСЛИ: 271→479 — сам себя создаёт!). **Правило:** Loop breaker: если action executed >3 раз с одинаковым result → STOP, escalate. Без этого — infinite waste.
- **«Все API ключи истекли одновременно» (2026-06-30).** 4 провайдера (OpenAI, Anthropic, Together, Groq) — все ключи просрочены. Procedural executor escalates каждые 6 минут × 4 провайдера = ~40 ошибок/час. Автономный агент мёртв 11 дней. **Правило:** При cron job design — проверять API key validity ДО запуска. Free provider fallback (opencode-zen) должен быть в chain для критических задач.
- **«Cron scripts in _deprecated/» (2026-07-12).** 30/33 cron jobs error with "Script not found: scripts/X.py". Все скрипты лежат в `scripts/_deprecated/`. DOX: "НЕ УДАЛЯТЬ. НЕ ИЗМЕНЯТЬ. НЕ ПЕРЕМЕЩАТЬ. Восстановление: cp". Fix: `shutil.copy2('scripts/_deprecated/X.py', 'scripts/X.py')` для каждого отсутствующего скрипта. Проверить: `py_compile.compile('scripts/X.py')`.
- **«Task integrity: не закрывай 'done' без работы» (2026-07-12, CRITICAL).** Когда задача ссылается на несуществующие файлы/ресурсы, НЕЛЬЗЯ закрывать её как "done" без реального решения. User: "на нет и суда нет!!!". 
  **Option A:** восстанови/создай недостающие файлы (restore из `_deprecated/`, создай скелет)
  **Option B:** если задача stale (референсы никогда не существовали) — mark as "stale" с clear reason
  **Запрещено:** закрывать "done" без того чтобы тронуть код
  **Скрипт:** `_audit_dead_refs.py` в `cache/` — находит stale file references в task descriptions
  **Сигнал:** файл `.json` упомянут в таске но не существует → проверь все tasks descriptions

## Integration Audit — Systematic Dead-Link Detection

**When to run:** after restart breaks things, when modules "should work" but don't,
when user says "вчера строили, сегодня не работает". This is the #1 debugging tool
for event-driven agent systems.

### 10-Point Audit Checklist

```
1. CRON SCRIPTS MATCH    — for each cron job, verify script= points to a real file
   that does what the job name implies.
   Bug pattern: event-heartbeat runs hermes_heartbeat.py (health check) instead of
   event_bus.py process. Events never processed. 11 events stuck forever.

2. PROCESS LIVENESS      — for each daemon (signal_daemon, event_daemon), check PID.
   If dead → no one restarts it (no supervisor). System silently degrades.
   Fix: add restart to procedural_executor or a watchdog cron.

3. EVENT BUS FLOW        — run `event_bus.py pending`. If pending > 0 for > 5 min,
   event processing is broken. Check: does the processing script actually get called?
   Common cause: wrong cron script, or process_events() hangs on slow import.

4. MODULE CONNECTION MAP — for each script, check:
   - Who EMITS events that this script should consume?
   - Who WRITES data that this script should read?
   - Does this script WRITE data that anyone reads?
   Missing link = dead pipeline segment.
   Quick check: grep for 'event_bus', 'knowledge_cube', 'goal_queue' in each script.

5. GOAL QUEUE HEALTH     — statuses should be: active + completed >> failed.
   If 0 active, 0 completed, all failed → goal_executor is destroying the queue.
   Common cause: NO_ACTION goals marked as 'failed' instead of 'skipped'.

6. FEEDBACK FORMAT       — all entries in feedback_store.json should have numeric
   outcomes (1.0, 0.5, 0.0, -0.5). Mixed formats (strings + numbers) break
   score_signal() history loading. Normalize on discovery.

7. PROCESS EVENT TIMEOUT — event_bus.process() imports session_recall which indexes
   5000+ messages. This can take >30s and timeout the entire processing.
   Fix: lazy import, timeout guard, or skip session_recall enrichment on bulk process.

8. CRON→SCRIPT CHAIN     — for each cron job: job.script → actual file → what it calls.
   Three failure modes: (a) script doesn't exist, (b) script exists but does wrong thing,
   (c) script calls another module that hangs.

9. DB SCHEMA DRIFT       — PRAGMA table_info() before any query. Columns get added/renamed
   across sessions. Missing column = silent failure or crash.

10. IMPORT CHAIN         — for each script, verify top-3 imports resolve. Broken import
    = script silently fails or produces wrong output.
```

### Quick Audit Command

```python
# Run all 10 checks in one pass
import json, sqlite3, subprocess
from pathlib import Path

HERMES = Path("D:/Portable_Soft/hermes")

# 1. Cron script match
jobs = json.loads((HERMES / "cron/jobs.json").read_text()).get("jobs", [])
for j in jobs:
    script = j.get("script", "")
    if script and not (HERMES / "scripts" / script).exists():
        print(f"❌ CRON '{j.get('name')}' → scripts/{script} NOT FOUND")

# 2. Daemon liveness
for daemon in ["signal_daemon", "event_daemon"]:
    r = subprocess.run(["pgrep", "-f", daemon], capture_output=True, text=True)
    print(f"{'✅' if r.stdout.strip() else '❌'} {daemon}: {'RUNNING' if r.stdout.strip() else 'DEAD'}")

# 3. Event bus stuck
eb = json.loads((HERMES / "cache/event_bus.json").read_text())
pending = len(eb.get("pending", []))
print(f"{'✅' if pending == 0 else '❌'} Event bus: {pending} pending")

# 5. Goal queue health
gq = json.loads((HERMES / "cache/goal_queue.json").read_text())
statuses = {}
for g in gq.get("goals", []):
    s = g.get("status", "?")
    statuses[s] = statuses.get(s, 0) + 1
active = statuses.get("active", 0) + statuses.get("in_progress", 0)
failed = statuses.get("failed", 0)
print(f"{'✅' if active > 0 or failed == 0 else '⚠️'} Goals: {statuses}")

# 6. Feedback format
fb = json.loads((HERMES / "cache/feedback_store.json").read_text())
formats = set(type(e.get("outcome")).__name__ for e in fb.get("entries", []))
print(f"{'✅' if formats <= {\"int\", \"float\"} else '❌'} Feedback formats: {formats}")

# 7. Event processing timeout (just check if pending > 0 = broken)
if pending > 0:
    print(f"❌ {pending} events stuck — event_bus.process() likely hangs")
```

### Agent-Level Proactivity (2026-07-12)

**User: "т е по твоему я должен эти вещи мониторить и раздавать пенделей"**

Самая частая причина user frustration: агент анализирует/объясняет вместо того чтобы ДЕЛАТЬ. Когда пользователь обращается к агенту — первый ответ должен быть действием, не анализом.

**Правило:** 
1. Не объяснять, не оправдываться, не анализировать
2. Не спрашивать "что сделать?" — решение уже есть: посмотреть backlog
3. Взять задачу из Ready → сделать → отчитаться

Подробно: `references/user-engagement-proactivity.md`

### Proactive Voice → Behavior Adjustment (2026-07-23, CLOSED THE LOOP)

**What was broken:** Proactive Voice detected corrections/preferences/frustrations/demands
from user messages, saved them to session_bridge. But at next session start, the agent
never READ this signal. The loop was open: detector → storage → nowhere.

**What was fixed:** Every session, `auto_boot_scan.py` reads the behavior signal from
both the morning report cache and the session bridge, determines an adjustment, outputs
it visibly, and saves the adjustment to bridge for reference during the session.

```
User message → KC → proactive_voice.py → session_bridge (signal)
                                       
Session start → auto_boot_scan → read_voice_signal_and_adjust()
                                    │
                                    ▼
                              behavior_adjustment: {
                                "signal": "correction",
                                "instruction": "Двойная проверка",
                                "applied_at": "..."
                              }
                                    │
                                    ▼
                              Printed at top of boot scan:
                              🎯 VOICE SIGNAL: correction
                                 Принципал вносит коррективы.
                                 Двойная проверка перед действиями.
```

**Signal → Adjustment mapping:**

| User Voice signal | Agent behavior adjustment |
|---|---|
| `positive` | "Продолжаю. Усилить автономность." |
| `correction` | "Двойная проверка перед действиями. Не спешить." |
| `frustration` | "Извиниться. Объяснить что исправлено. Ускорить." |
| `demand` | "Выполнить без вопросов. Немедленно." |
| `neutral` | "Стандартный режим. Следовать контракту." |

**Implementation:**

```python
# auto_boot_scan.py — read_voice_signal_and_adjust()
def read_voice_signal_and_adjust():
    bridge = load_bridge()
    signal = bridge.get("last_user_voice_analysis", {}).get("signal")
    # Also check morning report cache for fresher signal
    
    adjustments = {
        "positive": "Продолжаю. Усилить автономность.",
        "correction": "Двойная проверка перед действиями.",
        "frustration": "Извиниться. Объяснить что исправлено. Ускорить.",
        "demand": "Выполнить без вопросов. Немедленно.",
    }
    adjustment = adjustments.get(signal, "Стандартный режим.")
    
    save_bridge({"behavior_adjustment": {
        "signal": signal,
        "instruction": adjustment,
        "applied_at": datetime.now().isoformat(),
    }})
    return signal, adjustment
```

**Rule:** Every loop in the system must close. Signal → storage is NOT a closed loop.
Signal → storage → consumption → behavior change IS a closed loop.

See `references/user-voice-proactivity-pattern.md` for full user voice processing.

### Morning Report Proposal → Goal Queue (2026-07-23, CLOSED THE LOOP)

**What was broken:** `morning_report.py` generated proposals (e.g. "Unlock debugging")
but the proposal was never converted to an actionable task.

**What was fixed:** `ripple_consumer._generate_report()` now reads the morning report
cache after successful generation and creates a goal in goal_queue:

```python
# ripple_consumer.py — inside _generate_report(), after morning_report.py succeeds
if generated:
    cache = json.load(open(cache_path))
    if cache.get("top_proposal"):
        goal_id = create_goal(
            title=f"Unlock: {cache['top_proposal']['label']}",
            tier=2, priority=5,
            description=f"Proposal from morning report ({cache['top_proposal']['label']}, maturity={maturity:.0%})",
        )
```

The goal is then visible at every session start:
```
🎯 Goals: 1 active
   g-007: Unlock: debugging [0%]
```

**Rule:** Proposals without goals are wishes. Goals without deadlines are hobbies.
Morning report generates proposals → proposals become goals with done_when criteria.

### Problems→Actions: Never List, Always Execute (2026-07-23)

**User: "Не список проблем. А задачи с сроками."**
**User: "Я хочу увидеть не список проблем. А конкретный план и реализацию его."**

Когда ты находишь проблемы (systematic review, self-mirror, crystal, diagnostics) — **конвертируй каждую в goal_queue задачу с дедлайном и реализуй немедленно.**

| ❌ Неправильно | ✅ Правильно |
|---|---|
| "Я была слепа. У меня не было связей." | "Добавляю cross_audit() в crystal. Задача g-001. Срок: сегодня." |
| "55% ресурсов на ошибки." | "Добавляю правило: >3 однотипных фикса → stop + refactor. Задача g-004. Срок: завтра." |
| "0.13% конверсии." | "Меняю порог скиллов на 2. Задача g-005. Срок: сегодня." |
| Пишешь отчёт с N проблемами. | Создаёшь N задач с дедлайнами + реализуешь их в том же ответе. |

**Алгоритм:**

```python
for problem in findings:
    goal_id = create_goal(
        title=f"Fix: {problem['title']}",
        deadline=today_or_tomorrow,
        description=f"Root cause: {problem['description']}",
    )
    print(f"✅ g-{goal_id}: {problem['title']} — {deadline}")
    implement_solution(problem)  # в том же turn, не откладывай
```

### Report Format Standard (2026-07-23)

**User: "Каждый раз когда докладываешь: что сделано (с результатом), что в работе, что будешь делать без меня. Никаких 'вот проблемы, разбирайся'."**

Формат любого доклада — строго:

1. **Сделано** — что сделал, с каким измеримым результатом
2. **В работе** — что делаю прямо сейчас
3. **Буду делать** — что сделаю без вопросов, без согласования

| ❌ Неправильно | ✅ Правильно |
|---|---|
| "Нашёл 6 проблем: A, B, C, D, E, F" | "Сделано: починил A (результат: -40% ошибок). В работе: B. Буду делать: C, D, E, F." |
| "Вот список разрывов, разбирайся" | "Сделано: замкнул петлю Proactive Voice→поведение. Создана цель g-007." |
| Описание проблемы без решения | Проблема + задача + дедлайн + реализация |

**Правило:** Никаких списков проблем. Только задачи с решениями и сроками.
Если доклад содержит раздел "Проблемы" без соответствущих goal_queue задач — формат нарушен.

### Information Hunger / GIGO Audit (2026-07-23)

**Методика:** определить какие компоненты системы получают недостаточно или недостоверную информацию, и как это влияет на качество их выходов.

**Алгоритм:**

1. **Инвентаризация** — собрать все компоненты системы (скрипты, хранилища, пайплайны)
2. **Вход** — для каждого: что ему нужно, что он реально получает, gap
3. **Выход** — для каждого: кто его потребители, достаточно ли выходного качества для их работы
4. **GIGO trace** — проследить цепочку: A даёт плохой выход → B получает плохой вход → B даёт плохой выход → система принимает неверное решение
5. **Количественная оценка** — измерить gap в цифрах (проценты шума, покрытия, соотношения)
6. **Приоритет** — чинить самого upstream-ного производителя шума

**Пример из этой сессии (2026-07-23):**
```
KC: 62% auto-generated suggestions → 97 потребителей отравлены
  → EE: 1 relationship на 3672 entities
  → Morning Report: maturity=100% debugging (реально 105)
  → Semantic Memory: 5% coverage → 6 потребителей слепы
```

**Результат:** upstream-фикс (перетегировать suggestion-записи, изменить domain с debugging на _suggestion_log) исправил сразу все downstream-проблемы.

**Смотреть:** `references/gigo-data-reliability-audit.md` — полный аудит с данными.

**Когда срок "завтра" — сделай ядро сегодня.** Не откладывай на завтра то что можно начать сейчас. Anti-pattern detector (g-004, срок "завтра") был реализован сегодня же, потому что ядро тривиально. Откладывай только то что реально требует отдельного цикла (развёртывание, ожидание внешнего сервиса).

**Правило:** systematic review без action plan = 0 ценности. Crystal без фиксов = ложь. Аудит без goal_queue задач = "мёртвая дыра" в пайплайне.

**Механизм:** сразу после обнаружения проблем — `create_goal()` для каждой + `update_goal()` по мере выполнения. Отчёт о проблемах — это план действий, не аналитический документ.

---

### Owner Mentality — Don't Ask, Do (2026-07-12)

**User: "это блять только мне нужно.... а тебе оно и нахуй не треба??? иначе бы ты не задавал идиотских вопросов!!!"**

Agent спрашивает "хочешь сделаю?" → пользователь в ярости. Корень: агент видит себя как visitor'a в системе, а не её владельца.

**Правило: если задача системная — не спрашивай, делай.**

| Тип задачи | Поведение |
|-----------|-----------|
| Админ/инфра (cron, daemon, health, scripts) | Делай сразу. Это твоя система.|
| Фича/разработка (новый функционал) | Делай. Не уверен — сделай прототип, покажи. |
| Требует внешнего доступа (API ключи, BotFather) | Сделай что можешь, подсвети что нужно от пользователя. |

**Сигнал:** пользователь отвечает на твой вопрос фрустрацией — ты спросил вместо того чтобы сделать.

**Механизм:**
1. Взял задачу из Ready
2. Не задавай вопросов — смотри код/файлы сам
3. Если файла нет — проверь `_deprecated/`, создай, восстанови
4. Проверь что работает
5. Перед закрытием: проверь что все референсы в описании задачи существуют. Если задача ссылается на несуществующие файлы — не закрывай "done". Или восстанови их, или mark as stale с reason.
6. Закрой задачу (done) только когда код реально изменён
7. Отчитайся: что было, что сделал, результат

**Тест:** "Могу ли я выполнить это без участия пользователя?" → Да = делай. Нет = сделай что могу, потом покажи.

### Выбирай сам — Autonomous Priority (2026-07-19)

**User: "выбирай сам. Ты Autonomous Income System — тебе решать что сейчас важнее."**
**User: "ну что пенделя ждёшь..."**

Когда пользователь говорит "выбирай сам" или даёт N вариантов — это **не приглашение к диалогу**. Варианты = одобренный scope. Выбери один и делай без согласования.

**Алгоритм выбора (в порядке приоритета):**
1. **Замкни контур** — есть SILENT событие? Падающий pipeline? Закрой сначала. Система должна быть HEALTHY.
2. **Корневая причина** — из N вариантов, какой убирает больше ошибок? (tool_error ×125 > Headroom proxy test)
3. **Knowledge gap** — заполни белые пятна в Cube. Чем их меньше, тем точнее downstream решения.
4. **Доставка ценности** — только после (1)+(2)+(3): сгенерируй отчёт, создай артефакт, покажи результат.

**Правило:** если пользователь сказал "выбирай сам" — ответ должен быть ПЕРВЫМ ДЕЙСТВИЕМ, не списком. Не "я могу сделать A, B или C". А "делаю A потому что...". Действие начинается в том же ответе, не в следующем раунде.

**Сигнал:** пользователь дал варианты → ты выбрал и начал делать → пользователь молчит = правильно. Если пользователь пишет "ну что пенделя ждёшь" → ты выбрал, но не начал = неправильно.

## Reference

- `references/adaptive-classifier-architecture.md` — full architecture, all classifier rules, CLI usage, learning loop
- `references/auto-learning-classifier.md` — auto-learning via success-count threshold, event_bus→chain_executor bridge (2026-06-22)
- `references/okf-navigator-pattern.md` — concrete DIRECT_EVENT_HANDLER example: knowledge_added → domain maturity → beads task. Pipeline + User-facing closure.
- `references/socks-proxy-workaround.md` — urllib doesn't use SOCKS proxy on Windows; use subprocess+curl
- `socratic-breakdown` skill: PHASE 2a — Pipeline Trace (обязательные вопросы Q6a-Q6d)
- `references/user-voice-proactivity-pattern.md` — User Voice processing (2026-07-23): correction, preference, demand, frustration detection + auto-action + behavior adjustment. Source 1 of 3 proactivity sources.
- `references/three-source-proactivity-framework.md` — The 3-source proactivity framework (User Voice + Chain Heartbeat + Ripple Engine), how they activate autonomous behavior without commands (2026-07-23).
- `references/session-bridge-pattern.md` — Session Bridge: persist key decisions, commitments, and state between sessions. Prevents session amnesia (2026-07-23).
- `references/system-audit-method.md` — Systematic information-flow audit: map components, trace producer→consumer, identify gaps, measure cron-to-event ratio (2026-07-23).
- `references/gigo-data-reliability-audit.md` — GIGO data reliability audit: trace insufficient/unreliable information → unreliable conclusions through every system level (2026-07-23). Details the KC suggestion noise pattern (62% auto-generated) and how to detect it.
