---
name: readme
description: "Auto-generated from README.md"
trigger: "When user asks about README concepts"
usage: readme
Revisit: 2026-07-31
---

# Hermes Autonomous Arbitrage Agent

Autonomous event-driven arbitrage system for traffic monetization.

## Quick Start

```bash
# Install dependencies
uv sync

# Run autonomous agent (dry run)
uv run python scripts/autonomous_agent.py --dry

# Run finance core
uv run python scripts/finance_core.py summary

# Validate arbitrage scheme
bash scripts/validate-fix.sh Content-Locking-CPA
```

## Architecture

- **Orchestrator** → **Maker** → **Checker** (Loop Engineering pattern)
- **Finance Core** — P&L, Cash Flow, Unit Economics, Tax Ledger
- **Knowledge Cube** — FTS5 + semantic search
- **Arbitrage Workshop** — 50+ schemes with ЦА templates

## Structure

```
.omp/                    # Loop Engineering conventions
scripts/                 # Core scripts
  autonomous_agent.py    # Main orchestrator
  finance_core.py        # Finance ledger
  validate-fix.sh        # Deterministic validation
state/
  loop-state.md          # Orchestrator memory
cache/
  finance_core.db        # Finance ledger
  knowledge_cube.db      # Knowledge Cube
.omp/
  AGENTS.md              # Project conventions
  agents/
    maker.md             # Maker subagent
    checker.md           # Checker subagent
```