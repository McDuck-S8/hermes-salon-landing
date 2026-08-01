# MEMORY.md — All Paths and Fixes (2026-06-29)

## Problem
Multiple scripts pointed to different MEMORY.md locations:
- `scripts/crystal/executor.py` → `memories/MEMORY.md` (WRONG)
- `scripts/crystal/memory_integration.py` → `memories/MEMORY.md` (WRONG)
- `scripts/memory_guard.py` → `memories/MEMORY.md` (WRONG)
- Hermes startup → `MEMORY.md` at root (CORRECT)

Result: Crystal wrote to `memories/MEMORY.md`, Hermes couldn't find `MEMORY.md` at root.
User saw: `[File not found: MEMORY.md]` on every startup.

## Fix Applied

### 1. All scripts now point to root
```python
# memory_guard.py
MEMORY_FILE = HERMES_HOME / "MEMORY.md"

# crystal/executor.py
memory_file = os.path.join(HERMES_HOME, "MEMORY.md")

# crystal/memory_integration.py
self.memories_dir = HERMES_HOME  # was: os.path.join(HERMES_HOME, "memories")
```

### 2. Symlink safety net
```bash
# memories/MEMORY.md → root MEMORY.md
mklink D:\Portable_Soft\hermes\memories\MEMORY.md D:\Portable_Soft\hermes\MEMORY.md
```

Any script writing to `memories/MEMORY.md` now actually writes to root.

### 3. Health check cron
- `memory-guard` cron: every 10m, checks MEMORY.md existence
- `health-check` cron: every 15m, full system verification

## Verification
```bash
# Check symlink
ls -la memories/MEMORY.md  # should show -> /d/Portable_Soft/hermes/MEMORY.md

# Check all scripts point to root
grep -rn "MEMORY" scripts/memory_guard.py scripts/crystal/executor.py scripts/crystal/memory_integration.py | grep -v "if\|with\|return\|print\|join\|exists"

# Run health check
python scripts/health_check.py  # should be 10/10 OK
```

## Lesson
When a file has a canonical location that other processes depend on, ALL writers must agree on that location. Use symlinks as safety nets, but fix the root cause (wrong paths in scripts) first.
