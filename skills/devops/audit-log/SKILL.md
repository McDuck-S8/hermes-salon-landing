---
name: audit-log
description: Audit Log — Append-only log of every tool call, kill switch flip, state change, agent decision. Tamper-evident, queryable, compliance-ready.
---

# Audit Log — Immutable System Record

Append-only, tamper-evident log of all significant system events. Enables debugging, compliance, and post-incident reconstruction.

## Architecture

```
audit-log/
├── SKILL.md                    # This file
├── references/
│   ├── EVENT_SCHEMA.md              # JSON schema for all event types
│   ├── INTEGRITY.md                 # Hash chain / Merkle tree design
│   └── QUERY_API.md                 # How to query audit log
├── scripts/
│   ├── audit_logger.py           # Core: log_event(event_dict)
│   ├── integrity.py              # Hash chain verification
│   ├── query.py                  # Search/filter audit events
│   ├── exporter.py               # Export to SIEM / compliance formats
│   └── hooks.py                  # Auto-instrument tool calls, switches
└── templates/
    └── AUDIT_EVENT.json.template
```

## Event Types

| Type | Trigger | Fields |
|------|---------|--------|
| `tool_call` | Any tool invocation | tool, args_hash, result_hash, duration_ms, success, agent_id |
| `switch_flip` | Kill switch changed | switch, old_value, new_value, reason, user |
| `agent_decision` | Agent makes routing/strategic choice | agent, decision_type, input_hash, output_hash, confidence |
| `data_write` | KC write, file write, DB write | target, operation, record_id_hash, before_hash, after_hash |
| `external_call` | HTTP, API, LLM call | endpoint, method, request_hash, response_hash, cost_tokens |
| `error` | Unhandled exception | error_type, message_hash, stack_hash, context |
| `cron_job` | Cron start/end | job_id, status, duration_ms, output_hash |
| `war_room` | Standup/discuss | session_id, command, agents, consolidator_output_hash |

## Schema (JSON)

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
    "result_hash": "sha256:...",
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