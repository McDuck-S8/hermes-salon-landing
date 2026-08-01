---
id: event-bus
type: tool
namespace: knowledge/ai-core
status: canon
version: 1.0.0
owner: operator
created: 2026-06-29T00:00:00Z
summary: Event-driven architecture core (emit/subscribe, persisted log, DIRECT handlers)
description: |
  Event Bus is the nervous system of Hermes. It connects sensors to chains via
  a persisted event log. Supports DIRECT handlers that bypass the queue for
  critical events (new_external_signal → rd_processor + dev_processor).
depends_on:
  - signal-daemon
  - sensor-array
  - event-classifier
  - event-daemon
  - event-reactor
  - procedural-executor
tags:
  - event-driven
  - sensor-array
  - chains
  - direct-handlers
  - pub-sub
confidence: 0.95
retrieval_class: hot
export_class: operator
---

# Event Bus — Event-Driven Architecture Core

## Architecture
```
Sensors → Classification → Event Bus → Chains → Actions
                ↓
         DIRECT Handlers (bypass queue)
```

## Components
| Component | File | Role |
|-----------|------|------|
| Sensors | `signal_daemon.py`, `sensor_array.py` | Input (HN, GitHub, system metrics) |
| Classifier | `event_classifier.py` | Raw → typed events |
| Bus | `event_bus.py` | Emit/subscribe, persisted log |
| Daemon | `event_daemon.py` | Background consumer |
| Reactor | `event_reactor.py` | Pattern → action mapping |
| Procedural | `procedural_executor.py` | Deterministic reflexes (no LLM) |
| RD Processor | `rd_processor.py` | Research queue (DIRECT) |
| Dev Processor | `dev_processor.py` | Dev task queue (DIRECT) |

## DIRECT Event Handlers
```python
# In event_daemon.py
DIRECT_EVENT_HANDLERS = {
    "new_external_signal": ["rd_processor", "dev_processor"],
    "system_critical": ["procedural_executor"],
}
```

## Event Types
- `new_external_signal` — HN/GitHub trending (from signal_daemon)
- `system_metric` — CPU, RAM, disk, process health (from sensor_array)
- `error_detected` — Error patterns, exceptions
- `cron_tick` — Scheduled job triggers
- `research_task_created` — RD processor output
- `dev_task_created` — Dev processor output

## Integration
- `scripts/event_bus.py` — Core emit/subscribe
- `scripts/event_daemon.py` — Background daemon
- `scripts/event_reactor.py` — Pattern matching
- `scripts/event_classifier.py` — Classification
- `scripts/signal_daemon.py` — External source
- `scripts/sensor_array.py` — Internal sensors

## Related Entities
- [[signal-daemon]] — External signal monitoring
- [[sensor-array]] — System metrics sensors
- [[event-classifier]] — Event classification
- [[procedural-executor]] — Deterministic reflexes
- [[rd-processor]] — Research queue processor
- [[dev-processor]] — Dev task processor