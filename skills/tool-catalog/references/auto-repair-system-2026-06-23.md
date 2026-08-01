# Auto-Repair System (2026-06-23)

## Overview
BOOT_SEQUENCE.md step 0.6: AUTO-REPAIR scans SELF_IDENTITY.md at every boot.
Departments with "Требует настройки" or "Не работает" are automatically repaired.

## Implementation
File: `scripts/session_boot.py` — function `step0_6_auto_repair()`

## How It Works
1. Read SELF_IDENTITY.md
2. Parse department status lines
3. For each degraded department:
   - Reconnaissance: install playwright-stealth
   - Proactivity: install watchdog
   - Production: create goal for demo site
4. Log results

## Usage
```bash
python scripts/session_boot.py --quick  # includes auto-repair
python scripts/session_boot.py          # full boot with auto-repair
```

## Adding New Repair Routines
Edit `step0_6_auto_repair()` in session_boot.py.
Add elif branch for new department keyword.
Example:
```python
elif "новый_отдел" in dept.lower():
    # repair logic here
    repaired += 1
```