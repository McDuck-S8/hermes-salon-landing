# Socratic Task Breakdown — Reference

## Что это
Рекурсивный Socratic-опросник для декомпозиции задач.
Агент не выполняет задачу сразу, а сначала разбирает её
через систему вопросов до атомарного уровня.

## Источники
Синтез подходов:
1. PDCA-scaffold — 5 вопросов: цель, данные, инструменты, ограничения, проверка
2. Agent Architect Questionnaire — 8 модулей (Mission, Soul, Identity, Human Profile, Operations, Tools, Memory, Skills)
3. Recursive Decomposition (CodeFrame #421) — ATOMIC / COMPOSITE / AMBIGUOUS
4. Maestro orchestration — orchestrator + executor с циклом до "The task is complete"
5. Socratic Reasoning Patterns — 6 паттернов (Transformation, Decomposition, Regather, Deduction, Verification, Integration)

## Быстрый старт
```python
from scripts.hermes_hooks import get_hooks
hooks = get_hooks()

# Запустить Socratic breakdown перед задачей
hooks.socratic_breakdown("Сделать бота для салона")
# → серия вопросов → план
```

## Схема данных: три типа узлов

```
ATOMIC:
  action: str
  tool: str
  input: str
  output: str
  estimate: str

COMPOSITE:
  subtasks: list[Node]
  dependencies: dict[subtask_id -> list[subtask_id]]

AMBIGUOUS:
  question: str
  answered: bool
  fallback: str  # что делать если ответа нет
```

## Интеграция с Hermes

- Skill: `socratic-breakdown` (self-improvement category)
- План сохраняется в `.hermes/plans/{task_id}.md`
- После выполнения — Knowledge Cube: on_task_complete / on_error
- Если задача застревает — Transformation pattern
