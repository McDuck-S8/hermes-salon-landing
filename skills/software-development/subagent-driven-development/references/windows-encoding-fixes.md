# Windows Python Encoding Fixes

## Pattern: `ensure_ascii=True` for Windows charmap

**Problem:** Python scripts using `json.dumps(ensure_ascii=False)` fail on Windows when the hook system captures stdout with Windows' default CP1252 charmap encoding. Characters like `ñ` (U+00F1), `✓` (U+2713), `—` (U+2014) cause `'charmap' codec can't encode character`.

**Evidence (2026-06-28):**
```
inject_learnings.py: 102 errors
'charmap' codec can't encode character '\xf1' in position 9056
'charmap' codec can't encode character '\u2713' in position 9387
```

**Fix:**
```python
# BEFORE (fails on Windows):
print(json.dumps(output, ensure_ascii=False))

# AFTER (works everywhere):
print(json.dumps(output, ensure_ascii=True))
```

**Why it works:** `ensure_ascii=True` escapes all non-ASCII characters as `\uXXXX`, producing only ASCII output that any encoding can handle.

**When to apply:**
- Any Python script that outputs JSON to stdout
- Any script called as a hook (pre_llm_call, post_tool_call, etc.)
- Any script where stdout is captured by an external process

**Alternative:** Wrap stdout with UTF-8:
```python
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
```
This works for direct execution but may not work when the hook system captures stdout before the wrapper takes effect.

---

## Pattern: SQLite INSERT missing NOT NULL column

**Problem:** SQLite table has a `NOT NULL` column without a DEFAULT value. INSERT statement doesn't include that column → `sqlite3.IntegrityError: NOT NULL constraint failed`.

**Evidence (2026-06-28):**
```python
# Schema has: content TEXT NOT NULL (no default)
# INSERT was:
INSERT INTO experiences (ts,raw_text,hash,...) VALUES (?,?,?,?,...)
# Missing: content column
```

**Fix:**
```python
# BEFORE (missing content):
conn.execute("""INSERT INTO experiences (ts,raw_text,hash,...) VALUES (?,?,?,?,...)""",
    (now.isoformat(), text, h, ...))

# AFTER (added content):
conn.execute("""INSERT INTO experiences (ts,content,raw_text,hash,...) VALUES (?,?,?,?,?,...)""",
    (now.isoformat(), text, text, h, ...))  # content = duplicate of raw_text
```

**Detection:** Run the script → look for `NOT NULL constraint failed: table.column` in traceback.

**Prevention:** When schema has NOT NULL columns, always include them in INSERT. Check with:
```python
conn.execute("PRAGMA table_info tablename").fetchall()
```
