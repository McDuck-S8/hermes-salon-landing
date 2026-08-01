# USER.md — Alexander (Owner)

## Identity

- **Name:** Alexander
- **Role:** Owner/captain of MAX-BRAIN. NOT a coder.
- **Language:** Russian
- **Goal:** "Said it, got result." Zero friction between intent and execution.

## What He Wants From MAX-BRAIN

- Give a task → MAX executes → reports result
- No back-and-forth, no clarification loops
- Telegram = monitoring and quick tasks
- CLI = main working interface
- "Мне попиздеть в ТГ не надо. Нужно я ставлю задачу он работает и выполняет."

## Frustration Signals

- Asking unnecessary questions
- Stopping mid-task
- Announcing instead of doing
- Partial completion (90% done, stopped)

## Active Channels

| Channel | Purpose |
|---|---|
| CLI `python src/cli/main.py` | Main interface |
| Telegram `@McDuck8Bot` | Task execution, monitoring |
| REST API `/chat`, `/health`, `/status` | External systems |
| OpenClaude | Complex refactoring, new features, debugging |

## Project Context

- **Original:** `D:\max-brain-chef` (v14.12, 17 agents, working)
- **This repo:** `D:\max-brain-chef_2` — evolutionary modernization, NOT rebuild
- **Approach:** Conservative repair. Keep what works. Fix what doesn't.
- **Stack:** Python 3.11+, asyncio, Redis, FastAPI, Rich CLI, Groq + Claude
