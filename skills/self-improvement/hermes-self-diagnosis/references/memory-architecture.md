# Memory Architecture: Капля-Океан

## The Problem

The Hermes `memory` tool stores data in the system prompt with a **2200 character hard limit** (user profile) + **2200 character hard limit** (agent memory). Once full, new entries cannot be added — the tool rejects writes. Compression buys time but the architecture is fundamentally unscalable.

Old approach: stuff everything into memory → hit limit → compress → lose nuance → repeat.

## The Solution: Капля-Океан

A капля (drop) contains only identity + pointers. The океан (ocean) is the Knowledge Cube — a SQLite database with no size limit (currently 2119 entries, 129 domains).

**Капля (system prompt, ~300 chars):**
```
Who I am + where to find everything else.
```

**Океан (Knowledge Cube, unlimited):**
```
domain=user-preference — user's requirements, preferences, business context
domain=skill — 197 indexed skills with classification
domain=* — session knowledge, errors, patterns, conventions
```

### Principle

> A drop from the ocean contains all information about the ocean — not by containing it, but by being connected to it.

## Migration Steps

1. **Backup** current memory to `memory_backups/memory_backup_*.json`
2. **Insert** user data into Cube via direct SQL or `hooks.on_task_complete()`
3. **Clear** verbose memory entries
4. **Replace** with compact identity + pointer entries
5. **Verify** retrieval works: `recall_for_session("автономность")`

## Database Schema (Cube)

The `experiences` table:
- `raw_text` — the content
- `axis_domain` — classification domain (e.g. `user-preference`)
- `axis_outcome` — status (e.g. `stored`)
- `tags` — JSON array of tags for search
- `hash` — SHA256 for dedup

## Retrieval

```python
from auto_recall import recall_for_session
ctx = recall_for_session("автономность", top_n=3)
# Returns entries with formatted text
```

## Rollback

Backup saved at: `memory_backups/memory_backup_2026-06-10_0230.json`

Restore via `memory` tool:
```
memory(action="add", target="user", content="...")
memory(action="add", target="memory", content="...")
```

See `scripts/rollback_memory.py --list` for available backups.
