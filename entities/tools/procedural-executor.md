---
id: procedural-executor
type: tool
namespace: knowledge/ai-core
status: canon
version: 1.0.0
owner: operator
created: 2026-06-29T00:00:00Z
summary: Deterministic reflex chains without LLM (trigger → action → record)
description: |
  Procedural Executor runs deterministic reflex chains for critical system events.
  No LLM involved — pure trigger → action → record patterns. Handles: dead port
  kill/restart/verify, disk>80% find/log, memory>80% find/log, gateway down
  log/escalate, API key expired refresh/fallback.
depends_on:
  - event-bus
tags:
  - deterministic
  - reflexes
  - no-llm
  - procedural-skills
confidence: 0.95
retrieval_class: hot
export_class: operator
---

# Procedural Executor — Deterministic Reflexes

## Reflex Patterns (from PROCEDURAL_SKILLS.md)

| Trigger | Chain |
|---------|-------|
| Port dead | kill_process → restart_service → verify_port |
| Disk > 80% | find_large_files → log_alert → cleanup_candidates |
| Memory > 80% | find_memory_procs → log_alert |
| Gateway missing | log_alert → escalate |
| API key expired | refresh_token → fallback_provider |

## Integration
- `scripts/procedural_executor.py` — Engine
- `skills/PROCEDURAL_SKILLS.md` — Chain definitions
- `cache/procedural_feedback.jsonl` — Feedback log
- `cache/ALERTS.md` — Alerts

## DIRECT Event Handler
Registered in `event_daemon.py` for `system_critical` events.

## Related Entities
- [[event-bus]] — Event-driven architecture
- [[signal-daemon]] — External signals