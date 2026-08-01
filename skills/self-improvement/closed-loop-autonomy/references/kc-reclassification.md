# Knowledge Cube Outcome Reclassification

## Problem
KC outcomes misclassified: 71% failure rate (807/1131) because classifier used keyword matching on raw_text.

## Root Cause
- "failure" keyword in text (e.g., "failure mode analysis") → classified as failure
- "error" keyword in text (e.g., "error_logged" source) → classified as failure
- No distinction between actual crashes and text mentioning failures

## Solution
Reclassify using context-aware rules, not just keywords.

## Rules (reclassify_outcomes.py)
```python
def classify_outcome_v2(text, source, tags):
    # SUCCESS: verified results
    success_patterns = [
        r"successfully\s+(completed|finished|fixed|resolved)",
        r"tests?\s+passed",
        r"build\s+successful",
        r"merged\s+to\s+(main|master)",
    ]
    
    # FAILURE: actual crashes/errors
    failure_patterns = [
        r"traceback\s*\(most recent call last\)",
        r"(exception|error):\s*\w+error",
        r"module not found",
        r"exit code\s+[1-9]",
    ]
    
    # PARTIAL: progress without verification
    partial_patterns = [
        r"(started|begin|in progress|working on)",
        r"progress[:\s]+\d+%",
    ]
    
    # Source-based heuristics
    if "lavra_" in source:
        return "success"  # Knowledge captures are successful by definition
    if "signal" in source:
        return "success"  # Signals are data, not failures
    
    return "unknown"  # Default for ambiguous
```

## Results
- Before: success=97, partial=1, failure=807, unknown=226
- After: success=222, partial=1, failure=44, unknown=864
- Failure rate: 71% → 3.9%

## Populate Bayesian History
After reclassification, populate `cache/scorer_history.json`:
```python
# From KC outcomes
outcomes = [{"hash": h, "success": outcome == "success", "source": src, ...}]
history["outcomes"].extend(outcomes)

# From signals.jsonl
signals = [{"hash": sig["hash"], "source": sig["source"], "score": sig["score"], ...}]
history["signals"].extend(signals)
```

## Verification
```bash
python scripts/reclassify_outcomes.py  # Reclassify
python -c "import sqlite3; ..."        # Check distribution
python scripts/bayesian_scorer.py --status  # Verify scorer works
```

## Pitfall
- Don't reclassify "unknown" to "failure" — unknown means ambiguous, not failed
- Source-based rules are more reliable than text-based for KC entries
- After reclassification, always repopulate scorer_history.json
