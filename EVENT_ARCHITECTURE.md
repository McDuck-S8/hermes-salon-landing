---
name: event-architecture
description: "Auto-generated from EVENT_ARCHITECTURE.md"
trigger: "When user asks about EVENT_ARCHITECTURE concepts"
usage: event-architecture
Revisit: 2026-07-31
---

# EVENT ARCHITECTURE — Hermes Event-Driven External Loop

**Статус:** PRODUCTION (все компоненты активны)  
**Дата:** 2026-06-29  
**Источник:** Loop Engineering (Addy Osmani) + Hermes реализация

---

## Архитектура (WHAT)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL LOOP (Loop Engineering)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │   SENSORS    │───▶│ EVENT CLASSIF│───▶│  EVENT BUS   │───▶│ CHAINS   │  │
│  │  (вход)      │    │  (оценка)    │    │  (шина)      │    │ (логика) │  │
│  └──────────────┘    └──────────────┘    └──────────────┘    └────┬─────┘  │
│                                                                    │        │
│                                                    ┌───────────────┼───────┐│
│                                                    ▼               ▼       ▼│
│                                           ┌──────────────┐ ┌────────┐ ┌────┐│
│                                           │PROCEDURAL    │ │RD/DEV  │ │CRON││
│                                           │REFLEXES      │ │PROCESS │ │ACT ││
│                                           │(no LLM)      │ │(Bayes) │ │IONS││
│                                           └──────────────┘ └────────┘ └────┘│
│                                                                    │        │
│                                                    ┌───────────────┼───────┐│
│                                                    ▼               ▼       ▼│
│                                           ┌──────────────┐ ┌────────┐ ┌────┐│
│                                           │ DELEGATE_    │ │ WORK-  │ │NOTI││
│                                           │ TASK         │ │ SHOP   │ │FICA││
│                                           │ (subagents)  │ │ (queue)│ │TION││
│                                           └──────────────┘ └────────┘ └────┘│
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    MEMORY / STATE (External Truth)                   │   │
│  │  session_context  │  MEMORY.md  │  fabric  │  knowledge_cube  │ events│
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Компоненты (HOW)

### 1. SENSORS — входные точки

| Файл | Источник | Частота / Триггер | Выходной event |
|---|---|---|---|
| `signal_daemon.py` | HN (algolia), GitHub Trending | Adaptive backoff: 60с ↔ 10мин | `new_external_signal` |
| `sensor_array.py` | System metrics (CPU, RAM, Disk), process health, file watchers, error log tail | Continuous / on-change | `system_metric`, `process_event`, `file_change`, `error_detected` |
| `event_classifier.py` | Raw signals (webhook, manual, API) | On-demand | `typed_event` (classified) |
| `cron/scheduler.py` | Time-based | Per `cron/jobs.json` | `cron_tick:<job_id>` |

**signal_daemon adaptive backoff:**
```python
# Псевдокод
if new_signals_found:
    backoff = 60  # секунд
else:
    backoff = min(backoff * 1.5, 600)  # до 10 мин
```

---

### 2. EVENT CLASSIFICATION — Bayesian Scorer

**Файл:** `scripts/bayesian_scorer.py`  
**Формула:** `P(H|E) = P(E|H) * P(H) / P(E)`

| Use case | Hypothesis H | Evidence E | Threshold |
|---|---|---|---|
| `signal_scanner` | "Сигнал релевантен для workshop" | title, source, keywords | score < 0.3 → reject |
| `rd_processor` | "Сигнал → research task" | content, domain match | score > 0.6 → queue |
| `dev_processor` | "Сигнал → dev task" | tech keywords, actionability | score > 0.5 → queue |
| `daily_metrics` | "Flow alive" | recent actions, goals progress | P(flow_alive) > 0.7 |

**CLI:** `python scripts/bayesian_scorer.py --status|--score|--history`

---

### 3. EVENT BUS — шина + демон

| Файл | Роль |
|---|---|
| `event_bus.py` | `emit(event)`, `subscribe(pattern, handler)`, `event_log.jsonl` (persisted) |
| `event_daemon.py` | Background: потребляет `event_queue`, диспатчит в chains |
| `event_reactor.py` | Pattern matching: `event.type == "X" → action Y` |

**DIRECT_EVENT_HANDLERS** (bypass queue, immediate):
```python
# В event_daemon.py
DIRECT_EVENT_HANDLERS = {
    "new_external_signal": ["rd_processor", "dev_processor"],
    "system_critical": ["procedural_executor"],
}
```

---

### 4. CHAINS — логика реакции

| Тип | Файл | Описание |
|---|---|---|
| **Procedural Reflexes** | `procedural_executor.py` | Детерминированные цепочки БЕЗ LLM. Паттерны: порт мёртв→kill→restart→check, disk>80%→find large→log, mem>80%→find procs→log, gateway down→log→escalate, API key expired→refresh→fallback |
| **RD Processor** | `rd_processor.py` | `new_external_signal` → Bayesian score → `ARBITRAGE_WORKSHOP.md` (research queue) |
| **Dev Processor** | `dev_processor.py` | `new_external_signal` → Bayesian score → dev task queue (implementation) |
| **Event Reactor** | `event_reactor.py` | Generic pattern→action mapping из `event_registry.json` |

**Procedural Skills** (из `skills/PROCEDURAL_SKILLS.md`):
- `port_dead` → `kill_process` → `restart_service` → `verify_port`
- `disk_high` → `find_large_files` → `log_alert` → `cleanup_candidates`
- `memory_high` → `find_memory_procs` → `log_alert`
- `gateway_missing` → `log_alert` → `escalate`
- `api_key_expired` → `refresh_token` → `fallback_provider`

---

### 5. ACTIONS — исполнение

| Действие | Механизм | Для чего |
|---|---|---|
| `delegate_task` | Subagent (leaf/orchestrator) | Maker-Checker, параллельные задачи |
| `cronjob create/update` | Dynamic cron | Реактивное планирование |
| `proactive_doer` | Fix executor | Автономный ремонт (stale locks, broken JSON, failed jobs) |
| `notification` | Gateway (Telegram, etc.) | Human-in-the-loop |

---

### 6. MEMORY / STATE — внешняя истина

| Хранилище | TTL | Содержимое | Читает |
|---|---|---|---|
| `cache/event_bus.json` | Session | Event bus state, subscriptions | `event_daemon` |
| `cache/signals_processed.json` | Forever | Dedup сигналов (SHA256) | `signal_daemon`, `rd_processor` |
| `session_context` | Session | Boot context, goals, needs | `hermes_start.py`, agents |
| `MEMORY.md` | Forever | Agent memory (self-corrections, patterns) | `memory_guard.py`, boot |
| `fabric` | Forever | Cross-session, cross-agent knowledge | `fabric_*` tools |
| `knowledge_cube` | Forever | Structured knowledge, embeddings | `knowledge_cube.py`, `session_recall` |

---

## Трассировка события (END-TO-END)

### Сценарий: Новый тренд на GitHub → Research Task в Workshop

```
┌────────────────────────────────────────────────────────────────────────────┐
│ TIMELINE                                                                     │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│ T+0s    signal_daemon.py                                                   │
│         ├─ Poll GitHub Trending API                                        │
│         ├─ Found: "awesome-ai-agents" (new, 500★ today)                   │
│         ├─ Compute SHA256(title+url) → check cache/signals_processed.json │
│         ├─ NEW → emit("new_external_signal", {                             │
│         │     source: "github_trending",                                   │
│         │     title: "awesome-ai-agents",                                  │
│         │     url: "https://github.com/...",                               │
│         │     stars_today: 500,                                            │
│         │     ts: "2026-06-29T10:00:00Z"                                   │
│         │ })                                                               │
│         └─ Write SHA256 to cache/signals_processed.json                   │
│                                                                            │
│ T+0.1s  event_bus.py (emit)                                                │
│         ├─ Append to event_log.jsonl                                       │
│         ├─ Match DIRECT_EVENT_HANDLERS["new_external_signal"]             │
│         │    → ["rd_processor", "dev_processor"]                          │
│         └─ Sync call both processors (non-blocking)                       │
│                                                                            │
│ T+0.2s  rd_processor.py (DIRECT handler)                                   │
│         ├─ Bayesian score: P(relevant|signal)                             │
│         │   Evidence: "ai agents" in title, GitHub source, 500★           │
│         │   Prior: 0.7 (GitHub trending historically relevant)            │
│         │   Score: 0.84 → PASS (>0.6)                                     │
│         ├─ Create research task:                                          │
│         │   {type: "research", topic: "awesome-ai-agents",                │
│         │    source: "github_trending", priority: 8,                       │
│         │    url: "...", context: {...}}                                   │
│         ├─ Append to ARBITRAGE_WORKSHOP.md (research queue section)       │
│         └─ Emit "research_task_created"                                   │
│                                                                            │
│ T+0.2s  dev_processor.py (DIRECT handler)                                  │
│         ├─ Bayesian score: P(actionable|signal)                           │
│         │   Evidence: "agents" = tech, could integrate                    │
│         │   Score: 0.52 → PASS (>0.5)                                     │
│         ├─ Create dev task:                                               │
│         │   {type: "dev", title: "Integrate awesome-ai-agents patterns",  │
│         │    source: "github_trending", priority: 5}                      │
│         ├─ Append to dev queue (cache/dev_queue.json)                     │
│         └─ Emit "dev_task_created"                                        │
│                                                                            │
│ T+1s    event_reactor.py (pattern match)                                   │
│         ├─ Sees "research_task_created"                                   │
│         ├─ Matches rule: research_task → notify_telegram                  │
│         └─ Queue notification                                             │
│                                                                            │
│ T+15m   cron: proactive-doer (runs every 15 min)                          │
│         ├─ Checks research queue                                          │
│         ├─ Sees new high-priority task                                    │
│         ├─ delegate_task(role=orchestrator, goal="Research awesome-ai-   │
│         │   agents patterns for Hermes integration")                      │
│         │   → spawns maker (research) + checker (verify findings)         │
│         └─ Results → ARBITRAGE_WORKSHOP.md (findings section)             │
│                                                                            │
│ T+1h    Autonomous agent (next boot)                                      │
│         ├─ hermes_start.py boot                                           │
│         ├─ session_boot: ingests new research findings                    │
│         ├─ goal_queue: new goal from findings                             │
│         └─ autonomous_action: executes or schedules                       │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Диаграмма состояний события

```
                    ┌─────────────────┐
                    │   RAW SIGNAL    │  (GitHub API response)
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  DEDUP CHECK    │  SHA256 in signals_processed.json
                    └────────┬────────┘
                             │ NEW
                             ▼
                    ┌─────────────────┐
                    │  EMIT EVENT     │  event_bus.emit("new_external_signal")
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌───────────────┐ ┌───────────┐ ┌───────────────┐
     │ DIRECT: RD    │ │ DIRECT:   │ │ EVENT REACTOR │
     │ PROCESSOR     │ │ DEV PROC  │ │ (patterns)    │
     └───────┬───────┘ └─────┬─────┘ └───────┬───────┘
             │               │               │
             ▼               ▼               ▼
     ┌───────────────┐ ┌───────────┐ ┌───────────────┐
     │ Bayesian      │ │ Bayesian  │ │ Match rules   │
     │ Score > 0.6?  │ │ Score>0.5?│ │ → notify      │
     └───────┬───────┘ └─────┬─────┘ └───────┬───────┘
             │ YES           │ YES           │
             ▼               ▼               ▼
     ┌───────────────┐ ┌───────────┐ ┌───────────────┐
     │ Workshop      │ │ Dev Queue │ │ Telegram      │
     │ Research Task │ │ (cache)   │ │ notification  │
     └───────┬───────┘ └───────────┘ └───────────────┘
             │
             ▼
     ┌───────────────┐
     │ proactive-    │  (cron 15min)
     │ doer picks up │
     └───────┬───────┘
             │
             ▼
     ┌───────────────┐
     │ delegate_task │  (orchestrator → maker + checker)
     │ research      │
     └───────┬───────┘
             │
             ▼
     ┌───────────────┐
     │ Workshop      │  (findings persisted)
     │ Updated       │
     └───────┬───────┘
             │
             ▼
     ┌───────────────┐
     │ Next Boot →   │  (session_boot ingests)
     │ Autonomous    │
     └───────────────┘
```

---

## Конфигурация (настройка поведения)

### `cron/jobs.json` — расписание + event triggers (планируемое расширение)
```json
{
  "jobs": [
    {"id": "signal_daemon", "schedule": "adaptive", "script": "signal_daemon.py start"},
    {"id": "proactive_doer", "schedule": "15m", "script": "proactive_doer.py"},
    {"id": "self_assessment", "schedule": "6h", "script": "self_system.py --proactive"},
    {"id": "memory_watchdog", "schedule": "6h", "script": "memory_guard.py"},
    // FUTURE: event-driven cron
    // {"id": "on_research_task", "trigger": "event:research_task_created", "script": "..."}
  ]
}
```

### `config/event_registry.json` — паттерны реактора
```json
{
  "patterns": [
    {"event": "new_external_signal", "handler": "rd_processor", "direct": true},
    {"event": "new_external_signal", "handler": "dev_processor", "direct": true},
    {"event": "system_critical", "handler": "procedural_executor", "direct": true},
    {"event": "research_task_created", "action": "notify_telegram"},
    {"event": "dev_task_created", "action": "queue_dev_task"}
  ]
}
```

### `scripts/procedural_executor.py` — рефлексы (PROCEDURAL_SKILLS.md)
```yaml
# skills/PROCEDURAL_SKILLS.md
triggers:
  - name: "port_dead"
    condition: "netstat -tlnp | grep -q ':PORT' || true"
    chain: [kill_process, restart_service, verify_port]
  - name: "disk_high"
    condition: "df / | awk 'NR==2 {print $5}' | sed 's/%//' | test $(cat) -gt 80"
    chain: [find_large_files, log_alert, cleanup_candidates]
  - name: "memory_high"
    condition: "free | awk 'NR==2 {print int($3/$2*100)}' | test $(cat) -gt 80"
    chain: [find_memory_procs, log_alert]
  - name: "gateway_missing"
    condition: "! pgrep -f gateway"
    chain: [log_alert, escalate]
  - name: "api_key_expired"
    condition: "curl -s API_HEALTH | jq -r .error == 'expired'"
    chain: [refresh_token, fallback_provider]
```

---

## Метрики и наблюдаемость

| Метрика | Где смотреть | Норма |
|---|---|---|
| Events emitted/sec | `event_log.jsonl` | >0 (живая система) |
| Signal dedup rate | `signals_processed.json` growth | Low (new signals) |
| Bayesian score distribution | `bayesian_scorer.py --history` | Most >0.5 relevant |
| Procedural reflex triggers | `procedural_feedback.jsonl` | Rare (system healthy) |
| Research tasks created | `ARBITRAGE_WORKSHOP.md` queue | 1-5/day |
| Dev tasks created | `cache/dev_queue.json` | 1-3/day |
| Proactive-doer fixes | `proactive_doer.log` | 0-2/15min |
| End-to-end latency (signal→task) | Manual trace | <5s |

---

## Troubleshooting

| Симптом | Диагностика | Лечение |
|---|---|---|
| События не доходят до rd/dev processor | `event_bus.json` subscriptions пусты | Проверить `DIRECT_EVENT_HANDLERS` в `event_daemon.py` |
| Bayesian score всегда низкий | `bayesian_scorer.py --history` | Настроить priors / evidence keywords |
| Procedural рефлексы не срабатывают | `procedural_executor.py --status` | Проверить `PROCEDURAL_SKILLS.md` синтаксис |
| Signal daemon молчит | `signal_daemon.py status` | Проверить API keys, network, backoff state |
| Dedup блокирует новые сигналы | `signals_processed.json` size | Очистить старые записи (TTL) |

---

## Roadmap (Event-Driven Improvements)

- [ ] **Webhook endpoint** — `gateway/webhook` для GitHub/Telegram/Stripe inbound
- [ ] **Event replay CLI** — `python scripts/event_bus.py replay --from <ts> --to <ts>`
- [ ] **Dead letter queue** — failed events → `cache/event_dlq.jsonl` + retry logic
- [ ] **Event-driven cron** — `trigger: "event:name"` в `cron/jobs.json`
- [ ] **Visual event flow** — UI для трассировки event→chain→action (Mermaid/Graphviz)
- [ ] **Event schemas** — JSON Schema для каждого event type (validation на emit)
- [ ] **Distributed tracing** — correlation_id через всю цепочку (W3C traceparent)

---

## Ссылки на код

```
scripts/
├── signal_daemon.py          # HN/GitHub polling + adaptive backoff
├── sensor_array.py           # System sensors
├── event_classifier.py       # Raw → typed events
├── bayesian_scorer.py        # P(H|E) scoring
├── event_bus.py              # Emit/subscribe + log
├── event_daemon.py           # Background consumer + DIRECT handlers
├── event_reactor.py          # Pattern → action
├── rd_processor.py           # Research queue (DIRECT)
├── dev_processor.py          # Dev queue (DIRECT)
├── procedural_executor.py    # Reflexes (no LLM)
├── proactive_doer.py         # Autonomous fixes
├── goal_queue.py             # Task queue
├── goal_executor.py          # Execute goals
├── autonomous_agent.py       # Decision matrix
├── delegate_task             # Subagent spawning
└── session_recall.py         # BM25 history search
```

---

**Версия:** 1.0  
**Поддерживаемый:** Hermes Agent (автономная система)  
**Принцип:** Loop Engineering — External Loop fully implemented, Internal Loop autonomous.