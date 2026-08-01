---
id: bayesian-scorer
type: skill
namespace: knowledge/ai-core
status: canon
version: 1.0.0
owner: operator
created: 2026-06-29T00:00:00Z
summary: Probabilistic scoring engine P(H|E) = P(E|H) * P(H) / P(E)
description: |
  Bayesian Scorer provides probabilistic scoring for all decision points in Hermes.
  Used by: signal_scanner (score before emit), rd_processor (score before workshop),
  dev_processor (Bayesian priority), daily_metrics (P(flow_alive)). CLI available.
depends_on:
  - event-classifier
tags:
  - bayesian
  - probabilistic
  - scoring
  - decision-support
confidence: 0.9
retrieval_class: hot
export_class: operator
---

# Bayesian Scorer — Probabilistic Decision Scoring

## Formula
```
P(H|E) = P(E|H) * P(H) / P(E)
```
- H = Hypothesis (e.g., "signal is relevant")
- E = Evidence (signal content, source, keywords)

## Use Cases
| Component | Hypothesis | Evidence | Threshold |
|-----------|------------|----------|-----------|
| signal_scanner | "Signal relevant for workshop" | title, source, keywords | <0.3 reject |
| rd_processor | "Signal → research task" | content, domain match | >0.6 queue |
| dev_processor | "Signal → dev task" | tech keywords, actionability | >0.5 queue |
| daily_metrics | "Flow alive" | recent actions, goal progress | >0.7 healthy |

## CLI
```bash
python scripts/bayesian_scorer.py --status
python scripts/bayesian_scorer.py --score "hypothesis" "evidence"
python scripts/bayesian_scorer.py --history
```

## Integration
- `scripts/bayesian_scorer.py` — Core engine
- `scripts/signal_scanner.py` — Signal scoring
- `scripts/rd_processor.py` — Research queue scoring
- `scripts/dev_processor.py` — Dev task scoring

## Related Entities
- [[event-classifier]] — Uses for classification
- [[signal-daemon]] — Scores external signals
- [[rd-processor]] — Scores for research queue
- [[dev-processor]] — Scores for dev queue