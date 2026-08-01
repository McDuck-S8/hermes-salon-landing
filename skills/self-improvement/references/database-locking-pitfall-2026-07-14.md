# Database Locking Pitfall (2026-07-14)

## What Happened
`dimension_discovery.py` (cron 04:45) fails with `sqlite3.OperationalError: database is locked` when trying to read `knowledge_cube.db`.

## Root Cause
Two daemon processes hold persistent WAL-mode connections:
- `event_daemon.py` (PID 42056, 20896) — event bus listener
- `agent_daemon.py` (PID 21100, 10444) — autonomous agent loop
- `serve_dashboard.py` (PID 35456, 11724, 30868, 45208) — dashboard server

These keep the SQLite WAL lock (`knowledge_cube.db-wal` + `-shm`) active.

## The Rule
**Never run KC readers while daemons are active** — they hold the write lock.

## Fix Options
1. **Sequential runs**: Wait for cron jobs to run at different hours (skill_evolution 04:00, dimension_discovery 04:45, but daemons run continuously)
2. **Wait & retry**: `sleep 10 && python scripts/dimension_discovery.py` in cron wrapper
3. **Read-only connection**: Use `sqlite3.connect(..., uri=True)` with `mode=ro` (but WAL still needs brief lock)
4. **Shutdown daemons** for maintenance windows (not practical for 24/7)

## Best Practice
Add to dimension_discovery.py:
```python
import time
for attempt in range(3):
    try:
        conn = get_db()
        break
    except sqlite3.OperationalError as e:
        if "locked" in str(e) and attempt < 2:
            time.sleep(5)
        else:
            raise
```

## Verified
Running `dimension_discovery.py` manually after 5s wait succeeded (output shows 5 clusters found).