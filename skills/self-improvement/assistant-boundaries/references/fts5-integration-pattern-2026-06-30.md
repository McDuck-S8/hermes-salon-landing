# FTS5 Integration Pattern (2026-06-30)

## Problem
knowledge_brain.py `_find_similar()` did primitive word overlap matching:
- Fetched ALL 3230 rows from experiences table
- Split each into words, removed stop words
- Counted overlap (≥2 words required)
- No BM25, no FTS5, no semantic search

Meanwhile, session_recall.py had full BM25 + TF-IDF implementation.

## Solution
Replaced `_find_similar()` with FTS5 search:
1. Create FTS5 virtual table: `CREATE VIRTUAL TABLE IF NOT EXISTS experiences_fts USING fts5(raw_text, content='experiences', content_rowid='rowid')`
2. Populate if empty: `INSERT INTO experiences_fts(rowid, raw_text) SELECT rowid, raw_text FROM experiences`
3. Search: `SELECT raw_text, axis_domain, axis_outcome, tags FROM experiences JOIN experiences_fts ON experiences.rowid = experiences_fts.rowid WHERE experiences_fts MATCH ? LIMIT 5`

## Result
- Before: 0 past experiences found (word overlap ≥2 rarely matched)
- After: 5 past experiences with FTS5 rank scores (19.11, 18.23, 14.81, etc.)

## Lesson
When using existing scripts, RUN THEM FIRST. Docstrings say "Active Brain" but code does word matching. Only testing reveals the gap.

## Files Modified
- `scripts/knowledge_brain.py` — `_find_similar()` method replaced with FTS5 search
