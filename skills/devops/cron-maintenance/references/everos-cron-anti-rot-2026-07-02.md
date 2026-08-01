# EverOS Anti-Rot Cron Maintenance (2026-07-02)

## Cron Layer = Tools Layer (Hours)
- Cron jobs break fastest (API changes, token expiry, script moves)
- Expect breakage, wrap don't marry
- Decision log records why each cron was chosen so cheap to re-choose

## Anti-Rot Additions to Cron Jobs

### 1. Every Cron Job Gets Revisit Line
```bash
# In cron job script header:
> Revisit: when schedule changes, script path changes, or failure threshold shifts. Last touched: 2026-07-02.
```

### 2. expiry.md Registry Includes Cron Jobs
Track all cron jobs in `scripts/cache/expiry.md`:
| File | Revisit Trigger | Last Touched | Status |
|------|-----------------|--------------|--------|
| `cron/jobs.json` | Schedule/script changes | 2026-07-02 | ✅ Current |
| `scripts/self_healing_monitor.py` | Healing logic changes | 2026-07-02 | ✅ Current |
| `scripts/telegram_cron_monitor.py` | Telegram alerts change | 2026-07-02 | ✅ Current |

### 3. Monthly maintain-os Includes Cron Audit
- Scans all Revisit dates for cron-related files
- Interviews: "Is this cron still needed? Has schedule changed? Has failure threshold shifted?"
- Auto-prunes dead jobs, updates Revisit lines

### 4. Weekly Light Scan
- `cron-maintenance` script runs weekly light check:
  - Jobs with >3 consecutive failures → alert
  - Jobs not running in 2x interval → auto-restart attempt
  - Dead script paths → flag for removal

### 5. On-Contact Fix
When editing any cron job script → update its Revisit line immediately

### Pattern: Cron Job Template with Revisit
```python
#!/usr/bin/env python3
"""
Cron Job: <name> - <description>

> Revisit: when schedule changes, script path changes, or failure threshold shifts. Last touched: 2026-07-02.
"""
# ... cron job code
```

### Files Updated
- All cron job scripts in `scripts/` now have Revisit lines
- `scripts/cache/expiry.md` includes cron layer
- `cron-maintenance` skill updated with EverOS patterns