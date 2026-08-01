# Auto-Learning Classifier — Implementation Details

## Problem
`AdaptiveClassifier` had 9 seed rules but `learned_rules` always stayed at 0.
`learn_new_pattern()` existed but was never called automatically.

## Solution: Success-Count Auto-Learning (2026-06-22)

Added to `event_classifier.py` `record_outcome()`:

```python
def record_outcome(self, event_type, chain, outcome):
    self.history.append([event_type, chain, outcome, timestamp])
    
    # Auto-learn: if same event_type succeeds 3+ times with same chain
    chain_key = tuple(chain)
    recent = [h for h in self.history[-50:]
              if h[0] == event_type and h[2] == "success"
              and tuple(h[1]) == chain_key]
    
    if len(recent) >= 3:
        existing_chains = {tuple(r["chain"]) for r in self.rules if r.get("learned")}
        if chain_key not in existing_chains:
            self.learn_new_pattern(
                patterns=[event_type],  # or extracted input texts
                event_type=event_type,
                severity="medium",
                chain=chain,
            )
    self.save_state()
```

**Result:** 9 seed → 10 total rules after processing boot_completed events.

## Pattern: Success-Threshold Learning

```
IF same (event_type, chain) succeeds N+ times
   AND no learned rule exists for this chain
THEN create new learned rule
   patterns = most common input texts (or event_type)
   severity = medium (conservative default)
   chain = same chain that succeeded
```

**N=3** is a good threshold: enough signal to be real, not so many that it takes forever.

**When to use:** Any classifier that handles repeated similar inputs. The classifier gets BETTER at recognizing what works.

**Pitfall:** If input texts are always unique (e.g., "boot completed with different timestamps"), use event_type as pattern instead. The patterns field is for CLASSIFICATION, not for matching exact inputs.

## Event Bus → Chain Executor Bridge (2026-06-22)

`event_bus.py` `process_events()` was updated to call chain_executor:

```python
def process_events():
    from chain_executor import AdaptiveClassifier, execute_chain
    classifier = AdaptiveClassifier()
    
    for event in pending:
        result = classifier.classify(input_text)
        chain_result = execute_chain(
            result["event_type"], result["severity"],
            result["chain"], result["confidence"], input_text,
        )
```

**Before:** event_bus emitted events → mapped to cron jobs → jobs never ran.
**After:** event_bus emits → classify → execute chain steps → record outcome → auto-learn.

**Closed loop:** event → classify → execute → outcome → learn → next event classified better.

## CLI Verification

```bash
# Check classifier stats
python scripts/event_classifier.py
# → {"total_rules": 10, "seed_rules": 9, "learned_rules": 1, ...}

# Emit + process (full cycle)
python scripts/event_bus.py emit boot_completed '{"text": "boot ok"}'
python scripts/event_bus.py process
# → Chain [boot_completed]: action_completed [low] → 2/3 steps
# → [LEARNED] New rule for action_completed from 5 successes
```
