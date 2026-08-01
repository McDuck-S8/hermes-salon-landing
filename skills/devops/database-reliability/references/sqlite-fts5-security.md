# SQLite FTS5 Query Injection Prevention

## The Problem

SQLite FTS5's `MATCH` operator interprets special syntax as query operators:

| Syntax | Meaning |
|--------|---------|
| `"..."`   | Phrase delimiter |
| `*`       | Prefix wildcard |
| `(` `)`   | Grouping / precedence |
| `+`       | Prefix modifier (bare column) |
| `NEAR`    | Proximity operator |
| `AND`     | Boolean intersection |
| `OR`      | Boolean union |
| `NOT`     | Boolean negation |

Passing user input directly to `MATCH` allows query injection: `hello OR 1=1` returns unintended results, `malicious*` triggers prefix scans, and malformed syntax raises exceptions (DoS).

## The Pattern: `_sanitize_fts5_query()`

```python
import re

def _sanitize_fts5_query(query):
    """Sanitize a user query for safe use with FTS5 MATCH.

    Strips FTS5 special characters and operators, then wraps in double
    quotes to force literal phrase matching. Enforces 500-char limit.
    """
    if not isinstance(query, str):
        query = str(query)
    # Strip double quotes (would break out of quoted phrase)
    query = query.replace('"', '')
    # Strip FTS5 special characters that have syntactic meaning
    query = re.sub(r'[()*+]', '', query)
    # Strip FTS5 boolean/keyword operators (case-insensitive whole words)
    query = re.sub(
        r'\b(NEAR|AND|OR|NOT)\b',
        '',
        query,
        flags=re.IGNORECASE
    )
    # Collapse whitespace from removals
    query = re.sub(r'\s+', ' ', query).strip()
    # Enforce 500-char limit
    query = query[:500]
    # Wrap in double quotes for literal phrase matching
    return f'"{query}"'
```

### How to apply

```python
# Before (vulnerable):
rows = conn.execute("SELECT ... FROM kc_fts WHERE kc_fts MATCH ?", (user_input,))

# After (safe):
safe_query = _sanitize_fts5_query(user_input)
rows = conn.execute("SELECT ... FROM kc_fts WHERE kc_fts MATCH ?", (safe_query,))
```

### Verification

Check that every `MATCH ?` parameter in the codebase goes through sanitization:

```bash
# Find unsanitized FTS5 MATCH bindings
grep -rn "MATCH ?" scripts/*.py | grep -v "safe_query"
```

## Edge Cases

| Input | Result | Why |
|-------|--------|-----|
| `""`  | `""`   | Empty sanitized → FTS5 returns no results gracefully |
| `None` | `"None"` | Cast to `str()` first, no crash |
| `"hello OR 1=1 --"` | `"hello  1=1 --"` | Operators stripped, query is literal |
| `x` × 600 | truncated to 500 chars | Length limit enforced before wrapping |
| `NEAR((a + b)) OR NOT *` | `"a  b"` | All special chars and operators removed |

## Why double-quote wrapping?

FTS5 treats a double-quoted string as a **literal phrase match** — most special characters lose their syntactic meaning inside quotes. Combined with prior stripping of `"` from the input, this guarantees the query is always treated as plain text rather than an FTS5 expression.

## References

- [SQLite FTS5 Documentation — MATCH](https://www.sqlite.org/fts5.html#full_text_query_syntax)
- Original fix: `scripts/kc_rag.py` → `_sanitize_fts5_query()` (applied 2026-07-23)
