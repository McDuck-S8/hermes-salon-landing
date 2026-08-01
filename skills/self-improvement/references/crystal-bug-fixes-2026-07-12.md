# Crystal.py Bug Fixes — 2026-07-12

## Problems Found

Running `python scripts/crystal.py --iterative 3` failed with two bugs:

### 1. UnboundLocalError in `_self_reflect()` 
**Location**: `scripts/crystal.py` line ~526
**Error**: `cannot access local variable 'extract_done' where it is not associated with a value`
**Cause**: Variable `extract_done` defined inside `if recent:` block but used outside it
**Fix**: Move `extract_done` definition to top of function (before the `if recent:` block)

### 2. Missing `first_seen_ts` column in entity_engine.db
**Location**: `scripts/crystal.py` lines 2350, 2367 in `_execute_extract()`
**Error**: `sqlite3.OperationalError: table entities has no column named first_seen_ts`
**Cause**: Entity Engine initialization script only created `last_seen_ts` column
**Fix**: Add `first_seen_ts` column via ALTER TABLE, backfill with `last_seen_ts` values

## Fixes Applied

### Fix 1: Variable scope bug in crystal.py
```python
def _self_reflect(history, snap):
    # Define FIRST, before any conditionals
    extract_done = [aid.replace('extract_', '') for aid in history if aid.startswith('extract_')]
    
    # Then use anywhere in function
    recent = list(history.items())[-10:]
    if recent:
        # ...
    # ...
    untouched = {s: c for s, c in orphans_raw.items() if s not in extract_done}
```

### Fix 2: Schema migration scripts
**File**: `scripts/init_entity_engine.py` — Creates tables with correct schema including `first_seen_ts`
**File**: `scripts/fix_entity_schema.py` — Adds missing column to existing DB

```sql
ALTER TABLE entities ADD COLUMN first_seen_ts TEXT;
UPDATE entities SET first_seen_ts = last_seen_ts WHERE first_seen_ts IS NULL;
```

## Required Schema for Crystal

```sql
CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    type_id INTEGER,
    mention_count INTEGER DEFAULT 0,
    first_seen_ts TEXT,      -- REQUIRED
    last_seen_ts TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (type_id) REFERENCES entity_types(id)
)
```

## Verification

After fixes:
```bash
python scripts/init_entity_engine.py
python scripts/fix_entity_schema.py
python scripts/crystal.py --iterative 3
```

Expected: 3 unique cycles with different actions each, `self_model.json` updated with `studied` and `znu` keys.

## Related Files
- `scripts/crystal.py` — main crystal logic (lines 493-530, 2350, 2367)
- `scripts/init_entity_engine.py` — initialization script
- `scripts/fix_entity_schema.py` — schema patch script
- `cache/self_model.json` — persists studied/znu across cycles