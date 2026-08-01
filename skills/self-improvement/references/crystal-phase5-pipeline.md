# Phase 5 — Crystal Pipeline

## Architecture

```
crystal_observer → вычисляет 6 асимптот
     ↓
cache/crystal_asymptotes.json
     ↓
crystal_will → выбирает худшую асимптоту (driver)
     ↓
cache/crystal_command.json
     ↓
Hermes (agent) → читает команду, выполняет
     ↓
Knowledge Cube (запись результата)
     ↓
crystal_observer на следующем цикле видит новый срез
```

## Key Principles

1. **Crystal decides, Hermes executes.** No filtering, no bias. Hermes is a transparent conductor, not a decision-maker.
2. **Служение внешнему миру.** Everything in the pipeline must produce value outside itself. If a component only writes to itself (crystal writes to KC for crystal), it's dead. The output must eventually reach the user as an actionable result.
3. **Асимптоты — бесконечный горизонт.** They are never fully achieved. Their purpose is to create directional tension, not to be "solved."
4. **Classification artifacts are real.** An asymptote gap may be a symptom of upstream misclassification, not a real problem. Always sample real data before committing.

## Components

### crystal_observer.py
- Reads all 4 cubes (KC, EE, FL, Fabric)
- Computes 6 asymptotes with current value, target, gap, normalised_gap
- Saves to `cache/crystal_aspects.json`
- Formats output with progress bars per asymptote
- Writes a summary to KC (domain=crystal, outcome=snapshot)

### crystal_will.py
- Loads `cache/crystal_asments.json`
- Ranks by normalised_gap
- Picks the worst gap as driver (threshold: normalised_gap > 0.3)
- Gathers context for the chosen driver (SQL queries per domain)
- Writes command to `cache/crystal_command.json`

### Hermes (agent)
- Reads `cache/crystal_command.json` at session start or on user's "continue"
- Executes the action described in the command
- Writes the result to KC (domain=crystal, outcome=action or insight)
- Deletes `crystal_command.json` after execution
- Reports the result to the user

## 6 Asymptotes

| Metric | Target | Direction | Meaning |
|--------|--------|-----------|---------|
| Связность | 1.0 (100%) | up | % of KC records linked to EE entities |
| Покрытие | 1.0 (100%) | up | Uniformity of domain distribution (1 - δ/δMax) |
| Элегантность | 1.0 (100%) | up | % of non-noisy records (>15 chars, meaningful) |
| Предсказательность | 5.0 | up | success/failure ratio |
| Скорость | 0.001 days | down | Avg time between consecutive KC entries |
| Автономность | 1.0 (100%) | up | % self-initiated vs commanded actions |

## Known Pitfalls

1. **predictability gap can be misleading.** On 2026-06-12, the 83% gap was 91% auto-generated suggestions misclassified as "failure." Always check a sample of actual failure texts before committing to action.
2. **connectivity measurement is slow.** Recomputing orphans on every observer run scans all KC records × all entity names. Consider caching entity name lists.
3. **speed measurement uses only last 100 entries.** Recent burst writes (e.g. cube_feeder adding 9 entries in 1 minute) can make speed look faster than it is.
4. **autonomy metric is simplistic.** Self vs commanded source classification doesn't capture "who initiated the initiation" — a cron job running a script the user wrote is not truly autonomous.
