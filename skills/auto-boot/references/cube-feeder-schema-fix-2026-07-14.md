# Cube Feeder Schema Drift — Debug Details

## Date
2026-07-14

## Symptom
`hermes_start.py` boot failed at cube_feeder stage:
```
sqlite3.IntegrityError: NOT NULL constraint failed: experiences.content
```

## Root Cause
Two-sided schema drift between `knowledge_cube.py` and the actual SQLite DB:

1. **`add_experience()` INSERT** (line 120-123) omitted `content` column entirely
2. **`get_db()` CREATE TABLE** (line 21-29) lacked `content`, `importance`, `expiration_date`, `verification_method` that were in the actual DB

The table existed from a previous schema version or migration, but the code wasn't updated to match.

## Debug Trace

1. Read traceback → column `experiences.content` is NOT NULL
2. Checked `knowledge_cube.py:add_experience()` INSERT — no `content` column
3. Checked actual DB with `PRAGMA table_info(experiences)`:
   ```
   content TEXT NOT NULL
   importance REAL DEFAULT 0.5
   expiration_date TEXT
   verification_method TEXT DEFAULT 'manual'
   ```
4. Compared with code's CREATE TABLE — all 4 extra columns missing
5. Fix: added `content` to INSERT, synced CREATE TABLE schema

## Fix Applied
- `knowledge_cube.py:add_experience()` — added `content` to INSERT column list and parameters
- `knowledge_cube.py:get_db()` — added `content`, `importance`, `expiration_date`, `verification_method` to CREATE TABLE

## Verification
- `add_experience('test entry')` → `{'status': 'added'}`
- `add_experience('test entry')` (repeat) → `{'status': 'duplicate'}`
- Full cube_feeder run → 66 new entries added, 0 errors, KC now 3187 entries
