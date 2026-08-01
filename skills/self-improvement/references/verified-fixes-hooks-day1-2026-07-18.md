# Verified Fixes Pipeline — Day 1 Activation (2026-07-18)

## Problem
Self-improvement conversion was **0.27%** (17,704 suggestions → 19 skills). Root cause: the "Verified Fixes" pipeline was dead at every stage:
1. `verified_fixes.db` — empty (0 tables)
2. `knowledge_cube.db` — empty (0 tables)
3. `events.db` — schema existed but cross-connection commits invisible (isolation level issue)
4. Hooks (`hermes_hooks.py` → `event_evolution.py`) never wrote to verified_fixes
5. `self_improvement_loop.py` read from empty DBs → generated noise-only suggestions

## Solution: 3 Database Initializations + Hook Wiring

### 1. Knowledge Cube Schema
```python
from scripts.knowledge_cube import get_db
conn = get_db()  # Creates experiences, dimensions, white_spot_clusters, kc_entries + FTS tables
```

### 2. Verified Fixes DB
```sql
CREATE TABLE IF NOT EXISTS verified_fixes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_type TEXT NOT NULL,
    fix_description TEXT NOT NULL,
    tags TEXT DEFAULT '[]',
    source TEXT DEFAULT 'manual',
    created_at TEXT DEFAULT (datetime('now')),
    verified_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_vf_type ON verified_fixes(issue_type);
CREATE INDEX IF NOT EXISTS idx_vf_verified ON verified_fixes(verified_at);
```

### 3. Events DB — Fixed Cross-Connection Visibility
```python
# In EventMonitor._init_db():
conn = sqlite3.connect(str(EVENTS_DB), isolation_level=None)  # AUTOCOMMIT
conn.execute("PRAGMA journal_mode=WAL")
# Now commits from one connection visible to others immediately
```

### 4. Hook Wiring — Direct Write on Error/Fix
**event_evolution.py:on_error()** now writes directly:
```python
def on_error(error: str, fix: str = "", tags: list[str] = None, source: str = "agent"):
    emit_event("error_occurred", {...})  # existing event bus
    # ALSO write to verified_fixes for self-improvement loop
    conn = sqlite3.connect(CACHE_DIR / "verified_fixes.db")
    conn.execute(
        "INSERT INTO verified_fixes (issue_type, fix_description, tags, source) VALUES (?, ?, ?, ?)",
        (tags[0] if tags else "unknown", fix or error, json.dumps(tags or []), source)
    )
    conn.commit()
    conn.close()
```

**event_evolution.py:on_task_complete()** writes when verified:
```python
def on_task_complete(content: str, tags: list[str] = None, source: str = "agent", verified: bool = False, evidence: str = ""):
    emit_event("task_complete", {...})
    if verified and evidence:
        # Write to verified_fixes
        conn = sqlite3.connect(CACHE_DIR / "verified_fixes.db")
        conn.execute(
            "INSERT INTO verified_fixes (issue_type, fix_description, tags, source) VALUES (?, ?, ?, ?)",
            (tags[0] if tags else "proactive_fix", evidence, json.dumps(tags or []), source)
        )
        conn.commit()
        conn.close()
```

## Result: Verified Fixes Now Accumulate

**Test run:**
```python
from scripts.hermes_hooks import get_hooks
hooks = get_hooks()
hooks.on_session_start('demo')
hooks.on_error('Timeout on terminal call', 'Added 60s timeout param', ['timeout','command'])
hooks.on_task_complete('Fixed timeout', 'Commands complete in <30s', ['command','timeout'], verified=True, evidence='Added timeout=60 to terminal tool')
hooks.on_session_end()
```

**DB state after:**
```
verified_fixes: 7 entries (5 seed + 2 from hooks)
- command: 2 (timeout fix, execution fix)
- log_artifact: 1
- telegram_error: 1
- network_connect: 1
- tool_error: 1
```

**Self-improvement loop output:**
```
Loaded 7 verified fixes from D:\Portable_Soft\hermes\cache\verified_fixes.db
Loaded 4444 experiences from D:\Portable_Soft\hermes\cache\knowledge_cube.db
Found 1 recurring issue clusters from fixes
  command: count=30  ← now detected!
Generated 33 improvement suggestions
```

## Key Insight: Write Path > Read Path
The self-improvement loop's `load_verified_fixes()` was fine. The problem was **nothing wrote to it**. The fix wasn't reading better — it was wiring the write path so real fixes accumulate during normal agent operation.

## Files Modified
- `scripts/knowledge_cube.py` — use `hermes_config.CACHE_DIR` (unified path)
- `scripts/event_evolution.py` — `on_error()`, `on_task_complete()` write to verified_fixes.db; `isolation_level=None` for events.db
- `scripts/self_improvement_loop.py` — already reads from correct paths via hermes_config

## Next (Day 2)
1. Filter log noise: exclude `log_artifact` (141), `telegram_timeout` (150) from error clusters
2. Make auto-skills executable (patch files + tests, not TODO checklists)
3. Add suggestion consumer cron that applies top fix