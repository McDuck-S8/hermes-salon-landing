---
id: hermes-autonomous-agent
type: agent
namespace: knowledge/ai-core
status: canon
version: 1.0.0
owner: operator
created: 2026-06-29T00:00:00Z
summary: Autonomous decision-making agent with 29-candidate decision matrix
description: |
  Main autonomous agent loop that evaluates 29 action candidates via Bayesian scoring
  and executes the highest-scoring action. Integrates with crystal self-learning loop,
  event bus, goal queue, and procedural executor.
depends_on:
  - crystal-core
  - event-bus
  - goal-queue
  - procedural-executor
tags:
  - autonomous
  - decision-matrix
  - bayesian
confidence: 0.95
retrieval_class: hot
export_class: operator
---

# Hermes Autonomous Agent

## Overview
The autonomous agent is the executive runtime of Hermes. It runs continuously,
evaluating a decision matrix of 29 candidates per cycle, scoring each with Bayesian
inference, and executing the highest-scoring action.

## Decision Matrix
29 candidates across categories:
- Self-healing (cron health, memory, disk, gateway)
- Knowledge acquisition (white-spot exploration, gap filling)
- Skill evolution (auto-evolution from Knowledge Cube)
- Proactive execution (fix execution, verification)
- Revenue generation (arbitrage scheme testing, scaling)

## Integration Points
- `crystal/core.py` — self-learning loop (observe→diagnose→will→execute→learn)
- `scripts/event_bus.py` — event-driven triggers
- `scripts/goal_queue.py` — priority goal management
- `scripts/procedural_executor.py` — deterministic reflexes (no LLM)
- `scripts/signal_daemon.py` — external signal monitoring (HN, GitHub trending)

## Configuration
See `config.yaml` for agent settings:
- `agent.max_turns: 60`
- `agent.gateway_timeout: 1800`
- `agent.api_max_retries: 3`
- `agent.tool_use_enforcement: auto`

## Related Entities
- [[crystal-core]] — Self-learning loop
- [[event-bus]] — Event-driven architecture
- [[goal-queue]] — Goal management
- [[procedural-executor]] — Deterministic reflexes
- [[signal-daemon]] — External signal monitoring