# Silent DB Schema Mismatch — Debugging Pattern (2026-07-18)

## Symptom
Code "writes" to SQLite DB (no error), but SELECT returns 0 rows. Or: data appears during same-connection queries but disappears on reconnect.

## Root Causes Found

### 1. Schema Drift
DB was rebuilt with new schema while code uses old column names. `INSERT` fails silently via `except: pass`.

**Diagnosis:** `PRAGMA table_info(table_name)` before first INSERT.

### 2. Singleton Connection Killed
`get_db()` returns singleton, but a function calls `conn.close()`. Next `get_db()` creates fresh empty connection. Data lost.

**Diagnosis:** `print(c1 is c2)` after suspected close.

### 3. Hash Collision on UNIQUE Column
Deterministic hash produces same value for identical content. UNIQUE constraint blocks insert, hidden by `except: pass`.

**Fix:** `INSERT OR IGNORE` + include timestamp in hash: `sha256(text + timestamp)`.

### 4. Transaction Never Committed
Default isolation needs explicit `conn.commit()`. INSERT in memory but never on disk.

## Fix Pattern
1. `PRAGMA table_info()` before INSERT
2. Never close singleton connections
3. `INSERT OR IGNORE` for deterministic hashes
4. Always `conn.commit()` after batch writes
5. Replace `except: pass` with `except Exception as e: print(f"Error: {e}")`
