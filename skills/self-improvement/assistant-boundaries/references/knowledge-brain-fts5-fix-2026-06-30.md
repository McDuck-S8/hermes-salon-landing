# Knowledge Brain FTS5 Integration (2026-06-30)

## Problem
`knowledge_brain.py` `_find_similar()` did brute-force keyword matching:
- Fetched ALL 3230 rows from experiences table
- Computed word overlap for each row in Python
- Required ≥2 word overlap to return results
- Result: 0 relevant experiences found for most queries

## Fix
Replaced with FTS5 full-text search:
1. Create FTS5 virtual table: `CREATE VIRTUAL TABLE IF NOT EXISTS experiences_fts USING fts5(raw_text, content='experiences', content_rowid='rowid')`
2. Populate from experiences if empty
3. Search with: `SELECT ... FROM experiences JOIN experiences_fts ON experiences.rowid = experiences_fts.rowid WHERE experiences_fts MATCH ? ORDER BY rank LIMIT 5`
4. Build MATCH query from search terms with OR joining

## _classify_action() Evolution Fix
The static keyword matching in `_classify_action()` was also fixed:
- Added `DOMAIN_TO_TOOL` dict mapping domain names to tool categories
- Made method accept `past_experiences` as optional parameter
- When past_experiences provided, aggregates domain scores weighted by experience score
- Picks highest-scoring domain → maps to best tool
- Falls back to keyword matching only when no past experiences

## Key Files
- `scripts/knowledge_brain.py` — Brain class with before()/after() methods
- `scripts/knowledge_cube.py` — cube storage (experiences table)
- `cache/knowledge_cube.db` — SQLite database with FTS5 index

## Usage
```python
from knowledge_brain import Brain
brain = Brain()
advice = brain.before("memory guard auto fill")
# Now returns relevant past experiences with FTS5 scores
```
