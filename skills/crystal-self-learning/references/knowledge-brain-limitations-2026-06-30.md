# Knowledge Brain Limitations — 2026-06-30

## Current State
knowledge_brain.py has 3230 experiences in cube but returns generic recommendations.

## How it works
1. _find_similar() — searches for similar past experiences
2. _classify_action() — keyword matching → TOOL_MATRIX category
3. _check_white_spot() — checks white spots
4. detect_anomalies() — checks anomalies

## Problem
_classify_action() uses keyword matching, not semantic search.
Most queries fall through to "simple_check" → "Используй terminal".
The 3230 experiences are NOT leveraged for recommendations.

## TODO
- Replace keyword matching with FTS5 search (kc_rag.py already has this)
- Or use session_recall.py BM25 for semantic matching
- Knowledge Brain should be the DEFAULT tool before any action