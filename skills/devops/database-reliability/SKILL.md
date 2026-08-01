---
name: database-reliability
description: "SQLite reliability patterns: WAL mode, busy timeout, concurrent access guards"
trigger: Use when fixing SQLite 'database is locked' / 'unable to open database' errors, or adding new DB connections to scripts.
---

# Database Reliability — SQLite

## Root cause

Hermes uses SQLite for Knowledge Cube (`cache/knowledge_cube.db`). Multiple scripts access it concurrently:
- `kc_rag.py` (upsert)
- `auto_recall.py` (search)
- `auto_tagger.py` (classify)
- `anomaly_detector.py` (analyze)
- `architecture_model.py` (model I/O)
- `autonomous_agent.py` (agent runtime)

Default SQLite on Windows uses exclusive locking — concurrent reads/writes fail with "unable to open database".

## Fix

Every `sqlite3.connect()` must include **both** WAL mode and busy timeout:

```python
conn = sqlite3.connect(str(DB_PATH), timeout=5)           # wait 5s instead of failing
conn.execute("PRAGMA journal_mode=WAL")                    # Write-Ahead Logging — concurrent reads
conn.execute("PRAGMA busy_timeout=5000")                   # millisecond busy timeout (same as timeout=5)
conn.row_factory = sqlite3.Row                             # optional but recommended
```

### Why WAL
- Readers don't block writers and vice versa
- Much faster on concurrent access
- Still ACID compliant
- Single writer at a time, but readers proceed independently

### Why busy_timeout
- Without it, SQLite immediately raises `OperationalError` on lock contention
- With 5000ms, SQLite retries writes for 5 seconds before giving up

## Scripts that need both

| File | Fixed? |
|------|--------|
| `scripts/anomaly_detector.py` | ✅ (2026-07-19) |
| `scripts/auto_tagger.py` (×2 conns) | ✅ (2026-07-19) |
| `scripts/auto_recall.py` | ✅ (had WAL only) |
| `scripts/architecture_model.py` | ✅ (had both) |
| `scripts/autonomous_agent.py` | ✅ (via `_db_connect()`) |
| `scripts/kc_rag.py` | Check — uses `kc_connect()` helper? |

## FTS5 Query Security (Injection Prevention)

FTS5's `MATCH` operator interprets user input as a query expression — `*`, `"`, `()`, `+`, `NEAR`, `AND`, `OR`, `NOT` all have syntactic meaning. Passing unsanitized user input allows query injection and DoS via malformed syntax.

**Always sanitize user queries before FTS5 MATCH** using the `_sanitize_fts5_query()` pattern:

```python
safe_query = _sanitize_fts5_query(user_input)
rows = conn.execute("SELECT ... FROM kc_fts WHERE kc_fts MATCH ?", (safe_query,))
```

The sanitizer strips FTS5 special chars and operators, enforces a 500-char limit, and wraps the result in double quotes for literal phrase matching.

See `references/sqlite-fts5-security.md` for full pattern, edge-case table, and verification commands.

## INSERT OR IGNORE silently swallows constraint failures

`INSERT OR IGNORE` suppresses **all** constraint violations — including NOT NULL — without raising. The insert just writes 0 rows. If code then counts `inserted += 1` unconditionally, it reports rows that never landed (real case: `latent_domain_detector.py --seed` claimed 48 seeds inserted, cube actually got 0; the script's own verification count exposed it).

Rules:
- If a column is `NOT NULL`, the INSERT must provide it. Check schema with `PRAGMA table_info(table)`.
- Count **actual** rows: `cur = db.execute(...); if cur.rowcount > 0: inserted += 1 else: skipped += 1` — never trust an unconditional increment after OR IGNORE.
- Always verify with a follow-up `SELECT COUNT(*) WHERE source=?` — the script should print both and they must match.

## Verification

```bash
# Check all connections in scripts/*.py have WAL + timeout
grep -rn "sqlite3.connect" scripts/*.py | grep -v "timeout=" | grep -v "_db_connect\\|kc_connect"
# Check no unsanitized FTS5 MATCH queries exist
grep -rn "MATCH ?" scripts/*.py | grep -v "safe_query"
```
