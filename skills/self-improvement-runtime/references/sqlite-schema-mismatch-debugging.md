# SQLite Schema Mismatch Debugging

## The Pattern
When a DB table is rebuilt with a different schema (e.g. via migration script, `CREATE TABLE ... AS SELECT`, or manual sqlite3 CLI), code using the old schema fails silently because:
1. SQLite doesn't enforce column names on INSERT with `isolation_level=None` (autocommit)
2. `except Exception: pass` swallows the real error
3. The function reports success (`applied=1`) even though the INSERT didn't persist

## Symptoms
- INSERT "succeeds" but row count doesn't increase
- `UNIQUE constraint failed` on a column that shouldn't be unique
- Different connections show different schemas for the same table
- `PRAGMA table_info` shows different columns than expected

## Diagnosis Commands
```python
import sqlite3
conn = sqlite3.connect('path/to/db.db')

# 1. Show actual table schema
c = conn.cursor()
c.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
for name, sql in c.fetchall():
    print(f'TABLE {name}: {sql[:200]}')

# 2. Show column details
c.execute("PRAGMA table_info(table_name)")
for r in c.fetchall():
    print(r)  # (cid, name, type, notnull, dflt, pk)

# 3. Check row count
c.execute("SELECT COUNT(*) FROM table_name")
print(f'Rows: {c.fetchone()[0]}')

conn.close()
```

## Fix Pattern
1. Use `PRAGMA table_info` to get ACTUAL schema
2. Match INSERT column list to ACTUAL schema
3. Use `isolation_level=None` (autocommit) + `INSERT OR IGNORE` for dedup
4. Replace `except Exception: pass` with `except Exception as e: print(f"error: {e}")`
5. Use SHA256 hash as dedup key: `hashlib.sha256(text.encode()).hexdigest()[:16]`

## Real Case: verified_fixes.db (2026-07-18)
- Old schema: `id, issue_type, fix_description, tags, source, created_at, verified_at`
- New schema: `id, issue_hash UNIQUE, issue_type, issue_description, fix_type, fix_description, fix_content, target_file, evidence, tags, embedding, created_at, verified_at`
- Code used old schema (`source` column) -> INSERT silently failed
- 35+ "command" entries appeared because event_evolution used different code path
- Consumer reported `applied=1` but DB stayed at 6 rows
- Fix: updated all INSERT statements to match new schema + added error logging

## Prevention
When modifying a DB schema:
1. `grep -r "table_name" scripts/ --include="*.py" -l` to find ALL files
2. Update ALL of them simultaneously
3. Or use `INSERT OR IGNORE` with the actual schema
4. Never use bare `except Exception: pass` in DB operations during debugging
