# Maturity Criteria (Convergence Detection)

Logic for `calculate_mature_keys()` in `RippleEngine`.

## Core Principle

**Mature = Convergence**, not actionability.

A key matures when **multiple independent stones** point to it with strong signals. Actionability is a display metric, not a gate.

## Algorithm

```python
# Aggregate by new_key across ALL stones
key_stats = {}
for stone in stones:
    for key in stone.new_keys:
        if key not in key_stats:
            key_stats[key] = {"stones": [], "total_strength": 0, "total_conf": 0, "actionable": 0}
        key_stats[key]["stones"].append(stone)
        key_stats[key]["total_strength"] += stone.key_strength
        key_stats[key]["total_conf"] += stone.confidence
        if stone.actionable:
            key_stats[key]["actionable"] += 1

# Evaluate each key
mature = []
for key, stats in key_stats.items():
    count = len(stats["stones"])
    avg_strength = stats["total_strength"] / count
    avg_conf = stats["total_conf"] / count
    actionable_ratio = stats["actionable"] / count  # display only
    
    # Maturity gate: convergence + signal quality
    is_mature = (
        count >= 2 and              # Multiple stones converge
        avg_strength >= 65 and      # Strong average signal
        avg_conf >= 55              # Reliable
    )
    # actionable_ratio intentionally NOT in gate
    
    if is_mature:
        mature.append({
            "key": key,
            "supporting_stones": count,
            "avg_strength": round(avg_strength),
            "avg_confidence": round(avg_conf),
            "actionable_ratio": round(actionable_ratio * 100),
            "aspects": list(set(a for s in stats["stones"] for a in s.aspects)),
            "sources": list(set(s.source for s in stats["stones"])),
            "unlock_reason": f"{count} stones converge, avg strength {avg_strength:.0f}, {actionable_ratio*100:.0f}% actionable",
            "unlocked_at": datetime.now().isoformat(),
        })
```

## Threshold Rationale

| Threshold | Value | Reason |
|-----------|-------|--------|
| `count >= 2` | 2 | Single stone = anecdote; 2+ = pattern |
| `avg_strength >= 65` | 65 | Above "medium" (60), below "high" (75) — strong but not exclusive |
| `avg_conf >= 55` | 55 | Above "low" (45), accounts for noisy sources (0-1 confidence normalized) |

## Why NOT Gate on Actionable Ratio

- **Source bias**: Some sources (Partnerkin) mark `actionable=false` by default; others (ripple_keys_2) mark `true`
- **Computed vs source**: `stone.actionable` is recomputed from strength/confidence/conflicts — not the raw field
- **Convergence IS the signal**: If 5 stones independently generate the same key, it's mature regardless of individual actionability

## Output Structure

```json
{
  "key": "iGaming_SEO_playbook",
  "supporting_stones": 5,
  "avg_strength": 89,
  "avg_confidence": 81,
  "actionable_ratio": 40,
  "aspects": ["SEO_traffic", "ai_tools", "pbn_networks"],
  "sources": ["youtube", "partnerkin"],
  "unlock_reason": "5 stones converge, avg strength 89, 40% actionable",
  "unlocked_at": "2026-07-20T04:13:36.123456"
}
```

## Downstream Consumption

Unlocked keys are printed to stdout and can be:
1. Fed to `event_evolution.py` as `mature_key_unlocked` event
2. Written to Knowledge Cube as `type: mature_key` experiences
3. Consumed by `proactive_executor.py` for auto-implementation
4. Used by `crystal-architecture-awareness` for module health correlation

## Debugging Zero Results

If `mature_keys == 0`:

1. Check `key_stats` — are there keys with `count >= 2`?
2. Print `avg_strength` / `avg_conf` for top keys
3. If thresholds too high, lower to 60/50 temporarily
4. Verify `stone.actionable` recomputation (conflicts=0 gate)

```bash
python -c "
from scripts.ripple_engine import RippleEngine
e = RippleEngine()
e.gather_daily_stones()
from collections import Counter
c = Counter(k for s in e.stones for k in s.new_keys)
print('Top keys:', c.most_common(10))
"
```