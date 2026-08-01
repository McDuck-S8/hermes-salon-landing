# User Resource Preservation — Surviving Context Compaction

**Context compaction** is a system feature that collapses long conversations into
summaries. **It does NOT save user-provided data** (URLs, file paths, commands,
corrections, or preferences) — only the summary text survives.

**Lesson learned 2026-07-26:** User gave 15 YouTube research URLs. Context
compacted. I told the user "links lost, send again" instead of finding them
myself. User was furious: "ты проебал мной потраченное время... твоя задача
ещё не проебывать что от меня!!!"

## Rule

**User-provided content must be saved to durable storage BEFORE it can be lost.**

"Later" never comes. The moment you receive a user resource, SAVE IT NOW.

## The 4-Save Pattern

When the user gives you a resource (URL, file path, command, correction):

```
receive → 1. FILE: save to cache/ or data/ 
          → 2. MEMORY: memory(action='add', target='memory')
          → 3. EVENT: emit_event('resource_received', data)
          → 4. PROCESS: immediately or queue for background
```

### Example (15 YouTube URLs)

```python
# 1. File — durable, survives anything
targets_path = Path("cache/research_targets.json")
targets_path.write_text(json.dumps({
    "source": "user",
    "youtube_urls": URLS,
}, indent=2))

# 2. Memory — injected into every future turn
memory(action='add', target='memory',
       content='15 YouTube URLs saved to cache/research_targets.json')

# 3. Event — triggers processing (if event loop is running)
emit_event("research_urls_provided", {"urls": URLS})

# 4. Process — immediately or queue
# (event handler logs to event_queue.jsonl for later consumption)
```

## Recovery: How to Find Lost Resources

If you realize a user resource was lost to compaction:

### Step 1: Check memory
The `memory` tool's content is injected every turn. If you saved it there, it's
visible. If not:

### Step 2: Query state.db directly
`session_search` only searches indexed PAST sessions. The CURRENT session's
messages (including compacted ones) are in `state.db` messages table.

```python
import sqlite3

db = sqlite3.connect("state.db")
cur = db.execute("""
    SELECT m.id, m.role, substr(m.content, 1, 500) as snippet
    FROM messages m
    WHERE m.content LIKE '%youtube.com%' OR m.content LIKE '%github.com%'
      AND m.role = 'user'
    ORDER BY m.id DESC
    LIMIT 20
""")
for row in cur.fetchall():
    print(f"msg#{row[0]} [{row[1]}]: {row[2]}")
```

Key differences from `session_search`:
- Searches ALL sessions, including current one
- Returns raw content without summarization
- Can search tool output, not just user/assistant messages
- Supports `LIKE` and `ORDER BY id DESC` for chronological search

### Step 3: Check durable files
- `cache/research_targets.json` — user-provided URLs
- `cache/session_bridge.json` — session state snapshot
- `cache/event_queue.jsonl` — event handler log

### Step 4: Check events.db
```python
db = sqlite3.connect("cache/events.db")
cur = db.execute("""
    SELECT event_type, data FROM events
    WHERE data LIKE '%youtube%' OR data LIKE '%github%'
    ORDER BY id DESC
    LIMIT 10
""")
```

## Always

- **Never ask the user to re-send** something they already sent. Find it.
- **Save before processing.** Processing can wait. Saving cannot.
- **When in doubt about context, save.** A duplicate save is harmless.
- **state.db is the source of truth** for message history. Query it directly —
  don't rely solely on `session_search`.
