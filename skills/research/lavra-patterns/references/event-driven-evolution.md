# Event-Driven Self-Evolution — Reference

## Event Database Schema

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    data TEXT,          -- JSON
    source TEXT DEFAULT 'system',
    priority INTEGER DEFAULT 5,  -- 1-10, higher = more important
    processed INTEGER DEFAULT 0
);

CREATE TABLE triggers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    action TEXT NOT NULL,
    cooldown_hours INTEGER DEFAULT 24,
    last_triggered TEXT,
    enabled INTEGER DEFAULT 1
);
```

## Event Types

### task_complete
- **When**: After successful task finish
- **Action**: capture_knowledge (LEARNED entry)
- **Cooldown**: 4 hours
- **Data**: {content, tags, source}
- **Priority**: 5

### error_occurred
- **When**: After error + fix applied
- **Action**: capture_investigation
- **Cooldown**: 2 hours
- **Data**: {error, fix, tags, source}
- **Priority**: 7 (errors are important)

### skill_used
- **When**: After skill execution
- **Action**: evaluate_skill (check if >500 lines)
- **Cooldown**: 24 hours
- **Data**: {skill_name, skill_path, success}
- **Priority**: 3

### session_end
- **When**: Session closes
- **Action**: session_summary
- **Cooldown**: 4 hours
- **Data**: {session_id, summary}
- **Priority**: 5

### knowledge_threshold
- **When**: Knowledge cube grows significantly
- **Action**: optimize_knowledge (dedup, cluster)
- **Cooldown**: 48 hours
- **Data**: {current_count, growth_pct}
- **Priority**: 5

### user_correction
- **When**: User corrects agent behavior
- **Action**: capture_pattern
- **Cooldown**: 12 hours
- **Data**: {correction, context}
- **Priority**: 8 (user corrections are high-value)

## CLI Commands

```bash
# Initialize
python scripts/event_quickstart.py init

# Emit events
python scripts/event_quickstart.py task "Deployed salon bot" --tags salon-bot,deployment
python scripts/event_quickstart.py error "FTS5 corrupted" --fix "Recreated database"
python scripts/event_quickstart.py skill hermes-agent --success
python scripts/event_quickstart.py correction "Use OpenCode Zen" --context "self-evolution"

# Check status
python scripts/event_quickstart.py status
python scripts/event_quickstart.py recent 10

# Demo
python scripts/event_quickstart.py demo
```

## Integration Points

### With Knowledge Capture
```python
from evolution.core.knowledge import capture_knowledge

# Event engine calls this automatically
capture_knowledge(
    entry_type="LEARNED",
    content="Deployed salon bot with aiogram3",
    tags=["salon-bot", "deployment", "auto-captured", "task-complete"],
    source="auto"
)
```

### With Auto-Recall
```python
from scripts.auto_recall import auto_recall_with_lavra

# Next session auto-recalls captured knowledge
result = auto_recall_with_lavra("salon bot deployment")
# Returns: LEARNED entry about salon bot deployment
```

### With Hermes Hooks
```python
from scripts.hermes_hooks import get_hooks

hooks = get_hooks()
hooks.on_session_start("session-001")
hooks.on_task_complete("Deploy bot", "Success", tags=["deployment"])
hooks.on_error("Connection refused", "Changed port")
hooks.on_session_end()
```

## Adding Custom Events

```python
from scripts.event_evolution import emit_event

emit_event(
    event_type="custom_event",
    data={"key": "value"},
    source="my_module",
    priority=7
)
```

## Adding Custom Triggers

```python
import sqlite3

conn = sqlite3.connect("cache/events.db")
conn.execute(
    "INSERT INTO triggers (event_type, action, cooldown_hours) VALUES (?, ?, ?)",
    ("custom_event", "my_action", 24)
)
conn.commit()
conn.close()
```

## Design Decisions

1. **Event-driven over schedule-based**: User explicitly rejected cron.
   Learning must react to what happens, not what time it is.

2. **Cooldowns prevent noise**: Without cooldowns, high-frequency events
   would flood knowledge.jsonl. Each event type has appropriate cooldown.

3. **Priority system**: Errors (7) and user corrections (8) are more
   important than routine skill usage (3). Processing order matters.

4. **JSONL storage**: Same format as Lavra knowledge.jsonl. Compatible
   with auto-recall and knowledge cube import.

5. **SQLite for events**: Simple, no dependencies, queryable. Events are
   transient — old processed events can be archived/pruned.
