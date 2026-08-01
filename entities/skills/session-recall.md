---
id: session-recall
type: skill
namespace: knowledge/ai-core
status: canon
version: 1.0.0
owner: operator
created: 2026-06-29T00:00:00Z
summary: BM25 semantic search over 2,750+ session messages
description: |
  Session Recall provides BM25-based semantic search over Hermes conversation history.
  It indexes all session dumps and enables fast retrieval of relevant context for
  the autonomous agent, crystal, event bus, and self-improvement loop.
depends_on:
  - knowledge-cube
tags:
  - bm25
  - semantic-search
  - session-history
  - fts5
confidence: 0.9
retrieval_class: hot
export_class: operator
---

# Session Recall — BM25 Semantic Search

## Overview
FTS5-backed retrieval over SQLite message store. 2,750+ messages indexed.
Used by: crystal, autonomous_agent, event_bus, self_improvement_loop.

## Capabilities
- Discovery search: `session_recall(query="topic")` → top N sessions
- Scroll: `session_recall(session_id, around_message_id, window)`
- Read full session: `session_recall(session_id)`
- Browse recent: `session_recall()`

## Integration
- `scripts/session_recall.py` — CLI and library
- `scripts/session_boot.py` — Boot-time ingestion
- `scripts/kc_populate_session.py` — Knowledge Cube population

## Related Entities
- [[knowledge-cube]] — Structured knowledge storage
- [[crystal-core]] — Self-learning loop consumer
- [[autonomous-agent]] — Decision matrix consumer