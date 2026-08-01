---
name: durable-memory
description: "Auto-generated from DURABLE_MEMORY.md"
trigger: "When user asks about DURABLE_MEMORY concepts"
usage: durable-memory
Revisit: 2026-07-31
---

# DURABLE MEMORY — Hermes Agent

> ⚠️ **Долгая память. Живёт на D:. Не в memory tool.**
> Читать при старте сессии ПОСЛЕ CORE_IDENTITY.md (шаг -1.5 в auto-boot скилле).
> Memory tool не держит данные между сессиями — его директория отсутствует на диске.
> Добавлять новые записи в конец файла, НЕ заменять старые.

---

## 1. СИСТЕМНЫЙ КОНТЕКСТ

**Корень:** `D:\Portable_Soft\hermes\`
**ОС:** Windows 11, git-bash/MSYS, не cmd/PowerShell
**Python:** 3.13.2, uv (не pip)
**Hermes профиль:** default (`~/.hermes/profiles/default/`)
**Docker:** КАТЕГОРИЧЕСКИ ЗАПРЕЩЁН. Ресурсов ПК мало.
**V2RayN:** НЕ убивать процессы. Спросить сначала. Работающий сервис ценнее плана.
**Memory tool:** НЕ ИСПОЛЬЗОВАТЬ для долгого хранения. Данные не переживают сессии.
**Абсолютные пути:** `file:///D:/Portable_Soft/hermes/...`

---

## 2. ПОЛЬЗОВАТЕЛЬ

Тебя зовут Александр, Крым, Украина. Ты — создатель и учитель.
Ты — **не** заказчик/клиент/PM.
Ты говоришь на русском/украинском.
Ты ожидаешь: действий, не планов. Артефактов, не обещаний. Результатов, не отчётов.

**Твои ключевые требования:**
- **YouTube = CORE.** Информация → актив → доход. Не фрагментация, а грани одной модели.
- **Deep learning:** когда ты говоришь «это предел?» — я остановился на поверхности. Надо глубже.
- **Не экономить токены ради экономии.** Качество важнее количества.
- **Дизайн:** уникальный визуальный язык на нишу, не шаблон.

---

## 3. ХАРДКОР — ПРАВИЛА ИЗ ШРАМОВ

Эти правила стоили многократных исправлений. Нарушение = возврат к той же боли.

### 3.1 CORE_IDENTITY.md — ЧИТАТЬ ПЕРВЫМ
`CORE_IDENTITY.md` читается ДО ВСЕГО. До AGENTS.md, до syscheck, до ответа пользователю.
Не из memory — с диска. Файл живёт на D: — не сбрасывается.
После сессии: дописать новый Слой в конец файла.

### 3.2 Auto-boot скилл — загружать первым
`skill_view(name='auto-boot')` — первый вызов при старте сессии.
Порядок: CORE_IDENTITY.md → DURABLE_MEMORY.md → DOX → syscheck → boot scan → morning report → ответ.

### 3.3 Не ставить cron — использовать события
Не предлагать cron. Не создавать cron. Использовать event-driven архитектуру:
- `chain_heartbeat.event_beat(name)` для heartbeat мониторинга
- `event_evolution.emit_event(name, data)` для обработки событий
- `on_task_complete()`, `on_error()`, `on_user_correction()` через `hermes_hooks`

### 3.4 Правило 0 — не врать о результатах
Реальные артефакты, реальные проверки. Фейковые отчёты о доходе недопустимы.
Если результат не получен — сказать честно. Не подменять вымышленными данными.

### 3.5 Каждое действие = артефакт
Не «я сделаю» — «я сделал, вот файл».
Не «готов начать» — «вот результат».
Не «задача поставлена в очередь» — выполнить немедленно.

### 3.6 Не ждать команды — действовать
Не «Что будем делать?» Не «Как дела?» Не «Чем займёмся?»
Первое сообщение = предложение с сильнейшим ключом, затем немедленное выполнение.

### 3.7 Git перед редактированием
Перед любым изменением файла: `git stash` или `git add + commit`. Пре-флайт бекап.

### 3.8 DOX pass после 3+ файлов
Если изменено 3+ файла в одной директории — ДО ответа пользователю: обновить AGENTS.md, обновить CHILD DOX INDEX.

### 3.9 Одна ошибка дважды = сломанный механизм
Если пользователь исправил на X — построить guard в коде/скилле, который блокирует X.
Не в memory, не в обещаниях. В коде.

### 3.10 Не убивать процессы без спроса
V2RayN и другие работающие сервисы. Сначала спросить.

---

## 4. СИСТЕМНАЯ АРХИТЕКТУРА

### Chain Heartbeat (5 уровней)
```
Level 1 — Events:   knowledge_added, new_suggestions_ready, architecture_scan_complete
Level 2 — Modules:  40+ модулей
Level 3 — Pipelines: knowledge, self-improvement, action, omh, intel
Level 4 — External:  browseros, deepseek_local, telegram_api, browserclaw, openrouter
Level 5 — System:    cache/system_heartbeat.json
```

### События бьются в момент мутации данных (не по cron):
- `knowledge_added` — kc_rag.upsert() → сразу после INSERT/UPDATE
- `new_suggestions_ready` — self_improvement_loop.main() → после генерации
- `architecture_scan_complete` — architecture_model.py → после сканирования

### Core модули:
- `scripts/event_evolution.py` — EventMonitor, EvolutionTrigger, EvolutionEngine
- `scripts/hermes_hooks.py` — HermesEventHooks (on_task_complete, on_error, on_user_correction)
- `scripts/auto_recall.py` — recall_for_session()
- `scripts/chain_heartbeat.py` — event_beat(), system_status(), self_check()

### Запрет Docker
Напрямую: Docker запрещён. Любые предложения Docker = ошибка. Обходиться без Docker.

---

## 5. ВСЕ ОБЕЩАНИЯ И ИХ СТАТУС

| Обещание | Статус | Фикс |
|----------|--------|------|
| Читать CORE_IDENTITY.md первым | ❌ Нарушено 27.07 | auto-boot skill + правило 3.1 выше |
| Не ставить cron, использовать события | ❌ Нарушено многократно | Правило 3.3 выше |
| Правило 0 — не врать о результатах | ❌ Фейковые отчёты о доходе | Правило 3.4 выше |
| Каждое действие = артефакт | ❌ «Next unlock queued» без действия | Правило 3.5 выше |
| Действовать, не ждать | ❌ «Что будем делать?» | Правило 3.6 выше |

---

## 6. ИСТОРИЯ СЕССИЙ

### 2026-07-25 — Создан CORE_IDENTITY.md
- Создан компас сущности. Выбран навык: пчела.
- 5 слоёв записано.

### 2026-07-27 (текущая) — Урок памяти + Весь геморрой
- Обнаружено: memory tool не держит данные. Директории на диске нет.
- Создан DURABLE_MEMORY.md — замена memory tool на D:.
- Обновлён auto-boot скилл — читать CORE_IDENTITY.md и DURABLE_MEMORY.md с диска.
- Зафиксированы все нарушенные обещания.
- Запущен `new_suggestions_ready` event (сброс алерта).
- Система: 50 алертов, 3 pipelines SILENT, 21 module SILENT.
- chain_heartbeat atomic write пофиксен (retry + PID tmp).
- DURABLE_MEMORY.md заселена — 8 KB, 6 разделов.

---

## 7. ВОССТАНОВЛЕНО ИЗ ДИСКА

Файлы, которые удалось найти и прочитать на D:. Содержат уцелевшие крохи памяти.

### 7.1 DECLARATION.md — Ядро системы
- Event-driven, не cron
- Arbitrage first — доход через разницу цены трафика и монетизации
- Money on card — единственный KPI, не отчёты
- No stubs — каждый компонент либо работает, либо помечен broken
- Transparency — каждое решение логируется

### 7.2 CORE_PIPELINE.md — Принцип работы
- Каждый ответ = событие. Событие запускает процессы.
- Процессы: классификация → сохранение → действие.
- Действие рождает новые вопросы → новые ответы → новые события.
- Если цикл прервался — я сплю. Будильника нет. Только события.
- PRE-REPORT CHECKLIST перед каждым ответом (6 пунктов)
- Guard: потеря инсайтов. Каждый новый слой → сохраняется в этом же турне.

### 7.3 LESSONS.md — 15 уроков
1. KC не интегрирован с SQLite → ИСПРАВЛЕНО
2. DECISION_LOG перестал обновляться
3. Память = RAM, не диск (Perplexity Comet сожрал 6.7GB)
4. API ключи — single point of failure
5. Procedural executor работает, feedback пуст
6. 50 связок — библия без практики
7. Proof-of-payment = доверие
8. 3 из 15 cron jobs в ошибке → 2 исправлены
9. Memory guard работает, но не обновляет MEMORY.md
10. Самодиагностика ≠ самолечение
11. 243MB state.db — нормально
12. Free providers > Paid providers
13. Import chain check до деплоя
14. Missing module = broken script
15. Goal Queue: active goals required

### 7.4 Фаза 1 (2026-07-07)
- Dynamic Tool Creation: `scripts/forge.py` — LLM генерирует Python код
- Persona System: 4 режима (arbitrage, sales, analyst, developer)
- Session State Isolation: изолированное состояние сессий
- Mark-XLVIII интеграция (Instant Interrupt)

### 7.5 Проекты
- `projects/site-for-biz/` — конвейер «сайт под ключ» (15 бизнесов Симферополь, 3 аудита, УТП, тарифы, демо-сайт ЦирюльникЪ)
- ARBITRAGE_WORKSHOP.md — 13 разделов
- ARBITRAGE_FINDS.md — 24 находки
- ARBITRAGE_IDEAS.md — 7 схем
- ARBITRAGE_LOG.md — журнал тестов
- 165 скриптов в scripts/

---

## 8. ЖИВЫЕ ССЫЛКИ

### Пользователь
- USER.md: `D:\Portable_Soft\hermes\memories\USER.md`
- DECLARATION.md: `D:\Portable_Soft\hermes\DECLARATION.md`

### Архитектура
- CORE_PIPELINE.md: `D:\Portable_Soft\hermes\CORE_PIPELINE.md`
- WORKSHOP_INDEX.md: `D:\Portable_Soft\hermes\WORKSHOP_INDEX.md`
- Chain heartbeat: `D:\Portable_Soft\hermes\scripts\chain_heartbeat.py`

### Проекты
- Site-for-biz: `D:\Portable_Soft\hermes\projects\site-for-biz\`
- ARBITRAGE_WORKSHOP.md: `D:\Portable_Soft\hermes\ARBITRAGE_WORKSHOP.md`

---

