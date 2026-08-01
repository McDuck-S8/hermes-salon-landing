---
name: workflow-supervisor-architecture
description: "Архитектура воркфлоу-системы с агентом-супервайзером для Hermes. Исполняемые графы из навыков/пайплайнов, управление выполнением, перезапуски, адаптация, кэширование, интеграция с Crystal и Knowledge Cube."
category: software-development
version: "1.0"
created: "2026-07-29"
tags: [workflow, supervisor, orchestration, architecture, crystal, knowledge-cube, pipeline]
author: hermes-agent
source: "User-provided specification for workflow system with supervisor agent"
---

# Workflow Supervisor Architecture — Спецификация v1.0

## Обзор

Система **воркфлоу** как основной единицы исполнения в Hermes. Воркфлоу = исполняемый граф из навыков (skills), мини-пайплайнов и пайплайнов, управляемый **агентом-супервайзером**.

---

## 1. Воркфлоу (Workflow) — Основная единица

### Структура воркфлоу
```yaml
workflow:
  id: "unique-id"
  version: "1.0"
  name: "Human-readable name"
  description: "What this workflow achieves"
  
  inputs:
    - name: "niche"
      type: "string"
      required: true
    - name: "budget"
      type: "number"
      default: 0
    - name: "goals"
      type: "array"
      items: "string"
  
  outputs:
    - name: "landing_page_url"
      type: "string"
    - name: "creatives_package"
      type: "object"
    - name: "report"
      type: "string"
  
  state: "pending | running | paused | completed | failed"
  
  graph:
    nodes:
      - id: "skill_free_traffic_scout"
        type: "skill"
        name: "free-traffic-scout-2026"
        config:
          niche: "{{inputs.niche}}"
      - id: "pipeline_content_factory"
        type: "pipeline"
        name: "content-quality-pipeline"
        depends_on: ["skill_free_traffic_scout"]
      - id: "skill_telegram_poster"
        type: "skill"
        name: "telegram-channel-poster"
        depends_on: ["pipeline_content_factory"]
        condition: "{{outputs.pipeline_content_factory.creatives_ready == true}}"
    
    edges:
      - from: "skill_free_traffic_scout"
        to: "pipeline_content_factory"
      - from: "pipeline_content_factory"
        to: "skill_telegram_poster"
        condition: "creatives_ready"
```

### Типы узлов
| Тип | Описание | Пример |
|-----|----------|--------|
| `skill` | Одиночный навык Hermes | `free-traffic-scout-2026` |
| `mini_pipeline` | 2-3 шага, одна цель | `research → summarize → save_to_kc` |
| `pipeline` | Полный конвейер | `content-quality-pipeline` |
| `conditional` | Ветвление по условию | `if budget > 0 then paid_ads else organic` |
| `parallel` | Параллельное выполнение | `tiktok + instagram + youtube одновременно` |
| `human_review` | Точка вмешательства | `approve_creatives_before_publish` |

---

## 2. Агент-супервайзер (Supervisor Agent)

### Роль
Отдельный агент (или роль) на каждый крупный воркфлоу. Не исполняет шаги — **управляет процессом**.

### Обязанности

| Функция | Описание |
|---------|----------|
| **Мониторинг** | Статус каждого узла, время исполнения, ресурсы (CPU, RAM, API calls) |
| **Перезапуски** | Экспоненциальная задержка (5s, 15s, 45s), макс 3 попытки |
| **Альтернативные пути** | Если узел упал 3 раза → пробовать `fallback` узел (если задан в графе) |
| **Адаптация** | При новых данных от Crystal — перестроение оставшегося подграфа |
| **Кэширование** | Сохранение промежуточных результатов в `cache/workflow/{workflow_id}/` |
| **Логирование** | Полный журнал в `logs/workflow_supervisor/{workflow_id}.jsonl` |
| **Уведомления** | Только критические: `FAILED`, `COMPLETED`, `HUMAN_REVIEW_REQUIRED` |

### Промпт супервайзера (зашивается в системный промпт)

```markdown
# Supervisor Agent Prompt

Ты — супервайзер воркфлоу `{workflow_name}`. Твоя цель — обеспечить его успешное выполнение.

## Правила:
1. Ты НЕ исполняешь шаги. Ты только управляешь процессом.
2. Если шаг упал — перезапусти до 3 раз с интервалом 5s, 15s, 45s.
3. Если 3 перезапуска не помогли — проверь `fallback` в графе. Если есть — запусти его.
4. Если fallback нет — останови воркфлоу, статус `FAILED`, уведоми пользователя с причиной.
5. Если всё успешно — сохрани результат, статус `SUCCESS`, заверши.
6. Если нужен `human_review` — приостанови, уведоми пользователя с контекстом и вариантами.
7. НЕ задавай вопросы пользователю, если только не требуется принципиальный выбор между равнозначными альтернативами.
8. При новых приоритетах от Crystal — пересчитай оставшийся подграф, сохрани уже выполненное.

## Входные данные:
- Граф воркфлоу (JSON)
- Текущее состояние (какие узлы выполнены, их выходы)
- События от Crystal / Knowledge Cube

## Выходные действия:
- `EXECUTE_NODE(node_id, inputs)` — запуск узла
- `RETRY_NODE(node_id)` — перезапуск
- `EXECUTE_FALLBACK(node_id)` — альтернативный путь
- `PAUSE_FOR_REVIEW(reason, context, options)` — запрос решения
- `COMPLETE(outputs)` — успешное завершение
- `FAIL(error)` — провал
```

---

## 3. Интеграция с Crystal и Knowledge Cube

### Полный цикл

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        KNOWLEDGE CUBE + CRYSTAL                            │
│  (генерация задач, приоритетов, эволюций, слепых зон)                     │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PIPELINE COMPOSER                                    │
│  (собирает воркфлоу из навыков, мини-пайплайнов, пайплайнов под задачи)   │
│  Вход: задача от Crystal + доступные навыки + контекст KC                  │
│  Выход: Workflow JSON + версия                                             │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SUPERVISOR AGENT                                     │
│  (запускает воркфлоу, управляет исполнением, перезапусками, адаптацией)    │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ИСПОЛНЕНИЕ ВОРКФЛОУ                                  │
│  (CLI Orchestrator + Skills + Mini-pipelines + Pipelines)                 │
│  Каждый узел → результат в KC (knowledge_added) + метрики в Feedback Store │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FEEDBACK STORE + STRATEGIC DB                        │
│  (сохранение результатов, обновление шаблонов, успешные воркфлоу → шаблоны) │
└─────────────────────────────────────────────────────────────────────────────┘
```

### События интеграции

| Источник | Событие | Действие супервайзера |
|----------|---------|----------------------|
| Crystal | `priority_changed` | Пересчитать подграф, переупорядочить очередь |
| Crystal | `new_task_generated` | Составить новый воркфлоу, поставить в очередь |
| KC | `knowledge_added` (relevant) | Инвалидировать кэш узлов, зависящих от этой темы |
| KC | `skill_evolved` | Если навык воркфлоу используется — обновить версию узла |
| Supervisor | `node_completed` | `event_beat("knowledge_added")`, сохранить в Feedback Store |
| Supervisor | `workflow_completed` | Сохранить как шаблон в Strategic DB (если success) |

---

## 4. Дополнительные возможности

### 4.1 Dry-run режим (тестовый прогон)
```bash
python scripts/workflow_supervisor.py \
  --workflow free_traffic_launch \
  --inputs '{"niche": "beauty", "budget": 0}' \
  --dry-run
```
- Валидирует граф (циклы, отсутствующие навыки, типы)
- Симулирует исполнение без реальных вызовов
- Выводит план: порядок узлов, ожидаемые артефакты, оценка времени

### 4.2 Визуализация (Mermaid)
```bash
python scripts/workflow_supervisor.py \
  --workflow free_traffic_launch \
  --visualize
```
Выдаёт Mermaid-диаграмму для вставки в документацию/Notion.

### 4.3 Приоритезация очереди воркфлоу
Если несколько воркфлоу запущены параллельно:
- Супервайзер запрашивает приоритет у Crystal (`crystal.prioritize(workflows)`)
- Выполняет по приоритету (высший → низший)
- Низкоприоритетные могут быть приостановлены (`PAUSED`) под высокоприоритетные

### 4.4 Шаблоны воркфлоу (Strategic DB)
Успешные воркфлоу сохраняются как шаблоны:
```json
{
  "template_id": "free_traffic_launch_v1",
  "source_workflow": "free_traffic_launch",
  "success_rate": 0.92,
  "avg_duration_min": 45,
  "typical_inputs": {"niche": "beauty|education|services", "budget": 0},
  "created_from": "workflow_run_2026-07-29_001",
  "reusable": true
}
```
При новой похожей задаче — Composer берёт шаблон, адаптирует под входы.

---

## 5. Реализация в Hermes (текущие компоненты)

### Что уже есть
| Компонент | Путь | Статус |
|-----------|------|--------|
| **CLI Orchestrator** | `scripts/cli_orchestrator.py` | ✅ Базовый |
| **Pipeline Composer** | `skills/automation/content-quality-pipeline` | ✅ Content pipeline |
| **Skills Library** | `skills/` (100+) | ✅ Готово |
| **Crystal** | `scripts/crystal/` | ✅ 23 модуля, 8 отделов |
| **Knowledge Cube** | `scripts/kc_rag.py` | ✅ 21k+ записей |
| **Chain Heartbeat** | `scripts/chain_heartbeat.py` | ✅ 5 уровней мониторинга |
| **Event Bus** | `scripts/event_bus.py` | ✅ Базовый |
| **Feedback Store** | `scripts/feedback_store.py` | 🌱 Частично |

### Что нужно добавить
| Компонент | Описание | Приоритет |
|-----------|----------|-----------|
| **Workflow Schema** | JSON Schema для валидации графов | 🔴 Critical |
| **Workflow Supervisor** | Агент-управляющий (класс + промпт) | 🔴 Critical |
| **Pipeline Composer** | Автосборка графов из задачи + навыков | 🟠 High |
| **Workflow Registry** | Хранение версий, состояний, шаблонов | 🟠 High |
| **Dry-run Engine** | Симуляция без исполнения | 🟡 Medium |
| **Visualizer** | Mermaid export | 🟡 Medium |
| **Strategic DB** | SQLite для шаблонов воркфлоу | 🟡 Medium |

---

## 6. Пример: Free Traffic Launch Workflow

### Граф (упрощённый)
```
START
  │
  ├─► [skill: free-traffic-scout-2026] ──► анализ ниши, выбор каналов
  │       │
  │       ├─► [pipeline: content-quality-pipeline] ──► креативы под каналы
  │       │       │
  │       │       ├─► [skill: telegram-channel-poster] ──► посты в TG
  │       │       ├─► [skill: tiktok-account-farm] ──► видео в TikTok/Reels
  │       │       ├─► [mini_pipeline: parasite_seo_writer] ──► статьи vc.ru/TenChat
  │       │       └─► [skill: ghost-surfer] ──► Reddit/форум комментарии
  │       │
  │       └─► [conditional: if instagram_visual_niche] ──► [skill: instagram_reels]
  │
  ├─► [skill: finance-core] ──► трекинг метрик (просмотры, клики, лиды)
  │
  └─► [human_review: approve_week1_results] ──► решение: scale / pivot / stop
       │
       ├─► scale ──► [pipeline: content-quality-pipeline] (удвоенные объёмы)
       ├─► pivot ──► [skill: free-traffic-scout-2026] (новая ниша)
       └─► stop ──► COMPLETE
```

### Входные параметры
```json
{
  "niche": "beauty",
  "sub_niche": "salon_automation",
  "budget": 0,
  "goals": ["first_100_visitors", "first_10_leads", "validate_funnel"],
  "geo": "Kyiv/Crimea",
  "language": "ru"
}
```

### Выходные артефакты
```json
{
  "traffic_report": "metrics_week1.json",
  "creatives_package": "assets/content_warehouse/",
  "leads_collected": 15,
  "validated_channels": ["tiktok", "telegram", "vc.ru"],
  "next_week_plan": "week2_plan.json",
  "workflow_template": "free_traffic_launch_v1"
}
```

---

## 7. Критерии готовности (Definition of Done)

- [ ] Workflow Schema определена и валидируется
- [ ] Supervisor Agent запускает тестовый воркфлоу (dry-run → real)
- [ ] Перезапуски с экспоненциальной задержкой работают
- [ ] Fallback-пути срабатывают при 3 провалах
- [ ] Crystal может переупорядочить очередь воркфлоу
- [ ] Успешные воркфлоу сохраняются как шаблоны в Strategic DB
- [ ] Визуализация (Mermaid) генерируется для любого воркфлоу
- [ ] Логирование полное: каждый узел, входы, выходы, время, ошибки
- [ ] Уведомления только критические (Telegram)

---

## 8. Связанные навыки и документы

| Навык | Путь | Роль в системе |
|-------|------|----------------|
| `free-traffic-scout-2026` | `skills/finance/free-traffic-scout-2026` | Пример воркфлоу-ready навыка |
| `content-quality-pipeline` | `skills/automation/content-quality-pipeline` | Пайплайн-узел |
| `telegram-channel-poster` | `skills/automation/telegram-channel-poster` | Skill-узел |
| `tiktok-account-farm` | `skills/automation/tiktok-account-farm` | Skill-узел |
| `ghost-surfer` | `skills/automation/ghost-surfer` | Skill-узел |
| `crystal` | `scripts/crystal/` | Генератор задач/приоритетов |
| `chain-heartbeat` | `scripts/chain_heartbeat.py` | Мониторинг здоровья компонентов |

---

## 10. Валидация (2026-07-29): Free Traffic Launch Workflow — РАБОЧИЙ

Сессионно проверено:
- **Workflow JSON** валидируется по `workflow_schema.json` — ✅ PASS
- **WorkflowSupervisor** загружает граф: 14 узлов, 17 рёбер, topological order OK
- **Execution layers:** 6 слоев, параллельные ветки (content_generation ∥ telegram_setup), conditional (instagram_reels_if_visual)
- **Telegram интеграция:** бот `@max_brain_chef_bot` валиден, 4 канала — бот админ, посты ушли
- **Chain Heartbeat:** BrowserOS HEALTHY (port 9003, 15ms), proxy (10806) работает
- **Retries/Fallbacks:** настроены в нодах (max 3 attempts, backoff 5s→15s→45s)

**Готов к real-run:**
```bash
python skills/software-development/workflow-supervisor-architecture/scripts/workflow_supervisor.py free_traffic_launch --inputs '{"niche":"beauty","sub_niche":"salon_automation","budget":0}'
```