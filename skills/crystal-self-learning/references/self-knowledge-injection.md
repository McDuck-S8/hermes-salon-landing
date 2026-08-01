# Self-Knowledge Injection Protocol

**⚠️ LEGACY — superseded by Level 4 (self-code-level4.md)**

The crystal now reads its own source code directly (`self_code_audit` action → file I/O).
This KC-injection approach is preserved as reference only. The direct file-read approach
is simpler and doesn't depend on KC having the right domain/classifier/entries.

## Original Protocol (kept for history)

### Goal
Give crystal awareness of its own architecture, source code, and capabilities so it can self-improve.

### Problem
1. `_conscience()` uses `LIMIT 20` — ignores domains with few entries
2. `_conscience()` reads metadata, not entry content (`raw_text`)
3. Auto-classifier overrides explicit `domain` in `dynamic_axes`

### Why Level 4 replaced this
Level 4 (`self_code_audit`) reads `scripts/crystal.py` directly from disk instead of going through KC:
- No dependency on KC query results
- No LIMIT 20 cutoff issue
- No domain classification problems
- Can read the ENTIRE file, not just 5000-chars
- Can MODIFY code, not just read it
