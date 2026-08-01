---
id: dev-processor
type: tool
namespace: knowledge/ai-core
status: canon
version: 1.0.0
owner: operator
created: 2026-06-29T00:00:00Z
summary: Development task processor (DIRECT handler for new_external_signal)
description: |
  Dev Processor receives new_external_signal events directly and applies Bayesian
  scoring to create development tasks in dev queue (cache/dev_queue.json).
  Uses Bayesian priority instead of static urgency * impact. Only processes
  signals with score > 0.5.
depends_on:
  - event-bus
  - bayesian-scorer
  - signal-daemon
tags:
  - development
  - direct-handler
  - bayesian
  - task-queue
confidence: 0.9
retrieval_class: hot
export_class: operator
---

# Dev Processor — Development Task Processor

## Role
DIRECT event handler for `new_external_signal`. Creates actionable dev tasks.

## Flow
1. Receive `new_external_signal` event
2. Apply Bayesian scoring: P(actionable|signal)
3. If score > 0.5 → create dev task in cache/dev_queue.json
4. Emit `dev_task_created` event

## Integration
- `scripts/dev_processor.py` — Main processor
- Registered in `event_daemon.py` DIRECT_EVENT_HANDLERS
- Uses `scripts/bayesian_scorer.py` for scoring

## Related Entities
- [[signal-daemon]] — External signal source
- [[event-bus]] — Event bus (DIRECT handler)
- [[bayesian-scorer]] — Scoring engine
- [[rd-processor]] — Parallel research processor