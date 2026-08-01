# FirstMate Architecture Analysis

**Source**: https://github.com/kunchenguid/firstmate
**Analyzed**: 2026-07-08

## Core Concept

FirstMate = "Talk to one agent. Ship with a crew."

Вы (Captain) → FirstMate (Manager) → Crewmates (Workers в изолированных worktrees)

## Key Architectural Components

### 1. Event-Driven Supervision (`bin/fm-watch.sh`)
- **Zero-token bash watcher** — спит на флоте, классифицирует wake signals
- Actionable wakes: captain-relevant signals, stale panes, heartbeat backstops
- Durable local queue (`state/.wake-queue`) — recovery from missed process exits
- Wake classification logic с priority order

### 2. Presence-Gated Sub-Supervisor (`bin/fm-supervise-daemon.sh`)
- Активируется через `/afk` skill
- Self-handles routine wakes in bash
- Эскалирует только captain-relevant events как single batched digest
- Backend-agnostic: tmux, herdr, zellij

### 3. Worktree Isolation
- Каждый crewmate получает чистый git worktree
- Изоляция изменений, параллельная работа
- Ship mode: PR/merge → teardown | Scout mode: report → relay findings

### 4. Dispatch Profiles
- Steer which harness handles which task
- `claude`, `codex`, `opencode`, `pi`, `grok` backends

### 5. Fleet Sync
- Координация между crewmates
- X-mode: отвечает на публичные упоминания в X/Twitter

## What We Adapted for Hermes

| FirstMate | Hermes Adaptation |
|-----------|-------------------|
| Captain → FirstMate (CLI) | User → Agent Manager (Python) |
| Crewmates (separate processes) | Workers (subprocess calls) |
| Git worktrees | File-based isolation (cache/landings/, cache/*_checklist.json) |
| Zero-token watcher | Not needed (single session) |
| `/afk` away mode | Not needed |
| X-mode | Not needed |
| PR-based ship | File output + review score |

## What We Dropped
- VS Code extension / GUI
- Git worktree complexity (overkill for CLI)
- Multi-backend harness detection
- Turn-end guard hooks
- tmux/herdr/zellij backend abstraction

## Key Insight Applied

**Manager-Worker protocol via JSON over stdin/stdout**:
```
Manager → Worker: JSON task_data (task_id, description, context, previous_task_id)
Worker → Manager: JSON result (success, result, error)
```

Это проще чем FirstMate's shell-based coordination, но сохраняет суть: оркестратор не делает работу, он распределяет.