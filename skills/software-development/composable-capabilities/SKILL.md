---
name: composable-capabilities
description: >-
  Build Hermes agents from composable capability bricks.
  Each capability bundles tools, instructions, lifecycle hooks,
  and model settings into one self-contained unit.
  Agents are composed from bricks, not configured as monoliths.
category: software-development
---

# Composable Capabilities

**Паттерн:** Агент = композиция самодостаточных bricks (capabilities).
Каждый brick содержит всё, что нужно модели для его использования:
инструменты, инструкции, хуки, настройки модели.

Взято из Pydantic AI v2 / orbit-support-agent, адаптировано под Hermes
с нулевыми внешними依赖мостями.

## Когда использовать

- Сборка агента из нескольких независимых "умений" (search, scan, calculate)
- Одна и та же capability в разных агентах (reuse)
- On-demand подгрузка инструментов (deferred loading — экономим токены)
- Аудит lifecycle каждого вызова инструмента
- Определение схемы агента как YAML-файла (agent spec)
- Интеграция существующих Hermes-скриптов (CPA scanner, gap calculator) как tools

## Архитектура

```
   ┌──────────────────────────────────────────┐
   │           ComposedAgent                   │
   │  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
   │  │ Cap A    │  │ Cap B    │  │ Cap C   │ │
   │  │ tools[]  │  │ tools[]  │  │ hooks[] │ │
   │  │ instr    │  │ instr    │  │         │ │
   │  │ settings │  │ deferred │  │         │ │
   │  └──────────┘  └──────────┘  └─────────┘ │
   └──────────────────────────────────────────┘
         │              │              │
    execute_tool()  execute_tool()  before/after hooks
         │              │              │
         └──────────────┴──────────────┘
                      │
               audit_report()
```

## Ключевые компоненты

### Capability
Базовый brick. Содержит:
- `name` — уникальное имя
- `description` — что делает (для deferred-каталога)
- `instructions` — промпт, который получает модель
- `tools` — список `ToolDef` (имя + функция + описание + схема аргументов)
- `hooks` — `Hooks(before_tool, after_tool, before_run, after_run)`
- `settings` — `ModelSettings(temperature, max_tokens, top_p)`
- `defer_loading` — если True, capability скрыта до востребования

### Hooks
Lifecycle-хуки на каждый вызов:
- `before_tool(ctx, tool_name, args)` → args — модификация аргументов
- `after_tool(ctx, tool_name, result)` → result — модификация результата
- `before_run(ctx, prompt)` → prompt — модификация промпта
- `after_run(ctx, result)` → result — модификация результата

### ComposedAgent
Собранный из capability агент:
- `all_instructions` — объединённые инструкции из всех bricks
- `tool_map` — `{tool_name: capability_name}`
- `catalog()` — компактный список deferred-капабилити (для on-demand)
- `load_capability(name)` — активировать deferred capability
- `summary()` — человеко-читаемый состав

### execute_tool()
Цепочка выполнения: хук before → tool → хук after → аудит.
Каждый вызов логируется в глобальный `AUDIT`.

### load_agent_spec()
Загрузка агента из YAML. Позволяет определить схему как файл:
```yaml
agent:
  name: revenue-researcher
  capabilities:
    - name: web_search
      tools:
        - name: search_web
          type: native
    - name: cpa_scanner
      defer_loading: true
      tools:
        - name: scan_offers
          type: script
          path: skills/finance/arbitrage-sensors/scripts/cpa_scanner.py
          args: ["--once"]
```

## Использование

```python
from hermes_capability import (Capability, Hooks, compose_agent,
                               execute_tool, audit_report,
                               load_agent_spec)

# 1. Определяем инструменты
def search_kb(query: str) -> str:
    return f"Results for '{query}': found 3 articles"

# 2. Собираем capability
kb = Capability(
    name="knowledge_base",
    instructions="Always search KB first.",
    tools=[tool(description="Search KB")(search_kb)],
    settings=ModelSettings(temperature=0.0),
)

# 3. Компонуем агента
agent = compose_agent(capabilities=[kb])

# 4. Вызываем инструмент (с хуками и аудитом)
result = await execute_tool(agent, "search_kb", {"query": "how to cancel"})

# 5. Смотрим аудит
print(audit_report())
```

Или из YAML:
```python
agent = load_agent_spec("schemes/revenue_researcher.yaml")
```

## Адаптация внешних паттернов (важно)

Когда изучаешь внешний фреймворк/образец (Pydantic AI, LangChain, и т.д.):

1. **НЕ** анализируй и не сравнивай в тексте — сразу пиши код
2. Выдели core-паттерн (одна идея, не весь фреймворк)
3. Реализуй на чистом Python, 0 внешних зависимостей
4. Используй существующие Hermes-инструменты (web_search, terminal и т.д.)
5. Если нужен новый модуль — клади в `scripts/`
6. Запусти демку, покажи что работает
7. Обнови скилл этим паттерном

Фраза пользователя: **"бери идею и под себя"** — главный принцип.

## Pitfalls

- **Capability ≠ микросервис**. Не создавай capability на каждый чих.
  Группируй связанные инструменты (3-5 на capability).
- **Defer_loading только для редких сценариев**. Если capability
  вызывается в каждом run — не defer'ь, экономим round-trip.
- **Инструкции должны быть конкретными**. "Use web_search first" лучше
  чем "Search the web when appropriate".
- **Не дублируй инструменты**. Если два capability имеют `web_search` —
  конфликт имён. Используй префиксы или общий инструмент.
- **import subprocess и Path внутри функций** — да, это нормально для
  скриптовых tools. Основной модуль держи чистым.
- **Аудит не бесконечный.** `AUDIT` — глобальный список, очищай
  `reset_audit()` между независимыми run'ами.

## Референсы

- `scripts/hermes_capability.py` — реализация паттерна (436 строк)
- `references/capability_api.md` — полное API описание
- `references/agent_spec_example.yaml` — пример YAML spec
