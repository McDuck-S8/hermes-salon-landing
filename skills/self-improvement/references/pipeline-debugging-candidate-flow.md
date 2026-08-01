# Pipeline Debugging: Candidate Flow Tracing

## When to Use

Any pipeline that filters candidates through stages and produces "nothing to do" or empty output.
Common in: crystal will(), agent task selection, rule engines, recommendation systems.

## Pattern: Targeted Stderr Prints

```python
import sys

# At each pipeline stage:
print(f"[DEBUG stage_name] input={len(candidates)} output={len(filtered)}", file=sys.stderr)

# At decision points:
print(f"[DEBUG] condition=True/False reason=...", file=sys.stderr)
```

Run with: `python script.py 2>&1 | grep DEBUG`

## Common Failure Modes

### 1. Accumulated State Exhaustion
**Symptom**: Pipeline works first run, then "nothing to do" on subsequent runs.
**Root cause**: State (history, learning, preferences) accumulates across ALL past runs.
**Fix**: Sliding window — only check recent N entries:
```python
# BAD: checks all history
prev = set(all_entries)
# GOOD: checks last 5
prev = set(all_entries[-5:])
```

### 2. Mapping Mismatch
**Symptom**: Candidates generated but not matched to actions.
**Root cause**: Text in candidate doesn't exactly match mapping key (encoding, whitespace).
**Fix**: Debug with repr():
```python
print(f"[DEBUG] key={repr(key)} match={key==mapping}", file=sys.stderr)
```

### 3. Guard Condition Too Broad
**Symptom**: Candidate filtered out by `if X not in historical_ids` when X is already there.
**Root cause**: Previous run already executed this candidate.
**Fix**: Either clear history or add new candidate types.

### 4. Efficiency Threshold Misclassification
**Symptom**: Actions with efficiency=0.0 but "success" text produce no learning.
**Root cause**: Regex/classification doesn't match the actual result text pattern.
**Fix**: Print the result_text to see what patterns are present:
```python
print(f"[DEBUG] result_text={repr(result_text[:200])}", file=sys.stderr)
```

## Verification

After fixing, run with `--iterative N` and verify:
1. Each cycle produces a DIFFERENT action (not "всё сделано")
2. Actions are from different types (not all same category)
3. No duplicate actions across cycles
