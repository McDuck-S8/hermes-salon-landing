# Enrichment Queue Pattern: File-Based Tool Bridge

## Problem

Hermes tools like `web_search` are available as **direct agent tool calls**
but NOT from Python `execute_code` or `terminal` contexts (SSL error, Tavily
sandbox restrictions). When an event handler (`on_knowledge_added`) needs
web search, it can't call the tool directly.

## Solution: File-Based Queue

```
Event Handler (Python)              Agent (tool context)
       │                                     │
       ▼                                     │
write_enrichment_tasks() ──► JSON ──► enrich_next_pending()
                                  file
       │                                     │
       │                                     ▼
       │                             web_search (direct tool)
       │                                     │
       │                                     ▼
       │                             update_confidence() in DB
       │                                     │
       │                                     ▼
       │                             mark_enrichment_done()
```

The queue file lives at `cache/pending_enrichment.json`.

## Why This Works

1. **Event handler stays lightweight** — writes JSON (~10ms), doesn't block
2. **Agent consumes asynchronously** — picks up tasks when it can run web_search
3. **State is durable** — survives session kills, process restarts
4. **No polling needed** — the agent checks the queue when it makes sense,
   not on a timer (user prefers event-driven, not cron)

## Queue Schema

```json
{
  "id": "uuid-of-kc-entry",
  "domain": "referral-automation",
  "title": "SaaS реферальные программы",
  "confidence": 0.85,
  "tags": ["referral", "saas"],
  "query": "SaaS referral program affiliate recurring commission 2026",
  "created": "2026-07-13T23:47:00+00:00",
  "status": "pending | in_progress | done"
}
```

## Deduplication

Tasks are deduplicated by `id` on write — if the same concept is already
in the queue with status `pending` or `in_progress`, it won't be re-added.

## When to Consume

- After emitting a `knowledge_added` event
- At the end of a batch import session (many concepts added at once)
- When user asks "проверь концепты"
- Before a domain analysis report (enrich first, then analyze)
