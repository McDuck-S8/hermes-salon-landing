---
name: multi-agent-orchestration
description: "Multi-agent orchestration pattern for Hermes: Manager + specialized Workers with task queue, workflows, and honest validation."
version: 1.0.0
author: hermes
license: MIT
tags:
  - multi-agent
  - orchestration
  - worker-pattern
  - fleet-management
  - task-queue
  - workflow-engine
tools:
  - terminal
  - file
  - delegate_task
  - execute_code
inputs:
  - task_description
  - worker_type
  - workflow_name
  - context
outputs:
  - task_results
  - workflow_status
  - review_reports
---

# Multi-Agent Orchestration

Паттерн оркестрации множества специализированных агентов (воркеров) внутри Hermes. Вдохновлен FirstMate (fleet management), адаптирован для CLI-first архитектуры.

## Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│  Agent Manager (First Mate)                                 │
│  - Task queue (JSON)                                        │
│  - Worker registry                                          │
│  - Workflow engine (dependencies, parallel/sequential)      │
│  - Shared log: cache/agent_team.log                         │
└──────────────┬──────────────────────────────────────────────┘
               │ dispatches tasks
               ▼
┌─────────────────────────────────────────────────────────────┐
│  Worker Pool (Crewmates)                                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Review    │ │    Code     │ │  Content    │  ...      │
│  │  Worker     │ │  Worker     │ │  Worker     │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│  Все наследуют WorkerBase                                   │
└─────────────────────────────────────────────────────────────┘
```

## Компоненты

### 1. Agent Manager (`scripts/agent_manager.py`)
Оркестратор. CLI команды:
```bash
# Статус флота
python scripts/agent_manager.py --status

# Регистрация воркера
python scripts/agent_manager.py --register-worker review_001 --worker-type review_worker

# Создание задачи
python scripts/agent_manager.py --create-task "Create landing for beauty salon" --worker-type code_worker --priority 3

# Запуск воркфлоу
python scripts/agent_manager.py --workflow landing_review
```

### 2. Worker Base (`scripts/worker_base.py`)
Абстрактный базовый класс. Каждый воркер:
- Получает JSON task_data через stdin
- Возвращает JSON result через stdout
- Логирует в общий `cache/agent_team.log`
- Имеет доступ к чек-листам и Knowledge Cube

### 3. Специализированные Воркеры (`scripts/workers/`)
| Воркер | Тип | Задачи |
|--------|-----|--------|
| `review_worker.py` | review_worker | Ревью лендингов, кода, контента по чек-листам |
| `code_worker.py` | code_worker | Написание кода, инструментов, лендингов |
| `content_worker.py` | content_worker | Скрипты, хуки, видео-идеи (TODO |
| `arbitrage_worker.py` | arbitrage_worker | Поиск офферов, анализ CPA, настройка трекинга |
| `research_worker.py` | research_worker | Рынки, конкуренты, тренды, ниши |
| `general_worker.py` | general_worker | Общие задачи, тестирование |

## Воркфлоу (Workflows)

Определены в `agent_manager.py`:
- `landing_review` — Code Worker создаёт лендинг → Review Worker проверяет
- `arbitrage_pipeline` — Arbitrage находит оффер → Research анализирует → Content создаёт креативы

Зависимости задач передаются через `context.previous_task_id`.

## Честная валидация (Critical Pattern)

**Review Worker НЕ ставит фейковые 100/100**. Каждая проверка имеет конкретные критерии:

```python
# Плохо: lambda c: "guarantee" in c.lower()
# Хорошо:
trust_signals = ["money.back.guarantee", "refund.policy", "secure.checkout"]
trust_count = sum(1 for s in trust_signals if s.replace('.','') in content_lower.replace('.',''))
passed = trust_count >= 2
issue = None if passed else f"Only {trust_count}/2 trust signals found"
```

Правила честного ревью:
1. **Конкретные критерии** — не "есть слово", а "есть структура X с Y элементами"
2. **Детальные issues** — не "Missing: Trust", а "Only 0/2 trust signals found"
3. **Порог прохождения** — 70% (не 100%)
4. **Взвешенные проверки** — критичные (headline, cta) вес 2, остальные 1

## Файлы состояния

| Файл | Назначение |
|------|------------|
| `cache/task_queue.json` | Очередь задач со статусами |
| `cache/worker_registry.json` | Реестр зарегистрированных воркеров |
| `cache/agent_team.log` | Общий лог событий (JSONL) |
| `cache/landings/*.html` | Сгенерированные лендинги |
| `cache/*_checklist.json` | Результаты чек-листов |

## Использование

```python
# В коде агента
from scripts.agent_manager import AgentManager, WorkerType, TaskPriority

manager = AgentManager()
manager.register_worker(WorkerType.REVIEW, "review_001")
manager.register_worker(WorkerType.CODE, "code_001")

# Простая задача
task_id = manager.create_task(
    "Create landing for nutra offer",
    WorkerType.CODE,
    TaskPriority.HIGH,
    context={"niche": "nutra", "offer": "Keto trial $45"}
)
manager.dispatch_task(task_id)
result = manager.wait_for_completion([task_id])

# Воркфлоу
wf = manager.run_workflow("landing_review", [
    {"description": "Create landing", "worker_type": "code_worker", "priority": 3},
    {"description": "Review landing", "worker_type": "review_worker", "priority": 3, "context": {"checklist": "landing"}}
])
final = manager.wait_for_completion(wf["task_ids"])
```

## Pitfalls / Lessons Learned

1. **Context passing** — Review Worker должен получать `previous_task_id` в context, чтобы найти файл лендинга от Code Worker'а
2. **No fake scores** — Простые regex-проверки дают фальшивые 100%. Нужен конкретный парсинг HTML/JS
3. **Worker scripts must exist** — Manager падает с "Worker script not found" если файл отсутствует
4. **Russian responses** — Пользователь требует ответы на русском
5. **Honest review threshold** — 70% проходной балл, ниже = FAILED, агенту нужно дорабатывать

## OMH Skills Integration for Research & Planning Workflows (2026-07-25)

**Oh My Hermes** (`https://github.com/witt3rd/oh-my-hermes`) предоставляет композитные мульти-агентные скиллы, заменяющие ad-hoc паттерны сабагентов на структурированные, переиспользуемые воркфлоу.

### OMH Skills как специализированные Воркеры

| OMH Skill | Worker Role | Когда диспатчить |
|-----------|-------------|------------------|
| `omh-deep-research` | `research_worker` | Многофазный веб-исследование: decompose → parallel search → synthesize → verify citations |
| `omh-deep-interview` | `interview_worker` | Сократический интервью по требованиям с отслеживанием покрытия (vague idea → structured spec) |
| `omh-ralplan` | `planner_worker` | Консенсус-планирование: Planner → Architect → Critic debate until agreement |
| `omh-ralplan-driver` | `planner_driver` | Плейбук диспетчера для запуска `omh-ralplan` |
| `omh-ralph` | `executor_worker` | Верифицированное исполнение: implement → verify → iterate until done |
| `omh-ralph-driver` | `executor_driver` | Плейбук диспетчера для `omh-ralph` |
| `omh-ralph-task` | `task_executor` | Дисциплина одной задачи: envelope contract, file-scope rigidity, stash-verify-against-HEAD |
| `omh-autopilot` | `autopilot_worker` | Полный пайплайн: все три скилла end-to-end |
| `omh-triage` | `triage_worker` | Мульти-ролевой консенсус-триаж бэклога |

### Integration Pattern

```python
# Вместо ручного fan-out сабагентов для research:
# 9 queries × 3 subagents × BrowserClaw (timeout 600s)
# 
# Используем OMH pipeline:
# omh-deep-research → omh-deep-interview → omh-ralplan → omh-ralph
# 
# Или end-to-end: omh-autopilot

from scripts.agent_manager import AgentManager, WorkerType, TaskPriority

manager = AgentManager()

# Регистрируем OMH воркеров
manager.register_worker(WorkerType.RESEARCH, "omh_deep_research_01")
manager.register_worker(WorkerType.PLANNER, "omh_ralplan_01")
manager.register_worker(WorkerType.EXECUTOR, "omh_ralph_01")

# Research workflow
wf = manager.run_workflow("research_pipeline", [
    {"description": "Deep research: faceless YouTube automation AI 2024", 
     "worker_type": "research_worker", "priority": 3,
     "context": {"skill": "omh-deep-research", "queries": 9}},
    {"description": "Interview: clarify CPA funnel requirements", 
     "worker_type": "interview_worker", "priority": 3,
     "context": {"skill": "omh-deep-interview"}},
    {"description": "Consensus plan: CPA funnel architecture", 
     "worker_type": "planner_worker", "priority": 3,
     "context": {"skill": "omh-ralplan"}},
    {"description": "Verified implementation: Telegram bot + CPA offers", 
     "worker_type": "executor_worker", "priority": 3,
     "context": {"skill": "omh-ralph"}}
])

final = manager.wait_for_completion(wf["task_ids"])
```

### OMH Research Pipeline vs Manual Subagent Pattern

| Aspect | Manual Subagents | OMH Pipeline |
|--------|-----------------|--------------|
| Structure | Ad-hoc, per-session | Reusable, versioned skills |
| Planning | Implicit, in prompt | Explicit: Planner → Architect → Critic |
| Execution | Fire-and-forget | Verified: implement → verify → iterate |
| Cost envelope | Unpredictable | Bounded: 5-8 calls (up to 12 with retry) |
| Retry logic | Manual | Built-in 3-strike retry cap |
| Quality gate | Manual review | Verifier role in pipeline |

### Cost Envelope (omh-deep-research)
A typical happy-path session is roughly **5-8 `delegate_task` calls** (3-5 researchers + 0-1 followup + 1 synthesist + 1 verifier). With one synthesis retry, expect **up to ~10-12 calls**. The 3-strike retry cap bounds worst-case at ~14-16 calls before BLOCKED is surfaced.

## Agent Reach Integration for Data Extraction Workers (2026-07-25)

**Agent Reach** (`https://github.com/Panniantong/Agent-Reach`) дает каждому воркеру надежный интернет-доступ без overhead браузерной автоматизации.

### Worker Capabilities via Agent Reach

| Worker Type | Agent Reach Capabilities | Commands |
|-------------|-------------------------|----------|
| `research_worker` | YouTube search/transcripts, web search, GitHub, RSS, Exa | `yt-dlp`, `curl`, `gh`, `feedparser`, `mcporter` |
| `content_worker` | YouTube transcripts, Bilibili, Twitter, Reddit, RSS | `yt-dlp`, `opencli`, `bili`, `twitter`, `rdt` |
| `arbitrage_worker` | CPA network scraping, Telegram channels, competitor analysis | `yt-dlp`, `opencli` (Telegram), `feedparser` |
| `research_worker` (OMH) | YouTube as source in `omh-deep-research` synthesis | `yt-dlp` via `HermesWebAccess` |

### Worker Integration Pattern

```python
# In worker_base.py or worker scripts
from hermes_web_access import HermesWebAccess

class ResearchWorker(WorkerBase):
    def __init__(self):
        self.web = HermesWebAccess()  # Uses Agent Reach under the hood
    
    def execute(self, task_data):
        # OMH deep-research style: parallel YouTube searches
        queries = task_data.get("queries", [])
        all_results = []
        for q in queries:
            results = self.web.youtube_search(q, max_results=5)
            all_results.extend(results)
        
        # Batch extract transcripts for top videos
        for v in all_results[:10]:
            transcript = self.web.youtube_transcript(v["url"])
            # Feed to synthesis phase
```

### Why Agent Reach > BrowserClaw for Workers
- **Speed**: 5-10x faster (CLI vs headless browser)
- **Reliability**: No cookie walls, no bot detection, no dynamic waits
- **Scriptable**: Full CLI + JSON output, easy to pipe
- **Batch**: Search 50 videos, extract all subtitles, one command
- **No overhead**: Runs as CLI, minimal resources

### Subagent Timeout Pattern — Workers (2026-07-25)

**Problem:** Workers using BrowserClaw for YouTube research timeout at 600s.

**Solution:** Worker scripts must use Agent Reach (`yt-dlp`):
```python
# OLD (browser-based, times out)
# 9 queries × 3 videos = 27 browser navigations + waits + extraction = 600s+

# NEW (Agent Reach, ~60s total)
import subprocess, json
queries = [...]  # from task_data
for q in queries:
    result = subprocess.run(
        ['yt-dlp', f'ytsearch3:{q}', '--dump-json', 
         '--print', 'id,title,channel,view_count,description,url'],
        capture_output=True, text=True, timeout=60
    )
    for line in result.stdout.strip().split('\n'):
        if line:
            all_results.append(json.loads(line))

# Then batch extract subtitles for top videos
for v in top_videos:
    subprocess.run(['yt-dlp', '--write-auto-subs', '--sub-langs', 'en,ru',
                   '--skip-download', f'https://youtu.be/{v["id"]}'], timeout=120)
```

**Rule:** For worker tasks with >5 YouTube queries, always use `yt-dlp` via Agent Reach. BrowserClaw reserved for: video page interaction (comments, chapters), visual analysis, auth-required content.

## References

- `references/firstmate-architecture.md` — анализ архитектуры FirstMate
- `references/honest-review-patterns.md` — паттерны честной валидации
- `references/worker-protocol.md` — протокол общения Manager ↔ Worker