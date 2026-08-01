---
id: event-classifier
type: skill
namespace: knowledge/ai-core
status: canon
version: 1.0.0
owner: operator
created: 2026-06-29T00:00:00Z
summary: Classifies raw signals into typed events with confidence scores
description: |
  Event Classifier takes raw signals from sensors and external sources and
  classifies them into typed events with Bayesian confidence scoring.
  Uses bayesian_scorer for probabilistic classification.
depends_on:
  - event-bus
  - bayesian-scorer
tags:
  - classification
  - bayesian
  - signal-processing
confidence: 0.85
retrieval_class: warm
export_class: operator
---

# Event Classifier — Signal to Typed Event Classification

## Classification Pipeline
1. Raw signal input (from sensor_array, signal_daemon, webhooks)
2. Feature extraction (keywords, source, patterns)
3. Bayesian scoring via `bayesian_scorer.py`
4. Event type assignment with confidence
5. Emit to event_bus if score > threshold

## Event Types
| Type | Source | Threshold |
|------|--------|-----------|
| `new_external_signal` | signal_daemon | 0.3 |
| `system_critical` | sensor_array | 0.7 |
| `error_pattern` | sensor_array | 0.5 |
| `cron_event` | scheduler | 0.9 |

## Integration
- `scripts/event_classifier.py` — Classification logic
- `scripts/bayesian_scorer.py` — Scoring engine
- Outputs to `scripts/event_bus.py`

## Related Entities
- [[event-bus]] — Event bus consumer
- [[bayesian-scorer]] — Scoring engine
- [[signal-daemon]] — External signal source
- [[sensor-array]] — Internal sensor source