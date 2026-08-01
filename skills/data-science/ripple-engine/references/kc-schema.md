# Knowledge Cube Database Schema

## Location
`cache/knowledge_cube.db` (also mirrored to `~/.hermes/cache/knowledge_cube.db`)

## Tables

### `kc_entries` (primary — used by kc_rag.py, knowledge-filter, Ripple Engine)
```sql
CREATE TABLE kc_entries (
  id TEXT PRIMARY KEY,           -- 12-char hex ID
  content TEXT,                  -- Full entry text (NO title/url columns)
  tags TEXT,                     -- Comma-separated tags
  source TEXT,                   -- Source system (see below)
  category TEXT,                 -- Classification
  importance INTEGER,            -- 0-10 importance score
  created_at TEXT,               -- ISO timestamp
  updated_at TEXT,               -- ISO timestamp
  access_count INTEGER,          -- Usage counter
  confidence REAL,               -- 0.0-1.0 confidence score
  expiration_date TEXT,          -- ISO date or NULL
  verification_method TEXT       -- How entry was verified
);
```

### `experiences` (legacy — used by knowledge_cube.py, internal entries)
```sql
CREATE TABLE experiences (
  id TEXT PRIMARY KEY,
  ts TEXT,
  raw_text TEXT,
  hash TEXT,
  axis_* TEXT,                   -- Multiple axis columns
  dynamic_axes TEXT,             -- JSON blob
  source TEXT,
  confidence REAL,
  tags TEXT
);
```

**WARNING**: These are TWO DIFFERENT tables with different schemas. Always verify which table you're querying. The filter pipeline writes to `kc_entries`. Internal agent entries may go to `experiences`.

## Known Sources (as of 2026-07-19)
| Source | Count | Description |
|---|---|---|
| scripts | 211 | Internal script documentation |
| errors | 70 | Error logs and patterns |
| knowledge_filter | 48 | Filtered external knowledge |
| github-research | 26 | GitHub repo analysis |
| arbitrage-research | 18 | Arbitrage scheme research |
| rss_* | ~40 | RSS feed entries |
| agent | 6 | Agent-generated entries |
| youtube_* | ~10 | YouTube transcript entries |
| user | 1 | User-provided entries |

## Query Patterns

### Count by source
```sql
SELECT source, COUNT(*) FROM kc_entries GROUP BY source ORDER BY COUNT(*) DESC;
```

### Filter for analysis (Ripple Engine)
```sql
SELECT id, content, tags, source, category, importance, confidence
FROM kc_entries
WHERE source IN ('arbitrage-research', 'github-research', 'agent');
```

### Search by tags
```sql
SELECT * FROM kc_entries WHERE tags LIKE '%arbitrage%';
```

### Get schema
```sql
PRAGMA table_info(kc_entries);
```

## FTS5 Search
```sql
-- Full-text search on kc_entries
SELECT * FROM kc_fts WHERE kc_fts MATCH 'arbitrage telegram';
```

## improvement_suggestions.json Structure
Located at `cache/improvement_suggestions.json`:
```json
{
  "generated_at": "ISO timestamp",
  "summary": {...},
  "suggestions": [
    {
      "id": "cluster_id",
      "priority": "critical|high|medium|low",
      "title": "suggestion title",
      "description": "detailed description",
      "tags": "comma,separated",
      "evidence": "supporting data"
    }
  ],
  "recurring_clusters": [...],
  "log_error_clusters": [...]
}
```
