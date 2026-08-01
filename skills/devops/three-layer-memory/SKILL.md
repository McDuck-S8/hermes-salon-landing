---
name: three-layer-memory
description: Three-Layer Memory for Knowledge Cube — FTS5 keyword search + semantic embeddings + salience scoring. Implements the AI-First Business Playbook hybrid memory pattern.
---

# Three-Layer Memory — Hybrid Memory for Knowledge Cube

Implements the AI-First Business Playbook three-layer memory pattern:
1. **Keyword Search (FTS5)** — Exact token matching, fast, precise
2. **Semantic Embeddings (LanceDB)** — Vector cosine similarity, fuzzy recall
3. **Salience Scoring** — Usage-based boost, learns what memories matter

All three layers query in parallel, merge results, weight by importance, return ranked list.

---

## Key Implementation Lessons (2026-07-03)

### FTS5 Setup (Critical)
- Use **contentless FTS5** with `content='experiences', content_rowid='id'` for sync via triggers
- FTS5 columns: `content, axis_domain, axis_outcome, tags, source` — MUST include `content` for searchable text
- Triggers must INSERT/DELETE/UPDATE with exact column names matching FTS5 definition
- Query must JOIN with `experiences` table to get `content` column: `JOIN experiences e ON knowledge_cube_fts.rowid = e.id`

### Python Environment
- Hermes uses venv at `D:\Portable_Soft\hermes\hermes-agent\venv\Scripts\python.exe`
- Install deps with: `D:\Portable_Soft\hermes\hermes-agent\venv\Scripts\python.exe -m pip install sentence-transformers lancedb pyarrow`
- System pip installs won't be visible to Hermes

### Integration Pattern
- Add `query_cube(query_text=...)` parameter for backward compatibility
- Lazy-load engine with env var guards: `KC_TIER3_ENABLED`, `KC_LANCE_ENABLED`, `KC_SALIENCE_ENABLED`
- Fallback gracefully to FTS5-only if vector/salience unavailable

## Architecture

```
three-layer-memory/
├── SKILL.md                    # This file
├── references/
│   ├── MEMORY_TIERING_GUIDE.md      # Deep dive on tiering
│   ├── EMBEDDING_STRATEGY.md        # Model selection, chunking
│   ├── SALIENCE_ALGORITHM.md        # Scoring formula, decay
│   └── RELEVANCE_FEEDBACK.md        # Post-response learning loop
├── scripts/
│   ├── memory_query.py         # Unified query across all 3 layers
│   ├── embedding_generator.py  # Generates embeddings on write
│   ├── salience_scorer.py      # Computes salience scores
│   ├── relevance_feedback.py   # Post-response learning
│   ├── decay_job.py            # Periodic decay of old memories
│   └── migration.py            # Migrate existing KC to 3-layer
├── templates/
│   └── MEMORY_ENTRY.md.template
└── examples/
    └── query_example.md
```

## The Three Layers

### Layer 1: Keyword Search (FTS5)
- **What**: SQLite FTS5 index over `memory.text`
- **When**: Exact term matches, known identifiers, error codes
- **Speed**: <10ms
- **Implementation**: Existing `knowledge_cube.db` FTS5 table

### Layer 2: Semantic Embeddings (LanceDB)
- **What**: Vector embeddings in LanceDB (or pgvector)
- **When**: Fuzzy recall, "what did I say about X", concept similarity
- **Speed**: <50ms (local LanceDB)
- **Model**: sentence-transformers/all-MiniLM-L6-v2 (384 dim, fast, free)
- **Chunking**: 512 tokens, 50 token overlap

### Layer 3: Salience Scoring
- **What**: Boost score based on past usage
- **Formula**: `salience = base_importance + retrieval_count * 0.1 + recency_boost`
- **Recency decay**: Exponential decay, half-life 30 days
- **User pinning**: Manual importance 0-1 (pins memory)

## Query Pipeline

```
User Query
    │
    ├─► FTS5 Query (keywords) ──────────────────► Results A (score 0-1)
    │
    ├─► Embed Query → LanceDB Cosine ───────────► Results B (score 0-1)
    │
    └─► Salience Boost ─────────────────────────► Results C (multiplier)
    │
    ▼
Merge + Dedupe by memory_id
    │
    ▼
Weighted Score = (0.4 * A_score) + (0.4 * B_score) + (0.2 * C_boost)
    │
    ▼
Sort by Weighted Score
    │
    ▼
Top-K → Inject into Agent Context as "Relevant Memories"
```

## Relevance Feedback Loop (Post-Response)

After agent responds:
1. Ask LLM: "Which memories did you actually use? List memory_ids."
2. For each used memory: `salience += 1.0`
3. For each unused but retrieved: `salience -= 0.1`
4. Persist updated salience

## Auto-Decay Job (Daily)

```python
# For each memory:
days_old = (now - created_at).days
recency_factor = 0.5 ** (days_old / 30)  # half-life 30 days
effective_salience = salience * recency_factor

if effective_salience < 0.05 and retrieval_count == 0:
    archive_or_delete()
```

## Kill Switch
```env
KC_TIER3_ENABLED=true       # Enable embeddings layer
KC_TIER3_MODEL=sentence-transformers/all-MiniLM-L6-v2
KC_LANCE_ENABLED=true       # Use LanceDB for vectors
KC_SALIENCE_ENABLED=true    # Enable salience scoring
KC_FEEDBACK_ENABLED=true    # Enable relevance feedback
```

## Critical: Dependency Installation
**MUST install in Hermes venv, not system Python:**
```bash
D:/Portable_Soft/hermes/hermes-agent/venv/Scripts/python.exe -m pip install sentence-transformers lancedb pyarrow
```
System Python installs will NOT work — Hermes runs in its own venv.

## Integration Points

- **knowledge_cube.py** → calls `memory_query.query()` instead of raw FTS5
- **kc_populate_session.py** → calls `embedding_generator.generate()` on write
- **session_recall.py** → enhanced with 3-layer query
- **cron** → runs `decay_job.py` daily, `relevance_feedback.py` post-response

## OKF-Lite (Knowledge Lifecycle)

Added 2026-07-09 — three fields transform KC from "fact dump" to "living knowledge base":
- `confidence` (REAL) — Bayesian confidence, affects search ranking
- `expiration_date` (TEXT) — when knowledge goes stale, enables auto-refresh
- `verification_method` (TEXT) — how to verify (manual/automated/cross-reference)

See `references/okf-lite-migration-2026-07-09.md` for full migration details, API changes, and autonomous agent integration.

## OKF v0.1 + Understory Integration (2026-07-13)

Hermes' three-layer memory is **complementary** to the Open Knowledge Format (OKF) v0.1 and the Understory project — not a replacement. Key relationship:

| Capability | Three-Layer Memory (Hermes) | Understory / OKF |
|---|---|---|
| Search | FTS5 + Vector embeddings + Salience scoring | Naive text scan only |
| Storage | SQLite Knowledge Cube | File-based OKF markdown bundles |
| Portability | Locked in SQLite | Plain markdown, diffable, git-versioned |
| Graph visualization | ❌ None | ✅ d3-force force-directed graph |
| Auto-maintenance | Dream memory (manual) | memory_maintain (orphans + broken links) |
| Session seeding | ❌ None | MCP instructions field |
| MCP tools | `query_cube` (internal) | `memory_query/add/update/status/maintain` |
| Query tracing | ❌ None | `/.traces/` with graph replay |

### Hybrid Architecture (Recommended)

```
┌────────────────────────────────────────────────────┐
│                   Hermes Agent                      │
│  ┌──────────────────────────────────────────────┐  │
│  │         Three-Layer Memory (KC)              │  │
│  │  FTS5 + LanceDB Vectors + Salience Scoring   │  │
│  │  └─ Primary search engine (best-in-class)     │  │
│  └──────────────────────────────────────────────┘  │
│                         │ dual-write               │
│                         ▼                          │
│  ┌──────────────────────────────────────────────┐  │
│  │      OKF Bundle (file-based markdown)         │  │
│  │  ~/.hermes/knowledge/ — portable, diffable    │  │
│  │  Cross-linked concepts, index.md, log.md      │  │
│  └──────────────────────────────────────────────┘  │
│                         │ MCP client               │
│                         ▼                          │
│  ┌──────────────────────────────────────────────┐  │
│  │     Understory (Docker sidecar)               │  │
│  │  Web UI + force-directed graph + trace replay │  │
│  │  MCP tools: memory_query/add/update/status    │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

**Search**: Hermes three-layer (FTS5 + vectors + salience) — keep, never replace with Understory's naive scan.
**Storage**: Dual-write to both KC (fast query) and OKF bundle (portability/graph).
**Visualization**: Understory sidecar serves the graph web UI — Hermes MCP client connects.
**Maintenance**: Hermes event system triggers periodic maintenance; Understory's memory_maintain handles lint.

### Quick Start for Understory Sidecar

```yaml
# docker-compose.understory.yml
services:
  understory:
    image: ghcr.io/thecodacus/understory:latest
    ports:
      - "3800:3800"
    volumes:
      - understory-memory:/bundle
    environment:
      BUNDLE_ROOT: /bundle
      LLM_PROVIDER: llamacpp
      LLAMACPP_BASE_URL: http://host.docker.internal:8080
```

Add to Hermes config:
```yaml
mcp_servers:
  understory:
    url: "http://localhost:3800/mcp"
```

Tools appear as `mcp_understory_memory_query`, `mcp_understory_memory_add`, etc.

### See Also

- `references/understory-okf-hybrid-2026-07-13.md` — Full research: Understory architecture, OKF v0.1 spec analysis, gap analysis, and 3-phase integration roadmap
- `D:\Portable_Soft\hermes\research\understory-okf-integration-plan.md` — Complete integration plan with step-by-step implementation

## Status (2026-07-13)

| Layer | Component | Status |
|-------|-----------|--------|
| 1 | FTS5 (SQLite) | ✅ Active — `query_cube_fts()` integrated in `knowledge_cube.py` |
| 2 | Vector (LanceDB) | ✅ Active — deps installed in Hermes venv, backfill complete (3 rows) |
| 3 | Salience (usage) | ✅ Scaffold — `salience_scorer.py`, `relevance_feedback.py`, `decay_job.py` |
| 4 | OKF Export | ✅ Active — `migrate_kc_to_okf.py --export` writes full OKF v0.1 bundle to `knowledge/okf/` |
| 5 | Live Sync | ✅ Active — `kc_rag.upsert()` auto-writes .md to OKF bundle on every DB upsert |

## OKF Export Implementation (2026-07-13)

Built on top of OKF-Lite (3 SQL columns). Full OKF SPEC v0.1 pipeline:

- **Export**: `python scripts/migrate_kc_to_okf.py --export` — full rebuild of `knowledge/okf/`
- **Validate**: `python scripts/migrate_kc_to_okf.py --validate` — checks spec compliance
- **Live sync**: Every `kc_rag.upsert()` writes one .md file to `knowledge/okf/knowledge/{category}/{id}.md`
- **Bundle**: 1003 concepts, 28 subdirectories by domain, each with `index.md`, root `log.md`
- **Frontmatter**: type, title, tags, confidence, expiration_date, verification_method

See `references/okf-export-pipeline-2026-07-13.md` for full commands, architecture, tag parsing details, and API reference.

## Dependencies (installed in Hermes venv)

```
sentence-transformers==5.3.0  # all-MiniLM-L6-v2 (384-dim)
lancedb==0.15.0
pyarrow==20.0.0
```

## Backfill Command

```bash
D:/Portable_Soft/hermes/hermes-agent/venv/Scripts/python.exe \
  skills/devops/three-layer-memory/scripts/embedding_generator.py --backfill
```