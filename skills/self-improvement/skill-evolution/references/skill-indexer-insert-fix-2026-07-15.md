# Skill Indexer INSERT Fix (2026-07-15)

## Problem
Running `skill_indexer.py` from `scripts/_deprecated/` failed with:
```
sqlite3.IntegrityError: NOT NULL constraint failed: experiences.content
```

The `experiences` table schema requires `content` and `raw_text` columns (both NOT NULL), but the INSERT statement only provided `ts`, `raw_text`, `hash`, `axis_domain`, `axis_outcome`, `tags`, `source`.

## Root Cause
The `knowledge_cube.py` schema (current) has:
```sql
CREATE TABLE IF NOT EXISTS experiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL, 
    content TEXT NOT NULL,        -- REQUIRED
    raw_text TEXT NOT NULL,       -- REQUIRED
    hash TEXT UNIQUE NOT NULL,
    axis_time_hour INTEGER, axis_time_dow INTEGER,
    axis_domain TEXT, axis_outcome TEXT,
    dynamic_axes TEXT DEFAULT '{}',
    is_white_spot INTEGER DEFAULT 0, white_spot_cluster_id TEXT,
    source TEXT, confidence REAL DEFAULT 1.0, tags TEXT DEFAULT '[]',
    importance REAL DEFAULT 0.5,
    expiration_date TEXT, verification_method TEXT DEFAULT 'manual'
);
```

But `skill_indexer.py` INSERT was:
```sql
INSERT INTO experiences
   (ts, raw_text, hash, axis_domain, axis_outcome, tags, source)
VALUES (?, ?, ?, 'skill', 'indexed', ?, 'skill-indexer')
```
Missing `content` and one `raw_text` value.

## Fix Applied
Modified two INSERT statements in `skill_indexer.py`:

### For skills (line ~424-430):
```python
conn.execute(
    """INSERT INTO experiences
       (ts, content, raw_text, hash, axis_domain, axis_outcome,
        tags, source)
       VALUES (?, ?, ?, ?, 'skill', 'indexed', ?, 'skill-indexer')""",
    (now, content, content, hash_val, json.dumps(tags + [f"action:{action_type}", f"domain:{domain}", f"output:{output_type}"]))
)
```

### For skill chains (line ~466-474):
```python
conn.execute(
    """INSERT INTO experiences
       (ts, content, raw_text, hash, axis_domain, axis_outcome,
        tags, source)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
    (now, content, content, hash_val, "skill_chain", "indexed",
     json.dumps(chain_data["tags"] + ["chain", chain_name]),
     "skill-indexer")
)
```

## Result
- **363 skills indexed** successfully
- **9 skill chains indexed** successfully
- Zero errors

## Note
The working `skill_evolution_v2.py` does NOT use a separate indexer — it embeds its own indexing logic that correctly matches the schema. The standalone `skill_indexer.py` in `_deprecated/` is a legacy script kept for reference.