---
id: autonomous-agent
type: agent
namespace: knowledge/ai-core
status: canon
version: 1.0.0
owner: operator
created: 2026-06-29T00:00:00Z
summary: Autonomous decision-making agent (29-candidate decision matrix)
description: |
  The autonomous agent is the executive runtime of Hermes. It evaluates 29 action
  candidates per cycle, scores each with Bayesian inference, and executes the
  highest-scoring action. Integrates with crystal self-learning loop, event bus,
  goal queue, and procedural executor.
depends_on:
  - crystal-core
  - event-bus
  - goal-queue
  - procedural-executor
  - signal-daemon
tags:
  - autonomous
  - decision-matrix
  - bayesian
  - executive
confidence: 0.95
retrieval_class: hot
export_class: operator
---

# Autonomous Agent — Executive Runtime

## Overview
Main autonomous agent loop that runs continuously, evaluating a decision matrix
of 29 candidates via Bayesian scoring and executing the highest-scoring action.

## Decision Matrix (29 Candidates)
| Category | Candidates |
|----------|------------|
| Self-Healing | cron_health, memory_guard, disk_guard, gateway_guard |
| Knowledge Acquisition | white_spot_explore, gap_fill, session_recall_query |
| Skill Evolution | skill_scan, skill_evolve, skill_auto_create |
| Proactive Execution | fix_execute, verify_outcome, pattern_record |
| Revenue Generation | arbitrage_test, arbitrage_scale, traffic_optimize |

## Scoring
Bayesian: `P(action|evidence) = P(evidence|action) * P(action) / P(evidence)`

## Integration
- `scripts/autonomous_agent.py` — Main loop
- `scripts/crystal/core.py` — Self-learning consumer
- `scripts/event_bus.py` — Event triggers
- `scripts/goal_queue.py` — Goal management
- `scripts/procedural_executor.py` — Reflexes
- `scripts/signal_daemon.py` — External signals

## Related Entities
- [[crystal-core]] — Self-learning loop
- [[event-bus]] — Event-driven architecture
- [[goal-queue]] — Goal management
- [[procedural-executor]] — Deterministic reflexes
- [[signal-daemon]] — External signal monitoring