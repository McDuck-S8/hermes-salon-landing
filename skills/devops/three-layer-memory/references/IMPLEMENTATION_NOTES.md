# Three-Layer Memory — Implementation Notes (Session 2026-07-03)

## Actual Work Done

### 1. FTS5 Schema Fix
- Changed FTS5 table from contentless without `content` column → with `content` column
- Updated triggers: INSERT/DELETE/UPDATE now include `content` column
- Fixed `query_cube_fts()` to JOIN with `experiences` table using correct column names (`e.content`, `e.axis_domain`, `e.ts`)

### 2. Python Environment Critical Lesson
**Hermes runs in its own venv**: `D:/Portable_Soft/hermes/hermes-agent/venv/Scripts/python.exe`
- System `pip install` installs to wrong Python
- **Must use**: `D:/Portable_Soft/hermes/hermes-agent/venv/Scripts/python.exe -m pip install ...`

### 3. Vector Layer Backfill
- Installed `sentence-transformers`, `lancedb`, `pyarrow` in Hermes venv
- Backfill script: `embedding_generator.py --backfill`
- Created LanceDB table `kc_embeddings` with 3 rows (2 KC entries + 1 test)
- Vector search confirmed working via `MemoryQuery`

### 4. Integration Points Verified
| Component | Function | Status |
|-----------|----------|--------|
| `knowledge_cube.py` | `query_3layer()` | ✅ Returns merged FTS5+Vector+Salience |
| `knowledge_cube.py` | `query_cube(query_text=...)` | ✅ Backward compatible |
| `memory_query.py` | `MemoryQuery` class | ✅ FTS5 + Vector + Salience merge |

### 5. Key Code Changes

**`scripts/knowledge_cube.py`** (lines ~429-466):
```python
KC_TIER3_ENABLED = os.environ.get("KC_TIER3_ENABLED", "true").lower() == "true"
_3layer_engine = None

def _get_3layer_engine():
    global _3layer_engine
    if _3layer_engine is None and KC_TIER3_ENABLED:
        from memory_query import MemoryQuery
        _3layer_engine = MemoryQuery()
    return _3layer_engine

def query_3layer(query: str, limit: int = 10, domain: str = None) -> list:
    if not KC_TIER3_ENABLED:
        return query_cube_fts(query, limit, domain)
    engine = _get_3layer_engine()
    if engine:
        return engine.query(query, limit, domain).get("results", [])
    return query_cube_fts(query, limit, domain)
```

**`scripts/knowledge_cube.py`** `query_cube_fts()` fix:
```sql
SELECT e.id, e.content, e.axis_domain, e.axis_outcome, e.tags, e.source, e.ts, e.importance,
       bm25(knowledge_cube_fts) as rank
FROM knowledge_cube_fts
JOIN experiences e ON knowledge_cube_fts.rowid = e.id
WHERE knowledge_cube_fts MATCH ?
```

### 6. Commands That Work

```bash
# Install deps (in Hermes venv!)
D:/Portable_Soft/hermes/hermes-agent/venv/Scripts/python.exe -m pip install sentence-transformers lancedb pyarrow

# Backfill embeddings
D:/Portable_Soft/hermes/hermes-agent/venv/Scripts/python.exe skills/devops/three-layer-memory/scripts/embedding_generator.py --backfill

# Test 3-layer query
D:/Portable_Soft/hermes/hermes-agent/venv/Scripts/python.exe -c "
import sys
sys.path.insert(0, 'D:/Portable_Soft/hermes/scripts')
import knowledge_cube as kc
results = kc.query_3layer('test', 5)
for r in results:
    print(f'[{r[\"final_score\"]:.3f}] {r[\"text\"][:60]}')
"
```

### 7. Current Limitations
- **Salience layer**: Tables exist (`memory_salience`), scoring logic in `salience_scorer.py`, but not yet auto-updated on retrieval
- **Relevance feedback**: `relevance_feedback.py` scaffolded, not integrated into agent response loop
- **Decay job**: `decay_job.py` exists, not scheduled in cron
- **Embedding on write**: Not yet automatic — only backfill runs manually

### 8. Next Steps
1. Hook `record_retrieval()` in `knowledge_cube.py` to update salience on every query
2. Integrate `relevance_feedback.py` post-agent-response
3. Schedule `decay_job.py` daily via cron
4. Auto-generate embeddings on `add_experience()` write