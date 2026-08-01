# Backup Content Validation Pattern (2026-06-30)

## Problem
`memory_guard.py` `fix_memory()` was restoring MEMORY.md from a corrupted backup file. The backup had 14 lines (above MIN_LINES=10) but contained broken markdown fragments — not valid structured content. Every time `--fix` ran, it overwrote good content with garbage.

## Root Cause
The validation only checked line count (`backup_non_empty >= MIN_LINES`), not content quality. A corrupted file with enough lines passed the check.

## The Fix
Added `_validate_backup_content()` that checks:
1. **Section headers**: Must have at least one `## ` line
2. **Broken fragment detection**: Counts lines that look like garbage (long bullets with backticks, em-dashes, or `skill**`)
3. **Threshold**: If >30% of content lines are broken fragments, reject the backup

```python
def _validate_backup_content(content: str) -> bool:
    lines = content.split("\n")
    has_section = any(line.strip().startswith("## ") for line in lines)
    if not has_section:
        return False
    
    broken_count = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- ") and len(stripped) > 50:
            if "`" in stripped or "—" in stripped or "skill**" in stripped:
                broken_count += 1
    
    content_lines = [l for l in lines if l.strip() and not l.startswith("#")]
    if content_lines and broken_count / len(content_lines) > 0.3:
        return False
    
    return True
```

## Key Lesson
**Always validate backup content quality, not just size metrics.** Line count, file size, and even "has sections" are necessary but not sufficient. Check for structural integrity:
- Are section headers present?
- Are content lines complete (not truncated)?
- Do lines look like intentional content (not broken fragments)?

## Applicable To
- Any file restoration from backups
- MEMORY.md, USER.md, config files, state files
- Any system that auto-restores from snapshots

## Detection Pattern
When a file keeps getting corrupted:
1. Check all writers (grep for the filename in scripts)
2. Check backup quality (don't assume backup is good)
3. Check if validation is based on metrics vs content
