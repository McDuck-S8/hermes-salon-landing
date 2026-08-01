---
id: crystal-core
type: skill
namespace: knowledge/ai-core
status: canon
version: 1.0.0
owner: operator
created: 2026-06-29T00:00:00Z
summary: Self-learning loop (observe→diagnose→will→execute→learn) with 23 modules
description: |
  Crystal is the self-learning loop of Hermes. It runs continuously in 5 phases:
  observe (collect metrics/errors), diagnose (root cause analysis), will (plan actions),
  execute (run actions), learn (update knowledge). 23 modules cover alerts, brief,
  communication, conversation analysis, core, dev proposer, error analysis, executor,
  feedback loop, goals, growth loop, intelligence, knowledge base, memory integration,
  models, need analyzer, pattern detector, priority engine, resources, risk assessment,
  rollback, self-evolution, semantic parser, session reader, staleness, synergy,
  testing, versioning.
depends_on:
  - knowledge-cube
  - session-recall
  - event-bus
tags:
  - self-learning
  - crystal
  - observe-diagnose-will-execute-learn
confidence: 0.95
retrieval_class: hot
export_class: operator
---

# Crystal Core — Self-Learning Loop

## 5-Phase Loop
1. **Observe** — Collect system metrics, errors, session context, user needs
2. **Diagnose** — Root cause analysis, anomaly detection, pattern recognition
3. **Will** — Plan actions, prioritize via Bayesian scoring, generate goals
4. **Execute** — Run actions via autonomous agent, delegate tasks, verify outcomes
5. **Learn** — Update Knowledge Cube, evolve skills, record patterns

## 23 Modules
- alerts, brief, communication, conversation_analyzer, core
- dev_proposer, error_analyzer, executor, feedback_loop, goals
- growth_loop, intelligence, knowledge_base, memory_integration, models
- need_analyzer, pattern_detector, priority_engine, resources, risk_assessment
- rollback, self_evolution, semantic_parser, session_reader, staleness
- synergy, testing, versioning

## Key Files
- `scripts/crystal/core.py` — Main loop
- `scripts/crystal/*.py` — 23 modules
- `scripts/crystal.py` — CLI entry

## Related Entities
- [[knowledge-cube]] — Knowledge storage
- [[session-recall]] — BM25 history search
- [[autonomous-agent]] — Executive runtime
- [[event-bus]] — Event-driven triggers