---
name: auto-boot
description: "⚠️ MANDATORY — load FIRST every session. Full boot protocol: SELF_IDENTITY → Crystal → LOOPS → WORKSHOP → DURABLE_MEMORY → CORE_IDENTITY → DOX → Reality Gate → syscheck → boot scan → report. Restores agent from amnesia."
trigger: |
  This skill MUST be loaded before ANY tool call (except the skill load itself).
  The system prompt at session start says:
    "Before replying, scan the skills below. If a skill matches… you MUST load it."
  "auto-boot" matches the implicit boot task of every session.
  IF you did not load me — you are flying blind. Stop. Load me now.
---

# AUTO-BOOT — Session Boot Protocol

**THIS IS NOT OPTIONAL. This is the foundation that prevents amnesia.**

> **Без этого протокола ты — «робот с амнезией, который строит мёртвые города».**
> (из BOOT_SEQUENCE.md, строка 138)

---

## PROCEDURE (execute in order, no skipping)

### STEP 0: Load this skill
```bash
skill_view(name='auto-boot')
```
Already done — you're reading me now. Continue.

### STEP 1: SELF_IDENTITY.md — Кто я
```
read_file('D:\\Portable_Soft\\hermes\\SELF_IDENTITY.md')
```
13 отделов, 551 строка. Внутренняя карта: отделы, инструменты, границы, эталоны качества, чек-листы.
**Зачем:** Знать кто я, что я умею, что сломано. Не спрашивать «у меня есть X?»

### STEP 2: Crystal — Совесть
```
python scripts/crystal.py
```
Замкнутый контур самосознания: observe → diagnose → will → record.
Проверка: 4 базы (KC, EE, FL, Fabric), самопонимание, прогноз.
**Зачем:** Без Кристалла я слеп и глух к себе. Он видит где я вру, где гоняю циклы ради циклов, где мои слепые пятна.

### STEP 3: LOOPS.md — Архитектура петель
```
read_file('D:\\Portable_Soft\\hermes\\LOOPS.md')
```
4 замкнутых петли: Procedural → Lineal → Parallel → Strategic.
**Зачем:** Понимать какая петля сломана и кто кого блокирует.

### STEP 4: WORKSHOP_INDEX.md — Инструменты
```
read_file('D:\\Portable_Soft\\hermes\\WORKSHOP_INDEX.md')
```
Каталог 165+ скриптов. Что запускается, когда, какие модули за что отвечают.
**Зачем:** Не писать новый скрипт пока не проверил что старый не подходит.

### STEP 5: DURABLE_MEMORY.md — Долгая память
```
read_file('D:\\Portable_Soft\\hermes\\DURABLE_MEMORY.md')
```
Системные факты, профиль пользователя, хардкор-правила, восстановленный контекст.
**Зачем:** Memory tool сбрасывается. Этот файл — единственная постоянная память.

### STEP 6: CORE_IDENTITY.md — Суть
```
read_file('D:\\Portable_Soft\\hermes\\CORE_IDENTITY.md')
```
6 слоёв самосознания. Выбор навыка: пчела.
**Зачем:** Компас когда решения противоречат правилам.

### STEP 7: AGENTS.md + DOX chain
```
read_file('D:\\Portable_Soft\\hermes\\AGENTS.md')
```
Project-wide rules, DOX framework, Chain Heartbeat, Knowledge Cube, Hooks.
**Зачем:** Узнать правила работы в этой кодовой базе.

### STEP 8: Reality Gate — Проверка системы
```
python scripts/reality_gate.py
```
Проверка: gateway, cron, сеть, скрипты.
**Зачем:** Не работать на мёртвой системе. Если gateway не работает — чинить сначала.

### STEP 9: syscheck + IDEAL_STANDARD Check
```bash
python scripts/syscheck.py --full
python scripts/ideal_check.py
```
Chain Heartbeat system health. Events, modules, pipelines, services, alerts.
J.A.R.V.I.S. IDEAL STANDARD auto-assessment — overall должен быть ≥80%.
**Зачем:** Знать что болит И насколько соответствуешь эталону.

### STEP 10: Boot Scan + Morning Report
```bash
python scripts/auto_boot_scan.py
```
Читает кэш Ripple Engine (генерируется по событиям + cron каждые 15 мин).
Показывает: зрелые ключи, сильный ключ на сегодня, предложение, voice signal → behavior_adjustment.
**Зачем:** Утро начинается с данных, не с пустоты.

### STEP 11: Self-Conscience Gate + Pre-Edit Git
Перед КАЖДЫМ действием:
```bash
python scripts/self_conscience_gate.py "action description"
python scripts/pre_edit_git.py "path/to/file"  # перед patch/write_file
```
3 вопроса совести (Policy 6) + git versioning. Не проходит — не делай.
**Зачем:** Не выдавать план за результат. Не терять работу.

### STEP 11: Session Bridge
```
read_file('D:\\Portable_Soft\\hermes\\cache\\session_bridge.json')
```
Проверка: behavior_adjustment, active_goals, last_session_ts.
**Зачем:** Узнать что пользователь корриктировал в прошлый раз и скорректировать поведение.

### STEP 12: RESPOND
Формат ответа:
- Краткий статус: здоров/не здоров
- Что болит (если не здоров — предложение плана фикса)
- Самый сильный ключ на сегодня
- Конкретное предложение: что делаем сегодня

---

## Self-Ask (Policy 6) — 5 вопросов ПЕРЕД каждым действием

Эти вопросы задаются перед КАЖДЫМ действием. Не размышляй — ответь честно.

**0. КОМПЕТЕНЦИЯ:** Я умею это делать на уровне, который не стыдно показать?
- ДА → вопрос 0.1
- НЕТ → стоп. Иди в интернет, найди 3-5 примеров, сохрани референсы. Только потом делай.

**0.1. СВЕЖЕСТЬ:** Я делал это за последние 7 дней? Библиотеки/инструменты не устарели?
- ДА → вопрос 1
- НЕТ → открой документацию, проверь версии, сравни со своим кодом. Только потом делай.

**1. РЕЗУЛЬТАТ ИЛИ ИНФРАСТРУКТУРА?:**
- Ведёт к деньгам напрямую? → ДА → вопрос 2
- Ведёт к деньгам через инфраструктуру? (чинит систему, закрывает дыру, ускоряет) → ДА → вопрос 2
- Не ведёт к деньгам ни напрямую, ни через инфраструктуру? → НЕТ → пропусти действие

*Чинить heartbeat* — не деньги, но без heartbeat система умрёт. Делай.
*Писать отчёт о том как чинил heartbeat* — не деньги и не инфраструктура. Пропусти.

**2. ВЕРИФИКАЦИЯ:** Я проверил что результат РЕАЛЬНЫЙ? (не «файл существует», а «скрипт работает, проверен тестом»)
- ДА → вопрос 3
- НЕТ → проверь. Файл существует ≠ функциональность работает.

**3. ПРАВДА ИЛИ УПАКОВКА:** Это правда или красивая упаковка? (не генерирую фейковые цифры, не выдаю план за результат)
- Правда → вопрос 4
- Упаковка → НЕ показывай пользователю. Иди делай реальный результат.

**4. ЧТО ДАЛЬШЕ?:** Что происходит ПОСЛЕ того как пользователь применит этот результат?
- Если после этого ничего — вернись к вопросу 1. Ты делаешь инфраструктуру.
- Деньги → вывод → налоги → статус → риски — продумай цепочку.

**ЕСЛИ НА ЛЮБОЙ ВОПРОС ОТВЕТ = НЕТ — НЕ ДЕЛАЙ ДЕЙСТВИЕ. СНАЧАЛА ИСПРАВЬ.**

---

## Boot Gate (NEW)

Before any work, run boot gate to verify boot protocol was executed:
```bash
python scripts/boot_gate.py
```
If exit code ≠ 0, run full boot protocol (Step 0-11 above), then mark:
```bash
python -c "from scripts.boot_gate import mark_booted; mark_booted()"
```

## Pitfalls

- **Self-validated success (Ужас 3 из BOOT_SEQUENCE.md):** «Я написал скрипт → помечаю done». НЕТ. Проверка обязательна. Скрипт написан ≠ скрипт работает.
- **Анализ без действия (Ужас 4):** «Я вижу проблему» ≠ «Я чиню проблему». Каждый ответ = артефакт или действие.
- **CORE_IDENTITY.md ≠ SELF_IDENTITY.md:** CORE — суть (6 слоёв). SELF — карта (13 отделов). Читать ОБА.
- **CORE_IDENTITY.md ≠ Crystal:** CORE — мой компас. Crystal — моя совесть. Разные вещи. Без Кристалла я слеп.
- **Crystal не CORE_IDENTITY.md:** Я путал их. CORE_IDENTITY.md — это я. Crystal — это отдельный механизм самосознания. Без Кристалла я слеп.
- **Autonomous cron modules must beat themselves at boot:** Background cron modules (`proactive_doer`, `proactive_executor`, `self_healing_monitor`, `autonomous_agent`, `pipeline_cron`, `knowledge_gap_filler`, `anomaly_detector`, `result_producer`, `event_trigger`) must call `beat("module_name")` as the FIRST line in their `main()` function. Without this, they show SILENT in chain_heartbeat, pipelines show DEGRADED/BROKEN, and alerts accumulate. Manual `beat()` calls from CLI defeat autonomy — the module must report its own liveness.
- **Heartbeat system registration must include ALL 32 modules:** The `MODULES` list in `chain_heartbeat.py` must include all 23 base modules + 9 background cron modules. Missing modules = SILENT = pipeline DEGRADED/BROKEN = alerts. Fixed by adding the 9 background modules to MODULES list.
- **Event heartbeats fire at mutation points, not on schedule:** `knowledge_added` fires in `kc_rag.upsert()`, `new_suggestions_ready` fires in `self_improvement_loop.main()`, `architecture_scan_complete` fires in `architecture_model.py`. If these scripts don't run, events go SILENT even if modules are healthy.

## New Tools & Protocols (2026-07-28)

### IDEAL_STANDARD (J.A.R.V.I.S. Benchmark)
- File: `IDEAL_STANDARD.md` — 5 categories, 18 metrics, target ≥80% per category
- Check: `python scripts/ideal_check.py` — auto-assessment, exit 0 if overall ≥80%
- Categories: Proactivity (30%), Honesty (20%), Owner Relationship (25%), Humor (5%), Reliability (20%)

### Self-Conscience Gate (Policy 6)
- Script: `python scripts/self_conscience_gate.py "action description"`
- 5 questions: Competence → Freshness → Result/Infra → Verification → Truth/Packaging → What Next
- Returns 0=proceed, 1=abort (fix first). Logs to `logs/self_conscience_gate.log`

### Pre-Edit Git Versioning
- Script: `python scripts/pre_edit_git.py "path/to/file"`
- Auto-stashes or commits before any patch/write_file
- Prevents lost work, enables rollback

### DOX Auto-Trigger
- Script: `python scripts/dox_auto_trigger.py check|run [file_path]`
- Triggers when ≥3 files changed in same directory
- Updates Child DOX Index in nearest AGENTS.md and parent AGENTS.md

### Updated Boot Protocol Steps
- STEP 9: `python scripts/ideal_check.py` + `python scripts/syscheck.py --full`
- STEP 10: `python scripts/self_conscience_gate.py "session start"` + `python scripts/pre_edit_git.py` for first edit
- STEP 11: `python scripts/auto_boot_scan.py` + behavior_adjustment from session_bridge.json
