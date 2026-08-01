# Weights Loop Fix (2026-07-28)

## Issue
Test `test_3_weights_affect_scoring` failed because `compute_score()` in `autonomous_agent.py` did not use the weight from `feedback_store.compute_weight()`. Both actions scored 5.5 regardless of feedback history.

## Root Cause
`compute_score()` in `autonomous_agent.py` calculated score as:
```python
score = (urgency * 0.6) + (impact * 0.3) + (tier_bonus * 0.1)
```
No weight factor from `feedback_store.compute_weight()` was included.

## Fix Applied (`scripts/autonomous_agent.py:compute_score()`)

```python
def compute_score(action: dict, state: dict) -> float:
    """
    Score = urgency * 0.6 + impact * 0.3 + tier_bonus * 0.1 + weight_bonus

    Tier bonus:
      SURVIVE gets highest bonus (5), LEARN (3), PRODUCE (1)
    Weight bonus: from feedback_store.compute_weight (0.5-1.5)
    """
    urgency = action.get("urgency", 1)
    impact = action.get("impact", 1)
    tier = action.get("tier", 3)

    tier_bonus = (4 - tier) * 5  # TIER_SURVIVE(1)->15, LEARN(2)->10, PRODUCE(3)->5

    # Check cooldown — don't repeat same action within 30 minutes
    cooldown_penalty = 0
    recent_decisions = load_decisions()
    for dec in recent_decisions[-20:]:
        if dec.get("action_id") == action["id"]:
            try:
                dec_time = datetime.fromisoformat(dec["timestamp"])
                if (datetime.now() - dec_time).total_seconds() < 1800:
                    cooldown_penalty = 50  # Heavy penalty
                    break
            except Exception:
                pass

    # Weight from feedback store (0.5 to 1.5)
    weight = 1.0
    try:
        from feedback_store import compute_weight
        weight = compute_weight(action.get("id", ""))
    except Exception:
        pass

    score = (urgency * 0.6) + (impact * 0.3) + (tier_bonus * 0.1) + (weight * 0.1) - cooldown_penalty
    return round(score, 2)
```

## Test Result
`test_3_weights_affect_scoring` now **PASSES**:
- Action with negative feedback (weight ~0.8) gets lower score
- Action with positive feedback (weight ~1.2) gets higher score
- Difference visible in final scores