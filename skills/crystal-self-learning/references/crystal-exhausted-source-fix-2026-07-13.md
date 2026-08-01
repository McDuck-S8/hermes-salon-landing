# Fix: Exhausted Source Tracking in crystal.py will()

## Problem
Crystal's `will()` function repeats the same exhausted action (fabric extraction with 0 candidates) across multiple iterative cycles because failed extractions are not tracked as "done" persistently.

## Root Cause
In `will()` (crystal.py ~line 1997), when `_execute_extract()` returns 0 candidates:
```python
if chosen['id'].startswith('extract_') and chosen.get('source'):
    result = _execute_extract(chosen['source'])
    decisions.append(result)
    _save_will_history(chosen['id'], result)  # Only saves to KC history
```

The source is NOT added to `done_sources` set, so `_self_discover()` regenerates the same candidate next cycle.

Additionally, `done_sources` is a **local variable in `will()`** — it's recreated every call and doesn't persist across cycles.

## Fix Location
`scripts/crystal.py` — `will()` function, after `_execute_extract()` call (~line 2000)

## Fix Code
```python
# After _execute_extract() call, check if extraction yielded 0 candidates
if chosen['id'].startswith('extract_') and chosen.get('source'):
    result = _execute_extract(chosen['source'])
    decisions.append(result)
    _save_will_history(chosen['id'], result)
    
    # NEW: Track exhausted sources persistently
    if "0 кандидатов" in result or "не содержал новых сущностей" in result:
        # 1. Add to local done_sources for this cycle
        done_sources.add(chosen['source'])
        historical_ids.add(chosen['id'])
        
        # 2. Persist to self_model.json for cross-cycle tracking
        try:
            with open(SELF_MODEL_PATH, 'r', encoding='utf-8') as f:
                model = json.load(f)
            exhausted = model.get('sovest', {}).get('exhausted_sources', [])
            if chosen['source'] not in exhausted:
                exhausted.append(chosen['source'])
                model.setdefault('sovest', {})['exhausted_sources'] = exhausted
                with open(SELF_MODEL_PATH, 'w', encoding='utf-8') as f:
                    json.dump(model, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
```

## Also Fix: Define SELF_MODEL_PATH Constant
At module top (after line 15):
```python
SELF_MODEL_PATH = os.path.join(ROOT, "cache", "self_model.json")
```

## Also Fix: Load Exhausted Sources at will() Start
At beginning of `will()` function:
```python
# Load exhausted sources from self_model
exhausted_sources = []
try:
    with open(SELF_MODEL_PATH, 'r', encoding='utf-8') as f:
        model = json.load(f)
    exhausted_sources = model.get('sovest', {}).get('exhausted_sources', [])
except Exception:
    pass

# Add to done_sources
done_sources.update(exhausted_sources)
```

## Verification
After fix, run:
```bash
python scripts/crystal.py --iterative 3
```

Expected: Each cycle shows different action (not repeated "fabric не содержал...")

## Related Files
- `scripts/crystal.py` — main file to patch
- `scripts/clean_studied.py` — trims studied list
- `cache/self_model.json` — persists exhausted_sources

## Session Context
- Session 1 (2026-07-13 02:43): Fixed schema bug, initialized EE, 3 cycles worked (different actions)
- Session 2 (2026-07-13 15:09): Fixed INSERT bug, but cycles repeated same action
- This fix addresses the exhausted source tracking gap