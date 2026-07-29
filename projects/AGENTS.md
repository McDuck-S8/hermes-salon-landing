# projects/ — Standalone Sub-Projects

## Purpose
Standalone sub-projects with independent codebases, dependencies, and deployment configs.

## Ownership
Each sub-project is independently maintained. Mostly Telegram bots and utility projects.

## Local Contracts
- Each project has its own `requirements.txt` or `pyproject.toml`
- Most are Python projects
- `agentmemory/` is a TypeScript/Node.js project with its own AGENTS.md

## Work Guidance
- **agentmemory/**: Agent memory system — MCP server, hooks, evaluation, TypeScript (has detailed AGENTS.md)
- **TGB-Booking/**: Telegram booking bot — SQLAlchemy, Alembic, FSM states
- **salon-bot/**: Salon booking bot — aiogram, SQLite
- **crimea-bots/**: Crimea tourism bots — hotels, restaurants, transfers
- **entity-engine/**: Entity analysis engine
- **ai-education-bot/**: AI education Telegram bot

## Verification
- Each project has its own README with setup instructions
- Run tests per-project (see individual READMEs)

## Child DOX Index
| Project | Stack | Purpose |
|---|---|---|
| `agentmemory/` | TypeScript | Agent memory MCP server |
| `TGB-Booking/` | Python/SQLAlchemy | Telegram booking system |
| `salon-bot/` | Python/aiogram | Salon booking bot |
| `crimea-bots/` | Python | Crimea tourism bots |
| `entity-engine/` | Python | Entity analysis |
| `ai-education-bot/` | Python | AI education bot |
