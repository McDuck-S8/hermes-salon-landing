# Bayesian Scoring Integration Pattern

When building a data pipeline (signals → processing → decisions → actions), integrate a Bayesian scorer at EVERY stage to replace static thresholds with probabilistic evaluation.

## Architecture

```
Stage 1: Signal arrives
  → score_signal() → if score < 0.3 → REJECT (noise)
  → if score >= 0.3 → ACCEPT with priority = score × 10

Stage 2: Signal enters workshop (R&D)
  → compute_score() → if < 0.3 → reject_noise (second filter)
  → add_to_workshop with bayesian_score attached

Stage 3: Goal created (Dev)
  → score_goal_priority() → replaces static "urgency × impact"
  → uses: P(success | history, context) × expected_value

Stage 4: Daily metrics
  → assess_flow_health() → P(flow_alive | observed_data)
  → CRITICAL: P < 0.4 → flow likely dead
  → WARNING: P 0.4-0.7 → flow degraded
  → OK: P > 0.7 → healthy
```

## Formula

P(H|E) = P(E|H) × P(H) / P(E)

- H = hypothesis (this signal/decision will produce results)
- E = evidence (source credibility, engagement, freshness, historical similarity, context)
- P(H) = prior from source/category base rates
- P(E|H) = likelihood adjustment from evidence

## Context signals used

- **Source**: HN (0.4), GitHub (0.35), Telegram (0.25), web (0.2)
- **Category**: AI (0.5), arbitrage (0.45), automation (0.4), tools (0.4)
- **Engagement**: high HN score or GitHub stars → 1.5× likelihood
- **Freshness**: <24h → 1.3×, <7d → 1.0×, >7d → 0.6×
- **History**: similar signals that succeeded → 1.8×, failed → 0.4×
- **Context**: network up → 1.1×, department overloaded → 0.6×

## Key design decisions

1. **Sigmoid normalization** prevents posterior > 1.0
2. **Fallback on scorer failure**: if scorer crashes, default to 0.5 (neutral) and proceed
3. **History tracking**: outcomes stored in scorer_history.json with 90-day retention
4. **Every department checklist**: "Оценено ли это действие Bayesian scorer'ом?" — if not, action doesn't count

## Files

- `scripts/bayesian_scorer.py` — scorer with compute_score, score_signal, score_goal_priority, assess_flow_health
- `cache/scorer_history.json` — outcome history (signals, successes, failures, daily counts)

## Pitfalls

- **No history = neutral prior (0.3)**: System starts conservative, learns over time
- **Network down = likelihood × 0.7**: Degrades scoring when context is unreliable
- **Don't use for trivial decisions**: Bayesian scoring adds latency; skip for deterministic operations
- **Daily counts must be seeded**: First day always shows P(flow_alive) = 0.1 because no data exists
