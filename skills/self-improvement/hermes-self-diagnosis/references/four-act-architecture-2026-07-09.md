# Four-Act Architecture Diagnostic Framework

**Source:** theCUBE Research (2026) — "Next Gen of AI Agents That Know, Contextualize, and Remember"
**Date:** 2026-07-09
**Purpose:** Structured lens for identifying what's missing in Hermes

## The Four Acts

| Act | Name | What It Does | Hermes Status |
|-----|------|-------------|---------------|
| 1 | LLM++ (Fluency) | Language generation, RAG, summarization | ✅ llm_client.py (Cerebras + DeepSeek) |
| 2 | Knowledge Graph | Enterprise cognition — entities, relationships, policies | ✅ Knowledge Cube + OKF-Lite |
| 3 | Contextual Spaces | Situational intelligence — "what matters NOW?" | ❌ MISSING |
| 4 | Persistent Memory | Compounding intelligence — episodic, semantic, procedural | ✅ memory tool + session_recall |

## Diagnostic Queries

### Act 1: LLM Fluency
```sql
-- Are we making LLM calls?
SELECT COUNT(*) FROM experiences WHERE source LIKE '%llm%';
-- Check tracer health
SELECT COUNT(*) FROM llm_traces WHERE status='ok';
```

### Act 2: Knowledge Graph
```sql
-- KC health
SELECT COUNT(*) as total,
       COUNT(DISTINCT axis_domain) as domains,
       AVG(confidence) as avg_confidence,
       COUNT(CASE WHEN expiration_date IS NOT NULL THEN 1 END) as with_expiry,
       COUNT(CASE WHEN verification_method != 'manual' THEN 1 END) as auto_verified
FROM experiences;
```

### Act 3: Contextual Spaces (THE GAP)
```python
# Key question: "What matters RIGHT NOW?"
# We have: static knowledge, historical data, session memory
# We're MISSING: dynamic, role-aware working context that answers:
#   - What is the current operational state?
#   - What should be prioritized given constraints/risks?
#   - What knowledge is relevant to THIS specific decision?
#
# Potential implementation:
#   - Real-time state dashboard (system health, active goals, pending tasks)
#   - Decision context builder (relevance scoring per-decision, not global)
#   - Role-based knowledge filtering (arbitrage mode vs dev mode vs research mode)
```

### Act 4: Persistent Memory
```python
# Three memory types:
#   Episodic: session_search() — what happened before
#   Semantic: Knowledge Cube — standing facts
#   Procedural: skills/ — learned workflows
# Check: are all three populated?
#   Episodic: session_search(query="test") → should return results
#   Semantic: KC query → should return relevant entries
#   Procedural: skills_list() → should show skills with real content
```

## Gap Priority

| Gap | Impact | Effort | Priority |
|-----|--------|--------|----------|
| Act 3: Contextual Spaces | HIGH — without this, agent makes decisions without situational awareness | HIGH — requires real-time state + decision scoring | P1 |
| Langfuse cloud dashboard | MEDIUM — observability without dashboard is limited | LOW — just add keys to .env | P2 |
| kc_entries population | LOW — table exists but empty, FTS5 works on experiences | LOW — run doc_intake + signal_scanner | P3 |

## Reference

- Full article: https://thecuberesearch.com/next-generation-ai-agents
- OKF spec: https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing
