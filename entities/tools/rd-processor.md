---
id: rd-processor
type: tool
namespace: knowledge/ai-core
status: canon
version: 1.0.0
owner: operator
created: 2026-06-29T00:00:00Z
summary: Research & Development processor (DIRECT handler for new_external_signal)
description: |
  RD Processor receives new_external_signal events directly (DIRECT_EVENT_HANDLERS)
  and applies Bayesian scoring to create research tasks in ARBITRAGE_WORKSHOP.md
  research queue. Only processes signals with score > 0.6.
depends_on:
  - event-bus
  - bayesian-scorer
  - signal-daemon
tags:
  - research
  - direct-handler
  - bayesian
  - workshop
confidence: 0.9
retrieval_class: hot
export_class: operator
---

# RD Processor — Research Queue Processor

## Role
DIRECT event handler for `new_external_signal`. Bypasses event queue for immediate processing.

## Flow
1. Receive `new_external_signal` event (from signal_daemon via event_bus)
2. Apply Bayesian scoring: P(relevant|signal)
3. If score > 0.6 → create research task in ARBITRAGE_WORKSHOP.md
4. Emit `research_task_created` event

## Integration
- `scripts/rd_processor.py` — Main processor
- Registered in `event_daemon.py` DIRECT_EVENT_HANDLERS
- Uses `scripts/bayesian_scorer.py` for scoring

## Related Entities
- [[signal-daemon]] — External signal source
- [[event-bus]] — Event bus (DIRECT handler)
- [[bayesian-scorer]] — Scoring engine
- [[dev-processor]] — Parallel dev processor