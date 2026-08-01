# Revisit Injection Pattern (2026-07-02)

## Problem
Adding `Revisit:` lines to 100+ files with patch tool was corrupting long files and failing.

## Solution: sed on line 4
```bash
# For Python files (docstrings):
sed -i '4a\
\
> Revisit: when X changes. Last touched: 2026-07-02.' file.py

# For Markdown files:
sed -i '4a\
\
> Revisit: when X changes. Last touched: 2026-07-02.' file.md
```

## Why This Works
- Line 4 = after the opening `"""` in Python docstrings
- `sed` is atomic, doesn't parse file content
- Patch tool tries to match context and fails on long/duplicate content
- `a\` (append) adds after matched line

## Anti-patterns to Avoid
- `patch` tool for repetitive single-line inserts → corrupts files
- `read_file` with offset/limit before write_file → stale content
- Multiple patch attempts on same file → cascading corruption

## Files Updated (100+)
All core Hermes files across 5 layers + substrate now have Revisit lines.