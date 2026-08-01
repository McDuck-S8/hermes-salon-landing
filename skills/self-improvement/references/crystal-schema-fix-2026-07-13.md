# Crystal.py Schema Fix — 2026-07-13

## Problem
Running `python scripts/crystal.py --iterative 3` failed with:
```
sqlite3.OperationalError: no such column: r.source_entity_id
```

The query in `_self_discover()` (line ~2201) referenced non-existent columns in the `relationships` table:
- `r.source_entity_id` → should be `r.source_id`
- `r.target_entity_id` → should be `r.target_id`

## Root Cause
The `init_entity_engine.py` creates the `relationships` table with columns:
```sql
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,
    target_id INTEGER,
    relation_type TEXT,
    weight REAL DEFAULT 1.0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES entities(id),
    FOREIGN KEY (target_id) REFERENCES entities(id)
)
```

But `crystal.py` query used `source_entity_id` / `target_entity_id` (non-existent).

## Fix Applied
Patched `scripts/crystal.py` line 2204:
```sql
-- Before (broken)
LEFT JOIN relationships r ON e.id = r.source_entity_id OR e.id = r.target_entity_id

-- After (fixed)
LEFT JOIN relationships r ON e.id = r.source_id OR e.id = r.target_id
```

## Additional Work Done
1. **Entity engine DB was empty (0 bytes)** — ran `init_entity_engine.py` to create tables and seed 101 entities / 11 types
2. **Ran crystal --iterative 3** — all 3 cycles completed successfully:
   - Cycle 1: Extracted 2397 entities from white-spot-explorer (168 records)
   - Cycle 2: Extracted 649 entities from fabric (200 records)
   - Cycle 3: Fabric exhausted (0 new candidates)
3. **Verified self_model.json updated**:
   - `last_cycle`: 2026-07-13T02:49:45
   - `cycle_count`: 130
   - `studied`: 20 entries (trimmed to last 5 after)
   - `znu`: 23 keys
   - `assessments`: 20 entries

## Verification
```bash
# Check schema
sqlite3 cache/entity_engine.db ".schema relationships"

# Run crystal
python scripts/crystal.py --iterative 3
```

## Prevention
- When modifying SQL queries, always verify column names against the actual CREATE TABLE statement
- The entity_engine.db schema is defined in `scripts/init_entity_engine.py` — single source of truth
- Consider adding a schema validation step in crystal.py startup