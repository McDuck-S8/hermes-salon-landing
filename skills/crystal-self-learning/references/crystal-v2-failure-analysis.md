# Crystal v2.0 Failure Analysis

## What v2.0 Was
3576-line Python script with 9-phase self-consciousness loop:
observe → diagnose → forecast → horizon → will → conscience → evaluate → save → record → render

## Why It Failed

### 1. Hardcoded Dependencies
- `entity_engine.db` path hardcoded 8 times — file deleted → crash every cycle
- `SELF_MODEL_PATH` constant never defined → NameError at line 1734

### 2. Fake Analysis (will() function)
- 800 lines, 30+ branches
- Generated "analysis" from KC queries — pattern-matched output, not real reasoning
- LEARNING_TO_ACTION had 23 fixed keys that exhausted quickly

### 3. Self-Modification Was Dangerous
- Patched its own source code with crude string replace
- No versioning, no rollback, no validation

### 4. No Validation
- KC query results never checked for correctness
- SQL column name bugs (content → raw_text, domain → axis_domain) caused silent failures

### 5. No Persistent Learning
- `studied` list in self_model reset on file cleanup
- No cross-session memory of what was learned

### 6. Accumulated Tech Debt
- 19 patches applied sequentially, each fixing the previous
- No refactoring between patches
- Dead code paths accumulated

### 7. Conscience Loop Was Circular
- conscience → will → execute → evaluate → conscience
- Generated same learning_directions repeatedly
- Studied filter helped but didn't solve root cause

## What the Backup Contains
`scripts/crystal.py.BACKUP` (3576 lines, 178KB) — preserved for reference only. Do not import from it. Functions like `will()`, `_conscience()`, `_evaluate_conscience_learning()` are architecturally interesting but practically broken.

## Lessons for Future Architecture
1. State machine with clean transitions, not 800-line function with 30 branches
2. Versioned config with migration, not self-modifying code
3. Validation gate at every step
4. Persistent state in KC, not separate JSON file
5. Real metrics and thresholds, not pattern-matched output
6. Clean test coverage before adding complexity
