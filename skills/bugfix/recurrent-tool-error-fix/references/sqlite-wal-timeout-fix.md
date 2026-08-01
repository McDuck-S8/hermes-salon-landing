# SQLite WAL+Timeout — Root Cause Fix for `unable to open database`

## Problem
Self-improvement loop detected `tool_error` ×125. Root cause: SQLite concurrent access from multiple processes (`auto_recall.py`, `auto_tagger.py`, `anomaly_detector.py`, `architecture_model.py`) hitting the same `knowledge_cube.db` without write-ahead logging or busy timeout.

Default SQLite behaviour: one writer locks the entire database. A second connection fails immediately with `sqlite3.OperationalError: unable to open database file` instead of waiting.

## Fix (two lines per connection)

```python
conn = sqlite3.connect(str(db_path), timeout=5)  # Wait up to 5s for lock
conn.execute("PRAGMA journal_mode=WAL")           # Write-Ahead Logging
```

**WAL mode** lets readers proceed while a writer is active. **timeout=5** makes SQLite retry for 5 seconds before giving up, instead of failing instantly.

## Files patched this session (2026-07-19)

| File | Connection count | Before | After |
|---|---|---|---|
| `scripts/anomaly_detector.py` | 1 | raw connect | WAL + timeout=5 |
| `scripts/auto_tagger.py` | 2 | raw connect ×2 | WAL + timeout=5 ×2 |

Scripts that already had WAL (verified): `auto_recall.py`, `architecture_model.py`, `autonomous_agent.py`, `chain_heartbeat.py`.

## Verification

```python
import sqlite3
conn = sqlite3.connect('cache/knowledge_cube.db')
mode = conn.execute('PRAGMA journal_mode').fetchone()[0]
timeout = conn.execute('PRAGMA busy_timeout').fetchone()[0]
print(f"journal_mode={mode}, busy_timeout={timeout}")
# Expected: journal_mode=wal, busy_timeout=5000
```

## When to apply

- Any new script that opens `knowledge_cube.db` or any shared SQLite database
- Any existing script with `sqlite3.connect()` that lacks WAL and timeout
- After a `tool_error` spike detected by self-improvement loop
