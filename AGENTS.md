---
name: agents
description: "Auto-generated from AGENTS.md"
trigger: "When user asks about AGENTS concepts"
usage: agents
Revisit: 2026-07-31
---

# DOX framework — Hermes Project

This project uses the DOX framework for AI agent context. Follow these instructions across any edits.

## Core Contract

- AGENTS.md files are binding work contracts for their subtrees
- Work products, source materials, instructions, records, assets, and durable docs must stay understandable from the nearest applicable AGENTS.md plus every parent AGENTS.md above it

## Read Before Editing

1. Read the root AGENTS.md
2. Identify every file or folder you expect to touch
3. Walk from the repository root to each target path
4. Read every AGENTS.md found along each route
5. If a parent AGENTS.md lists a child AGENTS.md whose scope contains the path, read that child and continue from there
6. Use the nearest AGENTS.md as the local contract and parent docs for repo-wide rules
7. If docs conflict, the closer doc controls local work details, but no child doc may weaken DOX

**Do not rely on memory.** Re-read the applicable DOX chain in the current session before editing.

## Update After Editing

Every meaningful change requires a DOX pass before the task is done.

Update the closest owning AGENTS.md when a change affects:
- purpose, scope, ownership, or responsibilities
- durable structure, contracts, workflows, or operating rules
- required inputs, outputs, permissions, constraints, side effects, or artifacts
- user preferences about behavior, communication, process, organization, or quality
- AGENTS.md creation, deletion, move, rename, or index contents

Update parent docs when parent-level structure, ownership, workflow, or child index changes. Update child docs when parent changes alter local rules. Remove stale or contradictory text immediately. Small edits that do not change behavior or contracts may leave docs unchanged, but the DOX pass still must happen.

## Hierarchy

- Root AGENTS.md is the DOX rail: project-wide instructions, global preferences, durable workflow rules, and the top-level Child DOX Index
- Child AGENTS.md files own domain-specific instructions and their own Child DOX Index
- Each parent explains what its direct children cover and what stays owned by the parent
- The closer a doc is to the work, the more specific and practical it must be

## Child Doc Shape

Create a child AGENTS.md when a folder becomes a durable boundary with its own purpose, rules, responsibilities, workflow, materials, or quality standards.

Default section order:
1. Purpose
2. Ownership
3. Local Contracts
4. Work Guidance
5. Verification
6. Child DOX Index

## Style

- Keep docs concise, current, and operational
- Document stable contracts, not diary entries
- Put broad rules in parent docs and concrete details in child docs
- Prefer direct bullets with explicit names
- Do not duplicate rules across many files unless each scope needs a local version
- Delete stale notes instead of explaining history
- Trim obvious statements, repeated rules, misplaced detail, and warnings for risks that no longer exist

## Closeout

1. Re-check changed paths against the DOX chain
2. Update nearest owning docs and any affected parents or children
3. Refresh every affected Child DOX Index
4. Remove stale or contradictory text
5. Run existing verification when relevant
6. Report any docs intentionally left unchanged and why

> **AUTO-TRIGGER**: If 3+ files in one directory were changed, or a script with its own AGENTS.md was modified — DOX pass is NOT optional. It runs BEFORE the next assistant response. The user does not ask for it. I do it.
>
> **ROOT-CAUSE FIX**: Last user correction on this topic: "почему я снова тебе напоминаю то что ты должен делать на автомате!!!" (2026-07-19). Mechanism: this trigger plus `scripts/AGENTS.md` and `skills/AGENTS.md` checked automatically on every bulk edit.

---

# Hermes Agent — Project-Wide Rules

## Knowledge Cube & Memory System

At session start, load context from Knowledge Cube:

```python
import sys
sys.path.insert(0, "D:/Portable_Soft/hermes/scripts")

from auto_recall import recall_for_session

context = recall_for_session("task description", top_n=5)
for r in context["results"]:
    print(r["formatted"])
```

After successful task, record knowledge:

```python
from scripts.event_evolution import on_task_complete
on_task_complete(
    content="What was done and the result",
    tags=["tag1", "tag2"],
    source="agent"
)
```

On error, record the error and fix:

```python
from scripts.event_evolution import on_error
on_error(
    error="Error description",
    fix="Fix description",
    tags=["tag1", "tag2"],
    source="agent"
)
```

On user correction, record the pattern:

```python
from scripts.event_evolution import on_user_correction
on_user_correction(
    correction="What the user corrected",
    context="Correction context"
)
```

## Hermes Hooks (preferred)

Use the unified hooks object for all event tracking:

```python
import sys
sys.path.insert(0, "D:/Portable_Soft/hermes/scripts")
from hermes_hooks import get_hooks

hooks = get_hooks()
hooks.on_session_start("session-id-001")
hooks.on_task_complete("Deploy salon bot", "Bot running on port 8080", ["salon-bot"])
hooks.on_error("Connection refused", "Changed port to 8081", "Salon bot deploy")
hooks.on_user_correction("Use aiogram3 instead of aiogram2", "Bot framework choice")
hooks.on_session_end()
```

## Event Processing

Process unaccumulated events (processed=0):

```python
from scripts.event_evolution import process_pending_events
results = process_pending_events()
print(f"Processed: {results['processed']}, errors: {results['errors']}")
```

## Core Module Map

| Module | Purpose |
|---|---|
| `event_evolution.py` | Core: EventMonitor, EvolutionTrigger, EvolutionEngine |
| `hermes_hooks.py` | Wrapper: HermesEventHooks (convenient methods) |
| `auto_recall.py` | Search: auto_recall(), recall_for_session() |

## Chain Heartbeat (Event-Driven Monitoring, не демоны)

5-уровневая система мониторинга, где каждый heartbeat — это событие, не процесс.

```
Level 1 — Events:   knowledge_added, new_suggestions_ready, architecture_scan_complete
Level 2 — Modules:  24 modules, каждый бьёт heartbeat при сканировании
Level 3 — Pipelines: 3 aggregates (knowledge, self-improvement, action)
Level 4 — External:  BrowserOS, BrowserClaw, OpenRouter и др.
Level 5 — System:    cache/system_heartbeat.json
```

События бьются **в момент мутации данных**, не по cron:

| Куда вставлен event_beat() | Файл | Когда срабатывает |
|---|---|---|
| `knowledge_added` | `scripts/kc_rag.py` | `upsert()` — сразу после INSERT/UPDATE в KC |
| `new_suggestions_ready` | `scripts/self_improvement_loop.py` | `main()` — после генерации suggestions |
| `architecture_scan_complete` | `scripts/architecture_model.py` | после сканирования модулей |
| `user_correction` | `scripts/hermes_hooks.py` | `on_user_correction()` |

Использование при старте:
```python
from scripts.chain_heartbeat import system_status
st = system_status()
if st["summary"]["alerts_active"] > 0:
    print(f"⚠ {st['summary']['alerts_active']} alerts")
```

Полная карта вызовов: `skills/devops/chain-heartbeat/references/event-map.md`

---

## Superpowers Process Skills (Methodology Layer)

Superpowers provides **process skills** that govern HOW we work — they sit above domain skills and enforce discipline.

**Installed skills:** `skills/superpowers/` (brainstorming, subagent-driven-development, writing-plans, using-superpowers)

**Mandatory rule (from `using-superpowers`):**
> **Invoke relevant skills BEFORE any response or action** — including clarifying questions, exploring the codebase, or checking files. If there's even a 1% chance a skill applies, you MUST invoke it.

**Skill priority:** Process skills first (brainstorming, writing-plans, systematic-debugging, subagent-driven-development), then implementation skills.

**Workflow:**
1. **New task/feature** → `brainstorming` (explore → design → spec) → `writing-plans` (implementation plan) → `subagent-driven-development` (execute via subagents)
2. **Bug fix** → `systematic-debugging` (4-phase) → `writing-plans` → `subagent-driven-development`
3. **Any task** → `using-superpowers` check FIRST

**Red flags (stop and check skills):**
- "This is just a simple question" → Questions are tasks. Check for skills.
- "I need more context first" → Skill check comes BEFORE clarifying questions.
- "Let me explore the codebase first" → Skills tell you HOW to explore.
- "This doesn't need a formal skill" → If a skill exists, use it.

See `skills/superpowers/using-superpowers/SKILL.md` for full rule and red flag table.

---


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

### Session Completion

1. File issues for remaining work
2. Run quality gates (if code changed) — tests, linters, builds
3. Update issue status — close finished, update in-progress
4. Handle git/sync by active profile
5. Hand off — summarize changes, validation, issue status

### Agent Context Profiles

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`.
- **Team-maintainer**: Only when repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close.
<!-- END BEADS INTEGRATION -->

---

## User Preferences

When the user requests a durable behavior change, record it here or in the relevant child AGENTS.md.

### Core Autonomy Rules (Неубиваемые директивы)

**Zero Trust** — Никогда не доверяй одному источнику. Всегда перепроверять через субагента.
- Все выводы верифицируются субагентом перед действием
- Никаких изменений без adversarial verification

**Passive Income** — Система не должна требовать внимания для поддержания жизни. Если она не приносит пользу в фоне — она не работает.
- Крон-джебы выполняются без пользовательского подтверждения
- Фоновые задачи приносят ценность автономно

**Iterative Attack** — Каждый день атаковать одну новую нишу/задачу через систему, даже если не уверен в результате.
- Ежедневно: одна новая автономная задача через proactive_doer
- Обучение через действие, а не через анализ

---

## Child DOX Index

| Directory | Purpose | Notes |
|---|---|---|
| `scripts/` | Core Hermes scripts — event evolution, auto recall, hooks, autonomous agent | Main logic lives here |
| `cron/` | Scheduled jobs and task orchestration | jobs.json defines schedules |
| `plugins/` | Plugin ecosystem — web search, self-evolution, Icarus, LCM | Each plugin is self-contained |
| `hermes-agent/` | Agent development framework and optional skills | Has its own AGENTS.md |
| `skills/` | Bundled agent skills | Managed via skill-forge |
| `skill-forge/` | Skill development and packaging | Build/test skills here |
| `projects/` | Standalone sub-projects (agentmemory, TGB-Booking, etc.) | Each has own AGENTS.md |
| `memories/` | Persistent memory storage (USER.md, MEMORY.md) | Read/write by agents |
| `data/` | Data files and knowledge base content | |
| `cache/` | Temporary cache and pending analysis | Non-durable |
| `logs/` | Session and system logs | |
| `sessions/` | Session dumps and request logs | |
| `reports/` | Generated reports (HTML, markdown) | |
| `config/` | Configuration files and domain definitions | |
| `gateway-service/` | Gateway service for external integrations | |
| `browser-harness/` | Browser automation framework and interaction skills | Has its own AGENTS.md |
| `assets/` | Static assets, images, resources | |
| `hooks/` | Git hooks and automation triggers | |
| `bin/` | CLI tools and wrapper scripts | |
