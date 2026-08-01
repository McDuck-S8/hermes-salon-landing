# Procedural Syntax Fixes (2026-07-03)

## Issue
`procedural_executor.py` contained 4,377 non-ASCII bytes causing:
- Import failures for dependent modules
- Syntax errors from unterminated strings (odd triple-quote count: 81)
- Encoding issues with Cyrillic comments, arrows (→, —), em-dashes

## Fix Applied
```bash
# Remove all non-ASCII bytes
python -c "
with open('scripts/procedural_executor.py', 'rb') as f:
    content = f.read()
cleaned = bytes([b for b for b in content if b <= 127])
with open('scripts/procedural_executor.py', 'wb') as f:
    f.write(cleaned)
"
# Then fix triple-quote count (81 → 80)
# Remove one duplicate docstring in list_triggers()
```

## Result
- File parses cleanly
- `verify_trigger.py` imports and works
- Test Harness verification runs on procedural triggers

## Lesson
**Clean non-ASCII early** when files are shared across modules. The procedural_executor was written with Russian comments and special chars that broke downstream imports. A single cleanup pass at creation would have prevented hours of debugging.

## Files
- `scripts/procedural_executor.py` — cleaned (63,733 bytes, ASCII only)
- `scripts/verify_trigger.py` — standalone verification module