---
name: file-integrity
description: "Validate file content quality, detect corruption, and safely restore from backups"
trigger: When restoring files from backups, validating file content, or debugging garbage/corrupted output
---

# File Integrity & Backup Safety

## Purpose
Prevent writing garbage to files by validating content quality, not just metrics. Covers backup restoration, content validation, and debugging corrupted output.

## Core Principle
**Always validate backup content quality, not just size metrics.** Line count, file size, and "has sections" are necessary but not sufficient. Check for structural integrity.

## When to Use
- Restoring files from backups
- Validating file content before writing
- Debugging scripts that write garbage/corrupted output
- Auto-fill or auto-repair functions

## Pattern: Backup Content Validation

### The Trap
```python
# WRONG: Only checks line count
if backup_non_empty >= MIN_LINES:
    MEMORY_FILE.write_text(backup, encoding="utf-8")
```

A corrupted file with enough lines passes this check but writes garbage.

### The Fix
```python
def _validate_backup_content(content: str) -> bool:
    """Validate that backup content is readable and structured."""
    lines = content.split("\n")
    
    # Must have at least one ## section header
    has_section = any(line.strip().startswith("## ") for line in lines)
    if not has_section:
        return False
    
    # Count lines that look like broken fragments
    broken_count = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- ") and len(stripped) > 50:
            if "`" in stripped or "—" in stripped or "skill**" in stripped:
                broken_count += 1
    
    # If more than 30% of content lines are broken fragments, it's garbage
    content_lines = [l for l in lines if l.strip() and not l.startswith("#")]
    if content_lines and broken_count / len(content_lines) > 0.3:
        return False
    
    return True
```

## Detection Checklist

When a file keeps getting corrupted:

1. **Check all writers**: `grep -r "FILENAME" scripts/*.py`
2. **Check backup quality**: Don't assume backup is good — validate it
3. **Check validation logic**: Is it based on metrics vs content?
4. **Check for race conditions**: Multiple processes writing to same file?
5. **Check append vs write**: `open(file, "a")` vs `open(file, "w")`

## Structural Integrity Checks

| Check | What It Catches |
|-------|-----------------|
| Section headers present | Missing structure |
| No truncated lines | Incomplete writes |
| No broken fragments | Corrupted content |
| Logical section flow | Out-of-order writes |
| No duplicate sections | Multiple appends |

## Applicable Files
- MEMORY.md, USER.md (agent memory)
- Config files (config.yaml, jobs.json)
- State files (state.db, cache/*.json)
- Any auto-repaired file

## When No Backup Exists: Recover from __pycache__

A truncated/overwritten .py that is NOT in git and has no backup can still be
reconstructed from its compiled bytecode: `__pycache__/<name>.cpython-311.pyc`
holds the full module structure (function names, docstrings, all string
constants, imported names) via `marshal.loads(data[16:])`. Used 2026-07-31 to
rebuild a 989-line script that had been cut to 94 lines.
See `references/pyc-recovery-technique.md` for the full recipe and pitfalls.

## Related
- `self-improvement` — has `references/backup-validation-pattern-2026-06-30.md` with full case study
