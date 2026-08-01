---
id: knowledge-cube
type: knowledge
namespace: knowledge/ai-core
status: canon
version: 1.0.0
owner: operator
created: 2026-06-29T00:00:00Z
summary: Structured knowledge storage with domains, categories, and embeddings
description: |
  Knowledge Cube is the structured knowledge layer of Hermes. Organizes knowledge
  into domains (ai-architecture, arbitrage, finance, etc.) with categories and
  entries. Supports semantic search via embeddings and BM25 via session_recall.
  Feeds crystal self-learning loop and autonomous agent decision matrix.
depends_on:
  - session-recall
  - crystal-core
tags:
  - knowledge-storage
  - domains
  - embeddings
  - semantic-search
confidence: 0.95
retrieval_class: hot
export_class: operator
---

# Knowledge Cube — Structured Knowledge Storage

## Architecture
```
Knowledge Cube
├── Domains (ai-architecture, arbitrage, finance, ops, research, infra, personal)
│   ├── Categories
│   │   └── Entries (id, content, tags, embeddings, metadata)
```

## Domains
| Domain | Purpose | Status |
|--------|---------|--------|
| ai-architecture | Agent architecture, patterns, best practices | Active |
| arbitrage | Traffic sources, monetization, schemes | Active |
| finance | CPA networks, revenue models, projections | Active |
| ops | Infrastructure, deployment, monitoring | Active |
| research | White papers, trends, experiments | Active |
| infra | Hermes internals, config, scripts | Active |
| personal | Operator profile, preferences, pillars | Active |

## Key Files
- `scripts/knowledge_cube.py` — Core operations
- `scripts/kc_feeder.py` — Ingestion
- `scripts/kc_rag.py` — RAG retrieval
- `scripts/kc_populator.py` — Population from sessions

## Related Entities
- [[session-recall]] — BM25 search
- [[crystal-core]] — Consumer (self-learning)
- [[autonomous-agent]] — Consumer (decision matrix)