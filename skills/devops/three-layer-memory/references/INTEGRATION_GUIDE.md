# Three-Layer Memory Integration Guide

## Integration Points (Implemented)

- **Knowledge Cube** (`scripts/knowledge_cube.py`) → FTS5 table + triggers + `query_cube(query_text=...)` + lazy-load 3-layer engine
- **Memory Query** (`skills/devops/three-layer-memory/scripts/memory_query.py`) → FTS5 JOIN fixed: `JOIN experiences e ON knowledge_cube_fts.rowid = e.id`
- **Embedding Generator** (`skills/devops/three-layer-memory/scripts/embedding_generator.py`) → generates embeddings on write
- **Salience Scorer** (`skills/devops/three-layer-memory/scripts/salience_scorer.py`) → usage-based scoring
- **Relevance Feedback** (`skills/devops/three-layer-memory/scripts/relevance_feedback.py`) → post-response learning
- **Decay Job** (`skills/devops/three-layer-memory/scripts/decay_job.py`) → daily archive/delete low-salience

## FTS5 Setup (Critical - Fixed)

```sql
-- Contentless FTS5 with content='experiences', content_rowid='id'
CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_cube_fts USING fts5(
    content, axis_domain, axis_outcome, tags, source,
    content='experiences', content_rowid='id'
);

-- Triggers for sync (columns MUST match FTS5 definition exactly)
CREATE TRIGGER experiences_fts_insert AFTER INSERT ON experiences BEGIN
    INSERT INTO knowledge_cube_fts(rowid, content, axis_domain, axis_outcome, tags, source)
    VALUES (new.id, new.content, new.axis_domain, new.axis_outcome, new.tags, new.source);
END;

CREATE TRIGGER experiences_fts_delete AFTER DELETE ON experiences BEGIN
    INSERT INTO knowledge_cube_fts(knowledge_cube_fts, rowid, content, axis_domain, axis_outcome, tags, source)
    VALUES ('delete', old.id, old.content, old.axis_domain, old.axis_outcome, old.tags, old.source);
END;

CREATE TRIGGER experiences_fts_update AFTER UPDATE ON experiences BEGIN
    INSERT INTO knowledge_cube_fts(knowledge_cube_fts, rowid, content, axis_domain, axis_outcome, tags, source)
    VALUES ('delete', old.id, old.content, old.axis_domain, old.axis_outcome, old.tags, old.source);
    INSERT INTO knowledge_cube_fts(rowid, content, axis_domain, axis_outcome, tags, source)
    VALUES (new.id, new.content, new.axis_domain, new.axis_outcome, new.tags, new.source);
END;
```

## Query Pattern (Fixed)

```python
# WRONG - FTS5 contentless table has no 'id' or 'content' columns directly
# SELECT id, content, ... FROM knowledge_cube_fts WHERE knowledge_cube_fts MATCH ?

# CORRECT - JOIN with experiences table
sql = """
    SELECT e.id, e.content, e.axis_domain, e.axis_outcome, e.tags, e.source, e.ts, e.importance,
           bm25(knowledge_cube_fts) as rank
    FROM knowledge_cube_fts
    JOIN experiences e ON knowledge_cube_fts.rowid = e.id
    WHERE knowledge_cube_fts MATCH ?
    ORDER BY rank LIMIT ?
"""
```

## Python Environment

```bash
# Install in HERMES venv (NOT system Python)
D:\Portable_Soft\hermes\hermes-agent\venv\Scripts\python.exe -m pip install sentence-transformers lancedb pyarrow
```

## Backward Compatibility

```python
# Original query_cube() still works for axis-based queries
query_cube(domain="coding", outcome="success", limit=50)

# New query_text parameter enables 3-layer
query_cube(query_text="test experience", limit=10)
```

## Kill Switch Environment Variables

```env
KC_TIER3_ENABLED=true       # Enable embeddings layer
KC_TIER3_MODEL=sentence-transformers/all-MiniLM-L6-v2
KC_LANCE_ENABLED=true       # Use LanceDB for vectors
KC_SALIENCE_ENABLED=true    # Enable salience scoring
KC_FEEDBACK_ENABLED=true    # Enable relevance feedback
```