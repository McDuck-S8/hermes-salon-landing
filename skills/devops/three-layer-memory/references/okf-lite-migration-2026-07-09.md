# OKF-Lite Migration — Knowledge Cube → Open Knowledge Format

**Date:** 2026-07-09
**Trigger:** Google Cloud published OKF v0.1 (June 12, 2026). User requested Knowledge Cube upgrade.

## What is OKF-Lite?

Three critical fields added to Knowledge Cube tables to transform it from "fact dump" to "living knowledge base with shelf life":

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `confidence` | REAL | 0.5 | Bayesian confidence in this knowledge (0-1) |
| `expiration_date` | TEXT | NULL | ISO timestamp when knowledge becomes stale |
| `verification_method` | TEXT | 'manual' | How to verify: manual, automated, cross-reference, official-source |

## SQL Migration

```sql
-- experiences table (already had confidence)
ALTER TABLE experiences ADD COLUMN expiration_date TEXT;
ALTER TABLE experiences ADD COLUMN verification_method TEXT DEFAULT 'manual';

-- kc_entries table (new RAG pipeline)
ALTER TABLE kc_entries ADD COLUMN confidence REAL DEFAULT 0.5;
ALTER TABLE kc_entries ADD COLUMN expiration_date TEXT;
ALTER TABLE kc_entries ADD COLUMN verification_method TEXT DEFAULT 'manual';
```

## API Changes (kc_rag.py)

### upsert() — now requires verification_method
```python
upsert(
    content="...",
    confidence=0.85,              # NEW: Bayesian confidence
    verification_method="cross-reference",  # NEW: how to verify
    expiration_date="2027-01-01T00:00:00"  # NEW: when it expires
)
```

### search() — confidence-weighted ranking
```python
# Old: pure FTS5 score
# New: 0.3 × confidence + 0.7 × fts_score
# High-confidence knowledge ranks higher in results
```

### find_expired_knowledge() — NEW function
```python
expired = find_expired_knowledge(limit=100)
# Returns entries where expiration_date < now
# Used by autonomous_agent.py for [SURVIVE] action
```

### find_expiring_soon(days) — NEW function
```python
expiring = find_expiring_soon(days=30)
# Returns entries expiring within N days
# Proactive refresh before expiration
```

## Autonomous Agent Integration

New action in `autonomous_agent.py`:
```
[SURVIVE] Refresh expired knowledge
  Tier: 1 (SURVIVE) when >10 expired entries
  Urgency: 8, Impact: 7
  Logic: remove low-confidence (<0.3) expired, keep high-confidence for re-verification
```

## OKF v0.1 Spec (Google Cloud, June 2026)

- Knowledge = directory of markdown files with YAML frontmatter
- Only mandatory field: `type`
- Design: minimally opinionated, producer/consumer independent
- Reference: github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf

## Four-Act Architecture (theCUBE Research 2026)

OKF-Lite maps to **Act 2 (Knowledge Graph)** in the four-layer framework:
- Act 1: LLM++ fluency → llm_client.py
- Act 2: Knowledge Graph → KC + OKF-Lite ← WE ARE HERE
- Act 3: Contextual Spaces → MISSING (what matters NOW?)
- Act 4: Persistent Memory → memory tool, session_recall

**Gap:** Act 3 (Contextual Spaces) is the next upgrade target.
