# RAG Pipeline — SQLite FTS5 Pattern (2026-06-25)

## When to Use
- Need semantic search over local data
- Zero new dependencies (sqlite3 only, already in Python stdlib)
- Replaces: grep, keyword-only search, raw JSONL dumps

## Architecture
```
Content → upsert() → kc_entries table + kc_fts (FTS5)
Search  → FTS5 MATCH → ranked results → access_count++
Events  → kc_events table → pending_events() → mark_event_processed()
```

## Key Files
- `scripts/kc_rag.py` — core: upsert, search, get_by_tags, stats, event
- `scripts/kc_populator.py` — auto-fill from scripts, errors, meditations, channels, sessions

## FTS5 Gotchas
- Don't use `content='' contentless=''` — malforms on some SQLite versions
- Plain `CREATE VIRTUAL TABLE ... USING fts5(col1, col2)` works reliably
- FTS5 MATCH syntax: `"word1 word2"` for phrase, `word1 OR word2` for OR
- Fallback to LIKE on malformed queries

## Usage Pattern
```python
from kc_rag import upsert, search, stats

# Index
upsert("Telegram proxy required from Crimea", "telegram,proxy", "infra", "network", 7)

# Search (FTS5 ranked)
results = search("proxy telegram", limit=5)

# Stats
s = stats()  # total, by_source, by_category, most_accessed
```

## Populator Sources
- scripts/ — docstring extraction
- errors.log — last 50 errors
- cache/meditation_*.json — insights from self-reflection
- memories/USER.md — user preferences
- cache/channel_analysis_*.json — research results

## Measurement (Delta-Metric)
- WAS: 0 entries in KC
- ACTIONS: kc_rag.py + kc_populator.py
- BECAME: 198 entries, FTS5 search working
- DELTA: +4 usefulness units
