# Memory Guard Auto-Fill Bug (2026-06-30)

## Problem
`memory_guard.py` `auto_fill()` writes garbage to MEMORY.md. Happened 3+ times in one session.

## Root Cause
`fix_memory()` restores a corrupted backup (`_backup/2026-06-21_pre_update/MEMORY.md`) that has 14 lines of broken fragments. The line count passes MIN_LINES=10 check, but content is garbage.

## Fix Applied
1. Added `_validate_backup_content()` function that checks:
   - Must have at least one `## ` section header
   - Detects broken fragments (long lines with backticks, em-dashes, or `skill**`)
   - Rejects backups where >30% of content lines are broken fragments
2. Updated `fix_memory()` to use validation instead of just line count
3. `auto_fill()` is now the preferred method when backup is corrupted

## When Memory Guard Reports CRITICAL
Don't just run `--fix` — it may restore the corrupted backup. Instead:
1. Check if MEMORY.md has proper content (section headers, readable text)
2. If garbage → write proper content directly, then verify with `--check`
3. The fix in memory_guard.py should prevent this going forward

## Key Files
- `scripts/memory_guard.py` — the guard with auto_fill, fix_memory, validate
- `MEMORY.md` — the memory file being protected
