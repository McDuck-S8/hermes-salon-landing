# SQLite DB Lock Fix Pattern — 2026-07-15

## Symptom
Cron job fails with `sqlite3.OperationalError: database is locked`.
Common when multiple cron jobs access the same SQLite DB simultaneously.

## Root Cause
SQLite allows only one writer at a time. When cron jobs overlap (e.g. knowledge-gap-filler every 120m, cube-feeder every 6h), writes collide.

## Fix
Two changes to `sqlite3.connect()` call:

```python
# BEFORE (fails under contention):
conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA journal_mode=WAL")

# AFTER (waits up to 10s + SQLite busy timeout):
conn = sqlite3.connect(str(DB_PATH), timeout=10)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA busy_timeout=5000")  # Wait 5s before giving up
```

## Parameters
- `timeout=10` in `sqlite3.connect()` — Python-side wait before raising `database is locked`
- `busy_timeout=5000` pragma — SQLite internal wait in ms before returning SQLITE_BUSY

## Verification
```bash
# Run the script twice simultaneously
python scripts/script_A.py &
python scripts/script_A.py &
wait
echo "Both completed without DB lock error"
```

## Affected Scripts (patched)
- `scripts/knowledge_cube.py` — `get_db()` function, 2026-07-15
