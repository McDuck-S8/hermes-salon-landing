# AGENTS.md — Инструкции для Hermes Agent

Этот файл описывает протокол интеграции с системой автономного обучения.
Каждый агент-сессия должна следовать этим шагам.

---

## При старте сессии

Загрузить контекст из Knowledge Cube через auto_recall:

```python
import sys
sys.path.insert(0, "D:/Portable_Soft/hermes/scripts")

from auto_recall import recall_for_session

# Получить релевантный контекст для текущей задачи
context = recall_for_session("описание текущей задачи", top_n=5)
for r in context["results"]:
    print(r["formatted"])
```

---

## После успешной задачи

Вызвать хук для фиксации знаний:

```python
from scripts.event_evolution import on_task_complete

on_task_complete(
    content="Описание что было сделано и результат",
    tags=["tag1", "tag2"],
    source="agent"
)
```

---

## При ошибке

Зафиксировать ошибку и исправление:

```python
from scripts.event_evolution import on_error

on_error(
    error="Описание ошибки",
    fix="Описание исправления",
    tags=["tag1", "tag2"],
    source="agent"
)
```

---

## При коррекции пользователем

Зафиксировать паттерн из коррекции:

```python
from scripts.event_evolution import on_user_correction

on_user_correction(
    correction="Что именно пользователь поправил",
    context="Контекст коррекции"
)
```

---

## Через hermes_hooks.py (рекомендуется)

Более удобный способ — через единый объект хуков:

```python
import sys
sys.path.insert(0, "D:/Portable_Soft/hermes/scripts")
from hermes_hooks import get_hooks

hooks = get_hooks()

# Сессия начата
hooks.on_session_start("session-id-001")

# Задача выполнена
hooks.on_task_complete("Deploy salon bot", "Bot running on port 8080", ["salon-bot"])

# Ошибка произошла
hooks.on_error("Connection refused", "Changed port to 8081", "Salon bot deploy")

# Пользователь поправил
hooks.on_user_correction("Use aiogram3 instead of aiogram2", "Bot framework choice")

# Сессия завершена
hooks.on_session_end()
```

---

## Обработка накопленных событий

Если есть необработанные события (processed=0):

```python
from scripts.event_evolution import process_pending_events

results = process_pending_events()
print(f"Обработано: {results['processed']}, ошибок: {results['errors']}")
```

---

## Структура вызовов

```
event_evolution.py  — ядро: EventMonitor, EvolutionTrigger, EvolutionEngine
hermes_hooks.py     — обёртка: HermesEventHooks (удобные методы)
auto_recall.py      — поиск: auto_recall(), recall_for_session()
```

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:6cd5cc61 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md for details and anti-patterns.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **File issues for remaining work** - Create beads for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:
   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
   git push
   git status
   ```
5. **Hand off** - Summarize changes, validation, issue status, and any blocked sync/commit/push step

**Critical rules:**
- Explicit user or orchestrator instructions override this Beads block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If a required sync or push is blocked, stop and report the exact command and error.
<!-- END BEADS INTEGRATION -->

<!-- BEGIN BEADS CODEX SETUP: generated by bd setup codex -->
## Beads Issue Tracker

Use Beads (`bd`) for durable task tracking in repositories that include it. Use the `beads` skill at `.agents/skills/beads/SKILL.md` (project install) or `~/.agents/skills/beads/SKILL.md` (global install) for Beads workflow guidance, then use the `bd` CLI for issue operations.

### Quick Reference

```bash
bd ready                # Find available work
bd show <id>            # View issue details
bd update <id> --claim  # Claim work
bd close <id>           # Complete work
bd prime                # Refresh Beads context
```

### Rules

- Use `bd` for all task tracking; do not create markdown TODO lists.
- Run `bd prime` when Beads context is missing or stale. Codex 0.129.0+ can load Beads context automatically through native hooks; use `/hooks` to inspect or toggle them.
- Keep persistent project memory in Beads via `bd remember`; do not create ad hoc memory files.

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md for details and anti-patterns.
<!-- END BEADS CODEX SETUP -->
