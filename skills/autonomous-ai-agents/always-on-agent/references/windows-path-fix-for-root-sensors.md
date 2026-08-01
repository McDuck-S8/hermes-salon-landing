# Windows Path Fix for Root-Level Sensor Scripts

**Date**: 2026-07-26
**Problem**: Root-level sensor scripts in `scripts/` (not skill scripts) use forward-slash paths that break on Windows when `HERMES_HOME` is not set in cron environment.

## Affected Scripts
- `scripts/medium_sensor_run.py` — MEDIUM sensor (hourly)
- `scripts/fast_sensor_run.py` — FAST sensor (every 30 min)

## The Bug
```python
# WRONG - breaks on Windows cron
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
# Path.resolve() mangles "D:/..." to "\d\..." (loses drive letter colon)
```

## The Fix
```python
# CORRECT - raw string preserves drive letter
HERMES_HOME = Path(os.environ.get("HERMES_HOME", r"D:\Portable_Soft\hermes"))
```

## Required Changes

### scripts/medium_sensor_run.py (line ~17)
```python
# Change from:
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
# To:
HERMES_HOME = Path(os.environ.get("HERMES_HOME", r"D:\Portable_Soft\hermes"))
```

### scripts/fast_sensor_run.py (line ~17)
```python
# Change from:
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
# To:
HERMES_HOME = Path(os.environ.get("HERMES_HOME", r"D:\Portable_Soft\hermes"))
```

## Additional Cron Config
Set `HERMES_HOME=D:\Portable_Soft\hermes` in cron job environment variables to avoid fallback entirely.

## Verification
After fix, run:
```bash
python scripts/medium_sensor_run.py
python scripts/fast_sensor_run.py
```
Both should import `gap_calculator`, `format_short_alert`, `send_short_alert`, `finance_core` without `ModuleNotFoundError`.

## Root Cause Summary
Python's `Path.resolve()` on Windows normalizes forward slashes but when the path string lacks a proper drive letter format (or comes from env var without proper escaping), the drive letter colon (`:`) gets stripped, turning `D:\Portable_Soft\hermes` into `\d\Portable_Soft\hermes`. Raw strings (`r"D:\..."`) prevent this.