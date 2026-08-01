# Memory Guard Auto-Fill Bug — 2026-06-30

## Problem
memory_guard.py auto_fill writes garbage to MEMORY.md. Root cause: fix_memory() restores corrupted backup (14 lines of broken fragments pass MIN_LINES check).

## Fix Applied
- Added _validate_backup_content() that checks:
  - Must have at least one `## ` section header
  - Detects broken fragments (long lines with backticks, em-dashes)
  - Rejects backups where >30% of content lines are broken
- Updated fix_memory() to use validation instead of just line count
- auto_fill() now preferred when backup is corrupted

## Lesson
When validating data, check QUALITY not just QUANTITY.
Line count alone ≠ good content.