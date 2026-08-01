# KC Recovery from Lavra JSONL — 2026-07-22

## Context

System was down for ~3 days (July 19-22). After reviving heartbeat (27 alerts → 0), the Knowledge Cube was found to contain only 33 architecture snapshots — zero real knowledge entries.

## Root Cause

`data/knowledge_cube.db` had only 33 rows, all `entry_type='architecture'`. The actual knowledge (decisions, facts, learnings, patterns) had been lost — likely a DB reset or migration that dropped data but preserved schema.

## Recovery Steps

### 1. Diagnose KC emptiness

```python
import sqlite3
conn = sqlite3.connect('data/knowledge_cube.db')
cur = conn.cursor()
cur.execute('SELECT entry_type, COUNT(*) FROM knowledge_cube GROUP BY entry_type')
print(dict(cur.fetchall()))
# Expected: {'architecture': N, 'decision': M, 'learned': K, ...}
# Reality: {'architecture': 33}  → BAD
```

### 2. Check for importable data

```bash
ls -la data/
# Key files:
#   data/knowledge_cube.db         — 217KB (too small for healthy system)
#   data/lavra_knowledge.jsonl     — 138KB (217 entries — recovery source)
#   data/obsidian_search.db        — 4.2MB (obsidian search index)
#   data/discoveries/              — 5 discovery entries
```

### 3. Import lavra_knowledge.jsonl into KC

The lavra file uses **double-encoded JSONL**: each line is a JSON string that itself contains an escaped JSON dict.

```python
import json, sqlite3
from datetime import datetime

conn = sqlite3.connect('data/knowledge_cube.db')
cur = conn.cursor()

# Pre-check existing IDs
cur.execute('SELECT id FROM knowledge_cube')
existing = set(r[0] for r in cur.fetchall())

imported = 0
with open('data/lavra_knowledge.jsonl') as f:
    for raw in f:
        raw = raw.strip()
        if not raw:
            continue
        # Step 1: parse the outer JSON string
        outer = json.loads(raw)
        if isinstance(outer, str):
            # Step 2: parse the inner JSON dict
            entry = json.loads(outer)
        elif isinstance(outer, dict):
            entry = outer
        else:
            continue

        kid = entry.get('key')
        if kid in existing:
            continue

        content = entry.get('content', '')
        tags = json.dumps(entry.get('tags', []))
        source = entry.get('source', 'lavra')
        ts = entry.get('ts')
        created = datetime.fromtimestamp(float(ts)).isoformat() if ts else datetime.now().isoformat()
        etype = entry.get('type', 'knowledge')

        cur.execute('''INSERT OR IGNORE INTO knowledge_cube
            (id, content, tags, source, created_at, updated_at, entry_type, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1.0)''',
            (kid, content, tags, source, created, created, etype))
        imported += cur.rowcount

conn.commit()
print(f'Imported: {imported} entries')
```

### 4. Verify import

```python
cur.execute('SELECT entry_type, COUNT(*) FROM knowledge_cube GROUP BY entry_type')
for t, c in cur.fetchall():
    print(f'  {t}: {c}')
# Expected: architecture: 33, decision: 78, learned: 59, fact: 36, pattern: 30, investigation: 14
# Total: 250 entries
```

### 5. Test recall

```python
import sys
sys.path.insert(0, 'scripts')
from auto_recall import recall_for_session
results = recall_for_session('test query', top_n=3)
print(f'Recall results: {len(results.get(\"results\",[]))}')  # Should be > 0
```

## Lavra JSONL Entry Structure

```
{key}:           str — unique ID (e.g. "decision-agents-md-is-standard")
{type}:          str — "decision" | "fact" | "learned" | "pattern" | "investigation"
{content}:       str — the knowledge text
{source}:        str — origin ("user", "agent", etc.)
{tags}:          list[str] — classifiers
{ts}:            int — Unix timestamp
{bead}:          str (optional) — associated bead ID
```

## KC Schema

```sql
CREATE TABLE knowledge_cube (
    id TEXT PRIMARY KEY,
    content TEXT,
    tags TEXT,
    source TEXT,
    created_at TEXT,
    updated_at TEXT,
    entry_type TEXT DEFAULT 'knowledge',
    confidence REAL DEFAULT 1.0
);

CREATE TABLE discoveries (
    id INTEGER PRIMARY KEY,
    topic TEXT,
    title TEXT,
    url TEXT,
    takeaway TEXT,
    relevance INTEGER,
    timestamp TEXT
);
```

## Pitfalls

- **Double-encoded JSON**: `json.loads(line)` returns a **str**, not a dict. Must call `json.loads()` again on the result.
- **Some lines vary**: occasionally a line is single-encoded (already a dict). Always check `isinstance()` before choosing decode path.
- **Key collision**: lavra `key` field maps to KC `id`. Check existing before INSERT.
- **Timestamp parsing**: lavra uses Unix float; KC uses ISO 8601 string. Convert with `datetime.fromtimestamp()`.
