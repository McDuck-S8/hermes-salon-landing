---
id: signal-daemon
type: skill
namespace: knowledge/ai-core
status: canon
version: 1.0.0
owner: operator
created: 2026-06-29T00:00:00Z
summary: External signal monitoring (HN, GitHub trending) with adaptive backoff
description: |
  Signal Daemon monitors external sources (Hacker News, GitHub Trending) for
  relevant signals. Uses adaptive backoff: 60s when signals found, up to 10min
  when quiet. Emits `new_external_signal` events to event bus. Runs as background
  daemon.
depends_on:
  - event-bus
  - bayesian-scorer
tags:
  - external-monitoring
  - hn
  - github-trending
  - adaptive-backoff
confidence: 0.9
retrieval_class: hot
export_class: operator
---

# Signal Daemon — External Signal Monitoring

## Sources
- Hacker News (Algolia API)
- GitHub Trending (API)

## Adaptive Backoff
```python
if new_signals_found:
    backoff = 60  # seconds
else:
    backoff = min(backoff * 1.5, 600)  # up to 10 minutes
```

## Output
Emits `new_external_signal` events with:
- `source`: "hn" or "github_trending"
- `title`, `url`, `score`, `ts`
- Deduplicated via SHA256 in `cache/signals_processed.json`

## Integration
- `scripts/signal_daemon.py` — Main daemon
- `scripts/signal_scanner.py` — Scanning logic
- `scripts/bayesian_scorer.py` — Bayesian scoring before emit (score < 0.3 → reject)

## Related Entities
- [[event-bus]] — Event-driven architecture
- [[bayesian-scorer]] — Probabilistic scoring
- [[rd-processor]] — Research queue (DIRECT handler)
- [[dev-processor]] — Dev task queue (DIRECT handler)