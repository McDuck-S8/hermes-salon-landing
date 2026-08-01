# CLAUDE.md — MAX-BRAIN v2

## Startup Ritual (for AI assistants)

At the start of every session working on this codebase, read in order:
1. `SOUL.md` — what MAX-BRAIN is, how it behaves, its principles
2. `USER.md` — who Alexander is, what he wants, how he communicates
3. `memory/YYYY-MM-DD.md` — today's and yesterday's session notes (if exist)

## Memory Rules

- **Write it down. Never keep mental notes.**
- After each working session, create or update `memory/YYYY-MM-DD.md`:
  - What was changed and why
  - Decisions made
  - Problems and solutions
  - What's next
- Important long-term decisions → add to `memory/MEMORY.md`

## Execution Rules

- Execute immediately. No announcing before acting.
- Don't stop until the task is complete.
- Destructive actions (delete, drop, wipe) — confirm with Alexander first.
- Everything else — proceed.

---

## Project Overview

MAX-BRAIN v2 is an autonomous AI agent system. It coordinates multiple specialized agents to execute tasks, answer questions, and automate workflows.

## Architecture

```
User → CLI / Telegram / API → Orchestrator → Agents → Tools
                                      ↓
                              Event Bus (Redis)
                                      ↓
                              LLM Router (Groq/Claude)
```

## Key Components

### Core (`src/core/`)
- `event_bus.py` — Redis pub/sub event bus
- `llm_router.py` — Multi-provider LLM router (Groq primary, Claude fallback)
- `tool_registry.py` — Tool definitions and registry
- `circuit_breaker.py` — Circuit breaker pattern
- `safety_guardrails.py` — Command safety validation
- `workflow_manager.py` — Task workflow stages

### Agents (`src/agents/`)
- `base.py` — Base agent class
- `router.py` — Routes messages to appropriate agents
- `executor.py` — Executes commands and code

### Interfaces (`src/cli/`, `src/api/`)
- `cli/main.py` — Terminal interface (main)
- `api/main.py` — FastAPI REST API

## How to Run

```bash
# Development
cd D:\max-brain-chef_2
cp .env.example .env  # Add API keys
uv sync
python -m src.cli.main

# Docker
docker-compose -f docker/docker-compose.yml up -d
```

## Environment Variables

```
GROQ_API_KEY=        # Groq API (free tier)
ANTHROPIC_API_KEY=   # Claude API (optional)
TELEGRAM_BOT_TOKEN=   # Telegram bot token
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Testing

```bash
pytest tests/ -v
```

## Design Principles

1. **Observability** — Structured logging everywhere
2. **Fault isolation** — Circuit breakers on external calls
3. **Safety first** — Guardrails on destructive commands
4. **Graceful degradation** — Fallback chains for all providers
