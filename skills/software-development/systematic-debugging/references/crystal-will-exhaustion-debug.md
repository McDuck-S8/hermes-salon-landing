# Crystal Will() Exhaustion — Debug Session 2026-06-13

## Problem
crystal.py will() function generates candidates, picks best, executes. After 2-3 cycles, "всё сделано" — no candidates left.

## Root Cause Chain
1. **Fixed candidate strings**: conscience generates learning_direction from hardcoded lists (5 per type x 4 types = 20)
2. **historical_ids filter**: every executed action goes to will_history, blocking future selection
3. **Only 3 unique action types**: analyze_kc_domain, classify_kc_entries, cross_domain_analysis
4. **Result**: 3 unique action_ids -> all in historical_ids after 3 cycles -> exhaustion

## Patches Applied (All Wrong)
| Patch | What | Why Wrong |
|-------|------|-----------|
| #4 | conscience diversity: pick from prev_learning | Still fixed strings |
| #5 | 20 candidates (5x4 types) | More fixed strings = same exhaustion |
| prev_learning window | Last 2 assessments only | Just delays exhaustion by 1 cycle |
| HIGH efficiency learning | Generate LD for high-efficiency actions | More fixed strings |
| Data-driven LDs | Generate from actual KC domains | Code added but LD strings not in LEARNING_TO_ACTION mapping |

## Final Fix
**Remove historical_ids check for conscience actions.** KC grows between runs, so repeating conscience analysis produces different results each time.

```python
# Before (broken):
if action_id not in historical_ids and action_id not in seen_actions:

# After (works):
if action_id not in seen_actions:
```

## Key Insight
Conscience actions != script actions. Scripts produce side effects (extract, connect, build) - repeat is wasteful. Conscience actions produce observations (analyze, classify, scan) - repeat with growing KC is valuable.

## User Feedback
"ты снова сам кодишь, отсюда и твои фантазии" — 5 patches before finding root cause. Each patch added more code to fix symptoms.
