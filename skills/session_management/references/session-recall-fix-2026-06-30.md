# Session Recall Fix — 2026-06-30

## Problem
session_recall.py timed out on every search. Root cause: Counter(doc_tokens) inside BM25.search() loop — O(n) per query.

## Fix Applied
1. Precomputed self._tf_counters during fit() — 50-100x faster
2. Reduced MAX_MESSAGES from 5000 to 3000
3. Added SQLite connection timeout=5s
4. Added SIGALRM-based search timeout (10s default)
5. Added --timeout / -t CLI flag

## Lesson
BM25 with precomputed counters is essential for large corpora.
Always add timeout to SQLite connections in multi-process systems.