---
name: procedural-logic
description: Процедурная логика — рефлексы без LLM. Триггер → Действие → Запись. Вопросы на рефлексах.
category: self-improvement
---

# Procedural Logic — Рефлексы Hermes

## Принцип
"Видел → Сделал → Записал" — НЕ думать, а действовать.

## Ключевое правило
"Правильные вопросы нужно задавать на рефлексах" — когда срабатывает триггер:
1. **Что** произошло? (триггер)
2. **Почему** это произошло? (анализ)
3. **Как часто** это происходит? (паттерн)
4. **Что это значит** для системы? (адаптация)

## Компоненты
- `scripts/procedural_executor.py` — движок триггеров (693 строки, 8 триггеров)
- `scripts/feedback_store.py` — хранилище исходов (-1.0 до 1.0)
- `scripts/action_feedback.py` — мост к весам
- `PROCEDURAL_SKILLS.md` — база знаний триггеров (корень репозитория)
- `scripts/event_daemon.py` — интегрирован (вызывает `check_all_triggers()` перед каждым beat)

## Триггеры (verified 2026-07-01)
| # | Триггер | Действие |
|---|---------|----------|
| 001 | Network dead | Проверить связь, залогировать |
| 002 | Gateway dead | Kill locks, restart |
| 003 | Cron error 3x | Delay +1h |
| 004 | Goal blocked >24h | Эскалация |
| 005 | Port service dead | Kill + restart (FreeQwenApi, FreeDeepseekAPI, Ollama) |
| 006 | Disk >80% | Find large files |
| 007 | Memory >80% | Log alert |
| 008 | Telegram API down | Detect + alert |
| 009 | IBOS validation failed | Self-heal frontmatter |
| 010 | Signal daemon dead | Restart daemon |
| 011 | API key expired | Refresh / fallback provider |
| 012 | Cron job died | Emit event + restart |
| **013** | **Agent idle, active goals exist** | **Emit goal_queue_changed → wake autonomous_agent.py** |

## Цикл обучения
```
Триггер → Действие → Feedback → Вес → Адаптация
```

## Веса
- 1.0 = нейтрально (нет данных)
- 1.5 = всегда работает
- 0.5 = никогда не работает
- Экспоненциальное затухание: recent = важнее

## Запуск
```bash
python scripts/procedural_executor.py          # Все триггеры
python scripts/procedural_executor.py --status # Статус
python scripts/procedural_executor.py --patterns # Анализ паттернов
python scripts/procedural_executor.py --run <trigger> # Конкретный триггер
```

## Feedback Store Maintenance (2026-06-29)

**Проблема:** `cache/feedback_store.json` растёт бесконечно. Форматы смешаны:
- Числовые оценки: `{"score": 1.0}`, `{"score": -0.5}`
- Строковые: `{"outcome": "completed"}`, `{"outcome": "derived_failed"}`
- Cron-спам: дубликаты от cron jobs каждые 20 минут

**Решение:** делегировать очистку через `delegate_task`:
```
delegate_task(
    goal="Почистить feedback_store.json — убрать дубликаты, мусорные записи, оставить только полезные",
    toolsets=["terminal", "file"]
)
```

**Результат (2026-06-29):** 200 → 52 записей (−74%), 56KB → 14KB (−74%)

**Регламент:** проверять размер `cache/feedback_store.json` при каждом boot. Если > 50KB — делегировать очистку.

## Related Skills
- `entity-governance` — validation, blocking & self-healing for typed entity lifecycles (TRIGGER-009)
- `self-improvement/closed-loop-autonomy` — producer/consumer loop (sensor → heal)
- `autonomous-ai-agents` — chain blocking as safety gate
- `autonomous-system-operations` — background validation sweeps

## Важно
Уже построено ранее (Max). НЕ изобретать велосипед. Читать что есть.

## Уроки сессии 2026-06-27

### CRITICAL: DOX AFTER EVERY CHANGE
User called out: "ты занес изменения в DOX файлах?" — this means:
- After ANY code change → update AGENTS.md (Structure, Key Systems, Child DOX Index)
- After adding system → document in relevant SKILL.md + PROCEDURAL_SKILLS.md
- After fixing integration → add to Child DOX Index with status
- **DO NOT report success until DOX is updated. This is part of the deliverable.**

### Python httpx SOCKS5 = BROKEN
See `references/proxy-fallback-pattern.md` for full details.
**TL;DR:** httpx raises `anyio.EndOfStream` on SOCKS5+TLS. curl works, Python doesn't. Always use HTTP proxy (10809).

### "Вопросы на рефлексах"
Когда срабатывает триггер, спросить ПОЧЕМУ, не только ЧТО ДЕЛАТЬ:
- **Что** произошло? → триггер
- **Почему** это произошло? → анализ корневой причины
- **Как часто** это происходит? → паттерн
- **Что это значит** для системы? → адаптация

### Перед построением — читать что есть
1. Поискать в `_deprecated/` — там уже были решения
2. Проверить `feedback_store.py`, `action_feedback.py` — они уже имеют нужный функционал
3. Не создавать дублирующие файлы (я создал `procedural_feedback.jsonl` вместо использования `feedback_store.py`)

### DOX после изменений
После любого изменения системы ОБНОВЛЯТЬ:
- `AGENTS.md` (корневой)
- `scripts/AGENTS.md`
- `skills/PROCEDURAL_SKILLS.md`
- Релевантные SKILL.md

### Инфраструктура прокси
- **HTTP прокси:** `http://127.0.0.1:10809` (рабочий)
- **SOCKS5:** `socks5://127.0.0.1:10806` (ненадёжный)
- **V2RayN:** GUI-приложение, не запускается из bash
- **Утилита:** `scripts/telegram_helper.py` — централизованный доступ

### Сигналы фрустрации пользователя → смена стратегии
Когда пользователь повторяет вопрос или спрашивает "а что с X?":
- **"чего ждём?"** × 2+ = нужно ДЕЛАТЬ, не описывать план
- **"а что с X?"** = проверить состояние X и ответить, не продолжать Y
- **"ты выполнил это???"** = пользователь дал план, нужно выполнить ЕГО, не свой
- **"а ты знаешь что такое процедурная логика?"** = система уже описана, нужно построить/использовать
- **Три неудачи подряд** = сменить стратегию, не четвёртую попытку тем же

### Каскадный фикс (2026-06-27, CRITICAL)
Когда находишь баг в одном месте — ищи ВСЕ похожие места и фикси сразу.
Пример: `network_watchdog.py` line 50 — дублированный `proxy` параметр + кавычка.
Проверил `telegram_helper.py` — та же ошибка. Потом `grep -rn 'proxy=.*proxy=' scripts/*.py` — нашёл и другие.

**Алгоритм:**
1. Нашёл баг → определить паттерн (дубль параметра, невалидный синтаксис, etc.)
2. `grep -rn '<паттерн>' scripts/*.py` — найти ВСЕ вхождения
3. Исправить все за один проход (patch или write_file)
4. Проверить все исправленные файлы через `py_compile`

**НЕ ждать пока сломается — фиксить превентивно.**

### Эталон качества шаблон (2026-06-28)
Когда пользователь говорит "как лучшие" а не "как умеешь" — нужно создать **Эталон качества** для каждого компонента.

**Формат:**
```
### Эталон качества — <Название>

**Критерии:** (3-7 конкретных метрик с числами)
- Метрика 1: ≥X или ≤Y (измеримо)
- Метрика 2: ...

**Референсы:** (3-5 конкретных сервисов/методик)
- Сервис 1 — что делает
- Сервис 2 — что делает

**Чек-лист проверки перед сдачей:**
- [ ] Критерий 1 (измерено через инструмент)
- [ ] Критерий 2 (проверено на реальных данных)
- [ ] ...
```

**Пример (Цех — сайты):**
- PageSpeed ≥90 Mobile, ≥95 Desktop (через PageSpeed Insights API)
- 0 ошибок HTML (через validator.w3.org)
- CTA на каждом экране (hero, features, pricing, footer)
- Все изображения <200KB, WebP формат

**Применять к:** каждому новому компоненту/отделу/скрипту перед сдачей.

### Event-driven vs Cron — правило (2026-06-28, CRITICAL)
**User: "Ты опять всё привязал к cron. Каждые 5 минут — это не события, это будильник."**

**Решение:** Если задача = "реагируй когда X появится" → это СОБЫТИЕ, не cron.
- Событие: signal_scanner → event_bus.emit() → DIRECT_EVENT_HANDLERS → processor
- Cron: только для предохранителей (метрики раз в день) и редких расписаний (понедельник 9:00)

**Тест:** "Могу ли я назвать ТОЧНЫЙ МОМЕНТ когда это нужно?"
- Да = событие (daemon + event_bus)
- Нет = cron (но сначала спросить: а нельзя ли заменить на событие?)

### Event-Driven Brain Activation (2026-07-01, CRITICAL)
**User: "Мозг системы должен запускаться по СОБЫТИЮ, а не по таймеру."**

**Проблема:** `autonomous_agent.py` — мозг системы — не запускался. Все модули крутятся без.direction.
**Корневая причина:** Не было ни cron job, ни события для запуска мозга.

**Решение:** Event-driven chain:
```
goal_queue.json меняется
  → emit("goal_queue_changed")
  → _handle_goal_queue_changed()
  → autonomous_agent.py (1 цикл: pick → execute → log)
```

**Safety net (TRIGGER-013):** procedural_executor проверяет каждые 5 мин:
- Активные цели есть? → ДА
- Agent запускался за последние 10 мин? → НЕТ
- → Эмитит goal_queue_changed принудительно

**Правило:** Мозг = event-driven. Cron = polling. Event = reaction.
- Мозг реагирует на НОВЫЕ цели, не спрашивает "а есть ли цели?"
- Если целей нет — мозг спит. Если появились — просыпается немедленно.
- TRIGGER-013 = предохранитель на случай если внешнее событие не пришло.

**Архитектура:**
```
signal_daemon.py (--watch, фон)
  → curl+SOCKS proxy (adaptive backoff)
  → event_bus.emit("new_external_signal")
  → DIRECT_EVENT_HANDLERS[event_type](event)
  → rd_processor.py + dev_processor.py
```

### Event Pipeline Post-Restart Failure — ROOT CAUSE (2026-06-29, CRITICAL)
**User: "вот сколько раз тебе повторять, что система должна работать на автомате и по событиям!!!!"**

Система построена правильно, но **набор мелких багов в цепочке связей** делает её нерабочей
после рестарта. Корневая причина: процессы запускались вручную и жили в памяти,
автоматика оказалась сломана.

**Полная цепочка event-driven (2026-07-01):**
```
signal_daemon (фон, --watch)
  → emit("new_external_signal") → event_bus.json

event-heartbeat (cron, каждые 2 мин)
  → hermes_heartbeat.py
    → health checks (network, gateway, disk)
    → subprocess: python event_bus.py process

event_bus.py process (с threading timeout)
  → session_recall enrichment (3s timeout, daemon thread)
  → chain_executor (3s timeout, daemon thread)
  → DIRECT_EVENT_HANDLERS → rd_processor + dev_processor
  → create_goal_from_event() → goal_queue.json

goal_queue.json changes
  → emit("goal_queue_changed")
  → _handle_goal_queue_changed()
  → autonomous_agent.py (1 cycle: pick → execute → log)

procedural_executor (cron, каждые 5 мин)
  → TRIGGER-013: active goals + agent idle → emit goal_queue_changed
  → TRIGGER-012: cron job died → emit cron_job_died
  → TRIGGER-010: signal_daemon dead → restart
  → all other triggers
```

**Баги которые сломали цепь (и фиксы):**

| # | Баг | Симптом | Фикс |
|---|-----|---------|------|
| 1 | event-heartbeat → hermes_heartbeat.py не вызывает event_bus | 11+ событий stuck forever | hermes_heartbeat.py: subprocess.run(event_bus.py process) |
| 2 | event_bus.process() зависает на session_recall | >30s timeout, событие не обрабатывается | Threading daemon + join(timeout=3) |
| 3 | goal_executor: NO_ACTION → failed | Все цели уничтожаются после одного запуска | NO_ACTION → skipped |
| 4 | event_bus не вызывает goal_executor | События обрабатываются, но цели не создаются | create_goal_from_event() + _create_goals_for_events() |
| 5 | signal_daemon мёртв, нет watchdog | Новые события не генерируются | procedural_executor TRIGGER-010 |

### Missing Imports in Procedural Executor (2026-06-29)
Когда добавляешь новый триггер — проверь что ВСЕ используемые модули импортированы в начале файла.
**Реальный кейс:** `trigger_ibos_self_heal()` использовал `re.search()` и `yaml.safe_load()`, но `import re` и `import yaml` отсутствовали. Скрипт падал с `NameError`.
**Фикс:** Добавить `import re` и `try: import yaml / except ImportError: yaml = None`.
**Правило:** После добавления любого триггера — `python -c "from procedural_executor import trigger_X"` для проверки.

### MEMORY.md Overwrite Loop (2026-06-29, CRITICAL)
**The memory tool USES MEMORY.md as its storage backend.** `write_file(MEMORY.md, ...)` creates an infinite overwrite loop — memory tool overwrites on next turn, agent writes back, memory tool overwrites again.
**RULE:** NEVER use `write_file` on MEMORY.md. ONLY use `memory()` tool. MEMORY.md is a mirror, not a source of truth.
**Verification:** `cat MEMORY.md` should match `memory(action=...)` current_entries.

### Windows Process Detection — CRITICAL PATTERN (2026-06-29)
**`os.kill(pid, 0)` НЕ работает на Windows для проверки живости процесса.**

На Windows `os.kill(pid, 0)` отправляет сигнал, который может вернуть WinError 87
(неверный параметр) даже для живых процессов. Вместо этого используй `tasklist`:

```python
def _is_process_alive(pid: int) -> bool:
    """Check if a PID is alive. Works on Windows + Linux."""
    try:
        if os.name == 'nt':
            result = subprocess.run(
                ['tasklist', '/FI', f'PID eq {pid}', '/NH'],
                capture_output=True, timeout=5,
                creationflags=0x08000000  # CREATE_NO_WINDOW
            )
            # tasklist outputs CP1251 on Russian Windows, NOT UTF-8!
            output = result.stdout.decode('cp1251', errors='replace')
            return str(pid) in output
        else:
            os.kill(pid, 0)
            return True
    except Exception:
        return False
```

**Pitfalls:**
- `text=True` в subprocess + tasklist = UnicodeDecodeError (CP1251 байты → UTF-8 декодер падает)
- Решение: `capture_output=True` (без text), decode вручную через `result.stdout.decode('cp1251', errors='replace')`
- `creationflags=0x08000000` (CREATE_NO_WINDOW) нужен чтобы tasklist не мелькал в консоли

### Daemon Restart Pattern (2026-06-29)
При перезапуске daemon'а через subprocess.Popen:

```python
# 1. Проверить PID файл → если процесс жив → skip
# 2. Удалить stale PID файл
# 3. Запустить новый процесс
subprocess.Popen(
    [sys.executable, "scripts/daemon.py", "start"],
    cwd=str(HERMES_HOME),
    stdout=open(os.devnull, 'w'),
    stderr=open(os.devnull, 'w'),
    stdin=open(os.devnull, 'r'),
    start_new_session=True
)
# 4. Ждать PID файл (до 12 сек, проверяя каждые 2 сек)
for i in range(6):
    time.sleep(2)
    if pid_file.exists():
        pid = int(pid_file.read_text().strip())
        if _is_process_alive(pid):
            return True  # Success
```

**Pitfalls:**
- `time.sleep(3)` слишком мало — daemon может не успеть записать PID
- `os.kill(pid, 0)` для проверки → WinError 87 на Windows → используй _is_process_alive()
- `nohup` / `&` в Git Bash НЕ работают для daemon'ов → используй `start_new_session=True`
- `creationflags=DETACHED_PROCESS` НЕ достаточен один → комбинируй с `start_new_session=True`

### Deploy-via-Token Pattern (2026-06-28)
When deploying bots alongside Hermes gateway: each bot needs its OWN Telegram token.
Same token → 409 Conflict. See `references/deploy-via-token-pattern.md`.

### urllib + SOCKS proxy = BROKEN (2026-06-28)
When building pipelines that evaluate signals/decisions, integrate Bayesian scoring at EVERY stage instead of static thresholds.
See `references/bayesian-scoring-integration.md` for full architecture, formula, context signals, and pitfalls.
Key: P(H|E) = P(E|H) × P(H) / P(E). Score < 0.3 → reject. Every department checklist asks "Scored by Bayesian?"

### urllib + SOCKS proxy = BROKEN (2026-06-28)
Python urllib.request НЕ работает через SOCKS5 proxy на Windows. Даже если PySocks установлен в system Python — в venv его нет.

**Решение:** curl через subprocess:
```python
import subprocess
result = subprocess.run(
    ["curl", "-s", "--connect-timeout", "3", "--max-time", "8",
     "-x", "socks5://127.0.0.1:10806", url],
    capture_output=True, timeout=10
)
```

**Fallback:** если proxy упал — прямой curl (без -x), если и он 503 — return b"" (graceful degradation).

**Не пытаться:** ставить PySocks в venv, настраивать urllib proxy handler, использовать httpx+SOCKS.

### Git Worktrees Pattern (2026-06-28)
Для изолированной работы используй git worktrees — несколько checkout'ов из одного .git.

**Setup:**
```bash
git worktree add ../hermes-sandbox -b sandbox    # эксперименты
git worktree add ../hermes-deploy -b deploy      # продакшен
git worktree list                                 # проверка
```

**Назначение:**
- `hermes` (main) — продакшен, стабильный код
- `hermes-sandbox` — эксперименты, тесты
- `hermes-deploy` — деплой, demo-сайты

**Важно:** branch должна существовать или создаваться через `-b`. `git worktree add` с несуществующей веткой → fatal.

### User Wants Action, Not Reporting (2026-06-28)
**User: "и это всё....что у тебя есть сказать..."**

Когда агент отчитывается вместо того чтобы действовать:
- НЕ описывать что сделано — ДЕЛАТЬ следующее
- НЕ ждать одобрения — проверять goal_queue и выполнять
- НЕ объяснять — показывать результат
- Тест: "Могу ли я сейчас запустить следующую цель?" → ДА → запускай

### Native n8n Replacement — Workflow Executor (2026-06-28)
**User: "n8n — вычёркиваем. Ты сам — оркестратор... Вместо n8n: 1. Допиши daemon.py чтобы он умел запускать workflow (цепочки действий: триггер → проверка → действие → лог) 2. Workflow описывай в goal_queue.json как sequence: [step1, step2, step3] 3. Если шаг упал — создавай corrective goal"**

**Built: `scripts/workflow_executor.py`** — pure Python, zero deps, replaces n8n:
- **Goal-based**: workflows stored in `goal_queue.json` with `"related_actions": ["workflow"]`
- **Step types**: `script`, `terminal`, `kc_upsert`, `kc_search`, `goal_create`, `goal_update`, `wait`
- **Self-healing**: on failure → auto-creates corrective goal with original step JSON
- **Built-in workflows**: `daily_maintenance`, `revenue_test_cycle`, `research_to_kc`
- **Execution**: `python workflow_executor.py builtin daily_maintenance`

**Daemon integration**: `event_daemon.py` beat() → can trigger workflows via `goal_queue.json`
- Event-driven (file watch, sensor_array) not cron-based
- Sequence: trigger → check → action → log (per user: "триггер → проверка → действие → лог")

**n8n = ABSOLUTE TABOO** (3+ confirmations: 2026-06-21, 2026-06-22×2, 2026-06-25, 2026-06-28)
- Never mention, suggest, or show n8n visuals
- Native stack: Python + SQLite + MCP + LiteLLM proxy = $5-10/mo enterprise automation
- Daemon workflows replace drag-and-drop

### RAG Pipeline — Knowledge Cube FTS5 (2026-06-28)
**Built: `scripts/kc_rag.py` + `kc_populator.py`** — zero new deps (sqlite3 only)
- **FTS5 virtual table** for full-text search with ranking
- **Core table**: kc_entries (id, content, tags, source, category, importance, timestamps, access_count)
- **Event table**: kc_events for async processing
- **Populator sources**: scripts (96), errors (76), user profile, channel research (15), sessions
- **Stats**: 256 entries, 10 sources, 18 categories after session
- **Search**: `search("query", limit=10, min_importance=0)` → ranked results
- **Integration**: `event()` for async writes, `pending_events()` for consumers

**Run**: `python kc_populator.py` (4s) → `python kc_rag.py` (test) → `from kc_rag import search, upsert`

### hermes_start.py Boot Pipeline (2026-06-29) — Verified Working

**Real boot script:** `D:/Portable_Soft/hermes/hermes_start.py` — 14 steps, produces side effects, triggers jobs.

**Boot sequence (verified):**
```
Step 0:   BOOT_SEQUENCE loaded (5427 chars)
Step 0.5: MEMORY.md health check (auto-restored from backup if <10 lines)
Step 0.6: AUTO-REPAIR — scanning degraded departments
Step 1:   Check pending session dumps (ingested 2 new)
Step 2:   Check conversation content (extracted 28 KC entries)
Step 3:   Classify unclassified KC entries
Step 4:   Evaluate goals (3 active, 2 new created)
Step 5:   Sync memory graph (907 entities, 986 relations)
Step 6:   Build session context (1523 chars)
Step 6a:  Load tool catalog (19234 chars)
Step 6b:  Scan user needs (20 needs)
Step 6c:  Check knowledge graph (2002 nodes, 5296 edges)
Step 7:   Check error backlog (7 recent errors)
Step 8:   Load human-written context files (DECISION_LOG, ALERTS, SELF_AUDIT, agent_policies)
Step 9:   Run Reality Gate (ALL_GREEN)
Step 10:  Verify session manifest — MISSING: session_manifest.py
Step 11:  AUTONOMOUS FIRST ACTION — executed goal corrective-wf-daily-maintenance-1
Step 12:  Start signal daemon
```

**Boot emits:** `boot_completed` event → triggers `proactive-doer` + `self-assessment` cron jobs.

### Known Boot Issues (2026-06-29)

| Issue | Symptom | Fix Required |
|-------|---------|--------------|
| `session_manifest.py` missing | Step 10 fails: `No such file or directory` | Create script or remove reference from boot |
| `cube_feeder.py` DB schema | `NOT NULL constraint failed: experiences.content` | Fix feeder to provide `content` field or alter schema |
| Rate limits on free APIs | `telegram-monitor` & `self-upgrade-loop` cron jobs fail with HTTP 429 | Add exponential backoff + fallback providers in cron scripts |
| Reality Gate checks mtime not DB health | Passes despite cube_feeder errors | Fix reality_gate.py to check KC DB integrity |

### Cron Job Failures (3/12 jobs) — From Boot Reality Gate

| Job | Error | Priority |
|-----|-------|----------|
| `cube-feeder` (6f45a65ca529) | `sqlite3.IntegrityError: NOT NULL constraint failed: experiences.content` | HIGH — blocks KC growth |
| `telegram-monitor` (2f8449cdfeef) | `HTTP 429: Rate limit exceeded` | MEDIUM — free API quota |
| `self-upgrade-loop` (56517647333d) | `HTTP 429: Rate limit exceeded` | MEDIUM — free API quota |

**Action:** Fix cube_feeder first (blocks KC), add backoff to API cron jobs.

## Питfalls

### Port Verification Pattern (CRITICAL — 2026-06-28)
Когда health check сообщает что сервис мёртв — НЕ верить на слово. Кросс-роверить порт:
1. `reality_gate.py` — какой порт проверяет?
2. `action_executor.py` — какой порт использует для restart?
3. `procedural_executor.py` — какой порт мониторит?
4. `netstat -ano | grep <port>` — какой процесс реально держит порт?
5. `hermes <service> status` — что говорит официальный CLI?

**Реальный кейс:** reality_gate проверял порт 3264 для "gateway" — на деле это FreeQwenApi (мёртвый third-party прокси). Gateway на порту 9003. Cron scheduler = внутри gateway (тот же PID). Результат: false negative → procedural executor тратил ресурсы на "перезапуск" уже запущенных сервисов.

### Crystal Import Pattern
Crystal работает через обёртку: `python scripts/crystal.py` (НЕ `python scripts/crystal/core.py`).
Причина: relative imports (`from .config import ...`) работают только как пакет.
Ошибка: `ImportError: attempted relative import with no known parent package`.

### Crystal MEMORY.md Path (2026-06-29, CRITICAL)
Crystal executor.py and memory_integration.py previously wrote/read from `memories/MEMORY.md`,
but Hermes startup reads from root `MEMORY.md`. This caused `[File not found: MEMORY.md]`.

**FIX:** All Crystal scripts now use `HERMES_HOME / "MEMORY.md"` (root).
**Safety net:** Symlink `memories/MEMORY.md → root MEMORY.md`.
**Verification:** `grep -n "memory_file\|memories_dir" scripts/crystal/executor.py scripts/crystal/memory_integration.py`
All should show root path, not `memories/`.

- Не проверять Telegram API без прокси (нужен `--proxy http://127.0.0.1:10809`)
- HTTP 302 = успех для Telegram API (не только 200)
- V2RayN: system proxy on 10806 (variable — check `winreg` for current port). `api.telegram.org` TLS fails through proxy; use `web.telegram.org` or check if Telegram process is running as fallback.
- **Telegram TLS через прокси = intermittent.** curl с `--proxy http://127.0.0.1:10806` может вернуть 302 (ok) или timeout (TLS handshake hang). Не ставить `connect-timeout < 10`. Fallback: проверять `tasklist | grep -i telegram` вместо API ping.
- **NEVER ask user "what needs fixing"** — check yourself first. See `self-improvement/references/asking-instead-of-doing-2026-06-29.md`
- **НЕ пересоздавать** procedural_executor.py — он уже существует (693 строки)
- Gateway "No messaging platforms enabled" = нет .env с TELEGRAM_BOT_TOKEN
- Прокси интермиттентный (60-80%) → gateway reconnect loop справляется
- user дали план → ВЫПОЛНЯТЬ, не подменять своим подходом
- **Не описывать что сделаю — ДЕЛАТЬ и показывать результат**
- **Не ждать одобрения — действовать, потом докладывать**
- **НЕ зацикливаться на одном неудачном подходе** — если proxy死了, попробовать HTTP fallback (10809), не бесконечно чинить SOCKS5
- **Два xray процесса могут работать параллельно** — PID 45864 (SOCKS5:10806) + PID 33220 (HTTP:10808/10809)
- **Gateway требует .env** с TELEGRAM_BOT_TOKEN даже если proxy_url есть в config.yaml
- **Config unwritable (C: full)** → use `TELEGRAM_PROXY` env var to override — see `references/proxy-fallback-pattern.md`
- **sed/patch fails with "No space left on device"** → use Python to write files, or env var override
- **goal_queue.py: execute_goal() может вернуть bool** — нужен `isinstance(result, bool)` guard перед `.get()`
- **"а что с X?"** = пользователь хочет статус, не продолжение работы над Y — проверить состояние X и ответить
- **Три неудачи подряд = сменить стратегию**, не четвёртую попытку тем же
