# Entity Engine Schema Fixes — 2026-07-12

## Problem
`crystal.py --iterative 3` failed with two errors:

1. **UnboundLocalError in `_self_reflect()`** (line 526): `extract_done` referenced before assignment
2. **sqlite3.OperationalError**: `table entities has no column named first_seen_ts`

## Root Cause
- `entity_engine.db` existed but was empty (0 bytes, no tables)
- Crystal's `_execute_extract()` function expects `first_seen_ts` column in `entities` table
- The init script only created `last_seen_ts`, not `first_seen_ts`

## Fixes Applied

### 1. Fixed `_self_reflect()` variable scope bug
**File**: `scripts/crystal.py` line ~493
```python
def _self_reflect(history, snap):
    # Moved extract_done definition to TOP of function
    extract_done = [aid.replace('extract_', '') for aid in history if aid.startswith('extract_')]
    
    # ... rest of function uses extract_done ...
```

### 2. Created entity_engine initialization script
**File**: `scripts/init_entity_engine.py`
```python
# Creates tables: entity_types, entities, relationships
# Adds first_seen_ts column to entities table
# Seeds 11 entity types + 4 seed entities
```

### 3. Created schema fix script
**File**: `scripts/fix_entity_schema.py`
```python
# Adds missing first_seen_ts column
# Backfills existing rows: first_seen_ts = last_seen_ts
```

## Schema Requirements for Crystal
The `entities` table MUST have:
```sql
CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    type_id INTEGER,
    mention_count INTEGER DEFAULT 0,
    first_seen_ts TEXT,      -- REQUIRED by _execute_extract()
    last_seen_ts TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (type_id) REFERENCES entity_types(id)
)
```

## Verification
After running init + fix scripts:
```bash
python scripts/init_entity_engine.py
python scripts/fix_entity_schema.py
python scripts/crystal.py --iterative 3
```

Expected: 3 unique cycles with different actions each, `self_model.json` updated with `studied` and `znu` keys.

## Related Files
- `scripts/crystal.py` — main crystal logic (lines 2350, 2367 use first_seen_ts)
- `scripts/init_entity_engine.py` — initialization
- `scripts/fix_entity_schema.py` — schema patch
- `cache/self_model.json` — persists studied/znu across cycles