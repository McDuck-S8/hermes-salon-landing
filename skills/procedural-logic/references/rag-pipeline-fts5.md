# RAG Pipeline — Knowledge Cube with SQLite FTS5

## Overview
Zero-dependency RAG (Retrieval-Augmented Generation) using SQLite FTS5 virtual tables. Built per user directive: RAG Pipeline +4 utility.

## Architecture
```
kc_rag.py (core engine)
    ↓
kc_entries (core table)
    ↓
kc_fts (FTS5 virtual table) — full-text search with ranking
    ↓
kc_events (event table) — async processing
    ↓
kc_populator.py (auto-fills from 5 sources)
    ↓
scripts | errors | user profile | channels | sessions
```

## Schema
```sql
-- Core entries
CREATE TABLE kc_entries (
    id TEXT PRIMARY KEY,           -- MD5 hash of content (12 chars)
    content TEXT NOT NULL,         -- Full text
    tags TEXT DEFAULT '',          -- Comma-separated tags
    source TEXT DEFAULT '',        -- scripts, errors, channels, sessions, user, research, system
    category TEXT DEFAULT '',      -- tools, issues, research, actionable, preferences, etc.
    importance INTEGER DEFAULT 5,  -- 1-10 priority
    created_at TEXT,               -- ISO timestamp
    updated_at TEXT,               -- ISO timestamp
    access_count INTEGER DEFAULT 0 -- For LRU/ranking
);

-- FTS5 virtual table (external content mode)
CREATE VIRTUAL TABLE kc_fts USING fts5(
    id, content, tags, source, category
);

-- Event queue for async processing
CREATE TABLE kc_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT,
    payload TEXT,           -- JSON
    processed INTEGER DEFAULT 0,
    created_at TEXT
);
```

## API
```python
from kc_rag import upsert, search, get_by_tags, stats, event, pending_events, mark_event_processed

# Insert/update
eid = upsert(
    content="Full text content here",
    tags="tag1,tag2",
    source="research",
    category="insights",
    importance=8
)

# Search (FTS5 ranked, fallback to LIKE)
results = search("query terms", limit=10, min_importance=5)
# Returns: [{"id", "content", "tags", "source", "category", "importance", "rank"}, ...]

# By tags
results = get_by_tags(["tag1", "tag2"], limit=20)

# Stats
s = stats()
# {"total": 256, "by_source": {...}, "by_category": {...}, "most_accessed": [...]}

# Events (async)
event("task_complete", {"task": "RAG built", "result": "working"})
evts = pending_events(limit=50)
mark_event_processed(event_id)
```

## Populator Sources (`kc_populator.py`)
| Source | Function | Typical Count | Tags |
|--------|----------|---------------|------|
| Scripts | `populate_from_scripts()` | ~96 | `script,filename` |
| Errors | `populate_from_errors()` | ~46 | `error,log` |
| User Profile | `populate_from_user_profile()` | 1 | `user,profile,preference` |
| Channels | `populate_from_channels()` | ~15 | `channel,name,actionable` |
| Sessions | `populate_from_session_dumps()` | 0-10 | `session,title` |
| Meditations | `populate_from_meditations()` | 0+ | `meditation,type` |

## Run
```bash
python scripts/kc_populator.py        # Full population (4-5s)
python scripts/kc_rag.py              # Self-test (3 inserts + search)
```

## Quality Criteria (Эталон качества)
- [ ] Zero external dependencies (stdlib sqlite3 only)
- [ ] FTS5 search returns ranked results in <50ms
- [ ] Populator covers all 5+ sources
- [ ] Upsert is idempotent (same content = same ID)
- [ ] Events table enables async processing
- [ ] Stats show source/category breakdown
- [ ] Access count tracking for LRU
- [ ] Importance filtering (1-10)
- [ ] 250+ entries after session population

## Current Stats (2026-06-28)
- Total entries: 256
- Sources: scripts(97), errors(90), research(26), channels(15), diagnosis(10), session(7), system(5), trash(3), user(2), action(1)
- Categories: tools(97), issues(90), research(26), salon_bot(8), infrastructure(7), actionable(6), x402_economy(1), telegram_mini_apps(1), self_hosted_llm(1), mcp_servers(1), litellm_integration(1), free_ai_stack(1), content_monetization(1), blocker(1), automation_stack(1), architecture(1)

## Integration Points
- `event_daemon.py` → can call `event()` for async writes
- `procedural_executor.py` → can query via `search()`
- `autonomous_agent.py` → uses stats for decision context
- `workflow_executor.py` → `kc_upsert`/`kc_search` step types