# Audit Log Integration Guide

## Integration Points (Planned)

- **All Tool Calls** → `audit_logger.log_tool_call()` wrapper
- **Kill Switch Flips** → `audit_logger.log_switch_flip()` 
- **Agent Decisions** → `audit_logger.log_agent_decision()`
- **Data Writes** → `audit_logger.log_data_write()`
- **External Calls** → `audit_logger.log_external_call()`
- **Errors** → `audit_logger.log_error()`
- **Cron Jobs** → `audit_logger.log_cron_job()`
- **War Room** → `audit_logger.log_war_room()`

## Architecture

```
audit_log/
├── SKILL.md
├── references/
│   ├── EVENT_SCHEMA.md
│   ├── INTEGRITY.md
│   ├── QUERY_API.md
│   └── INTEGRATION_GUIDE.md
├── scripts/
│   ├── audit_logger.py
│   ├── integrity.py
│   ├── query.py
│   ├── exporter.py
│   └── hooks.py          # Auto-instrument tool calls, switches
└── templates/
    └── AUDIT_EVENT.json.template
```

## Auto-Instrumentation (hooks.py)

```python
# Wraps all tool calls automatically
@audit_hook
def tool_call(tool, args, result, duration, success):
    log_event({
        "type": "tool_call",
        "tool": tool,
        "args_hash": hash(args),
        "result_hash": hash(result),
        "duration_ms": duration,
        "success": success
    })

# Wraps kill switch changes
@audit_hook
def switch_flip(switch, old, new, reason):
    log_event({
        "type": "switch_flip",
        "switch": switch,
        "old_value": old,
        "new_value": new,
        "reason": reason
    })
```

## Event Schema (JSON)

```json
{
  "event_id": "uuid-v4",
  "timestamp": "2026-07-03T10:30:00.123Z",
  "type": "tool_call",
  "agent_id": "content",
  "session_id": "sess_abc123",
  "trace_id": "trace_xyz789",
  "payload": {
    "tool": "web_search",
    "args_hash": "sha256:...",
    "result_hash": "sha25...",
    "duration_ms": 1450,
    "success": true
  },
  "integrity": {
    "prev_hash": "sha256:...",
    "this_hash": "sha256:...",
    "chain_index": 15432
  }
}
```

## Hash Chain (Tamper Evidence)

Each event includes:
- `prev_hash` — hash of previous event
- `this_hash` = SHA256(prev_hash + JSON(payload) + timestamp)
- `chain_index` — monotonic counter

Verification: recompute chain from genesis → any break = tampering detected.

## Storage

- **Primary**: SQLite (`cache/audit_log.db`) — fast queries, local
- **Archive**: Append-only JSONL (`logs/audit/audit_YYYYMMDD.jsonl`) — immutable, portable
- **Remote** (optional): Push to SIEM / object storage

## Query API

```python
# Find all tool calls by agent in last hour
audit.query(type="tool_call", agent_id="content", since="-1h")

# Verify chain integrity
audit.verify_integrity()

# Export for compliance
audit.export(format="jsonl", since="2026-07-01", until="2026-07-03")
```

## Kill Switch
```env
HERMES_AUDIT_LOG_ENABLED=true
HERMES_AUDIT_LOG_LEVEL=full  # full | tool_calls_only | switches_only
HERMES_AUDIT_REMOTE_ENABLED=false
```