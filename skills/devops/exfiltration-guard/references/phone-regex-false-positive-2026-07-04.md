# Phone Regex False Positive Fix — 2026-07-04

## Problem
Exfiltration Guard falsely flagged the number `15` as a phone number, blocking `health_check.py` cron job.

**Error:**
```
Exfiltration blocked: [{'type': 'phone', 'match': '15', 'position': 35, 'length': 2}]. Quarantined: exfil_20260704_14084...
```

**Root cause:** The E.164 regex `r"\+?[1-9]\d{1,14}"` matches ANY 2+ digit number starting with 1-9.

## Fix Applied

**File:** `skills/devops/exfiltration-guard/scripts/exfil_guard.py`

**Before:**
```python
PII_PATTERNS = [
    (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "email"),
    (r"\+?[1-9]\d{1,14}", "phone"),  # E.164 — TOO BROAD
    ...
]
```

**After:**
```python
PII_PATTERNS = [
    (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "email"),
    (r"(?:\+\d{1,3}[-.\s]?)?(?:\(\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}", "phone"),  # US/Intl format
    ...
]
```

## New Pattern Logic
- Optional country code: `\+?\d{1,3}[-.\s]?` (e.g., `+1`, `+7 `, `+44 `)
- Optional area code: `\(\d{3}\)?[-.\s]?` (e.g., `(555)`, `555-`, `555 `)
- 3 digits + separator: `\d{3}[-.\s]?`
- 4 digits: `\d{4}`

**Matches:** `+1-555-123-4567`, `555-123-4567`, `(555) 123-4567`, `+7 999 123 45 67`
**Does NOT match:** `15`, `123`, `999`, `2024`, `1000`

## Testing
```python
from skills.devops.exfiltration_guard.scripts.exfil_guard import scan_outbound

# Should NOT trigger
scan_outbound("test 15")
scan_outbound("disk usage 85%")
scan_outbound("year 2024")

# Should trigger
scan_outbound("call +1-555-123-4567")
scan_outbound("phone: 555-123-4567")
scan_outbound("mobile +7 999 123 45 67")
```

## General Lesson
**Broad regex patterns cause false positives on numeric data** (PIDs, percentages, years, counts, status codes). Always use structured formats for PII detection.

## Files Modified
- `skills/devops/exfiltration-guard/scripts/exfil_guard.py` (line 38)