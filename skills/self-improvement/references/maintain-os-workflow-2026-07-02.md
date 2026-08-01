# Maintain-OS Workflow Design (2026-07-02)

## EverOS-Inspired Maintenance Cadence for Hermes

Based on EverOS ROT.md model: monthly auto + weekly light + on-contact.

## Monthly Auto (maintain-os)

**Trigger**: Cron job `0 4 1 * *` (1st of month 04:00)

**Workflow**:
1. **Scan Revisit Dates** - Read all `> Revisit:` lines from tracked files
2. **Identify Overdue** - Files where last touched > trigger threshold
3. **Interview** - Present multiple-choice questions for each overdue file:
   - "Is this file still needed?"
   - "Has the trigger condition changed?"
   - "Update Revisit line?"
   - "Archive/remove?"
4. **Apply Updates** - User answers → update Revisit lines, expiry.md, archive if needed
5. **Report** - Summary of changes to MEMORY.md

**Token Budget**: ~10k tokens per run (5 minutes of user tapping)

## Weekly Light Scan

**Trigger**: Cron job `0 4 * * 1` (Monday 04:00)

**Checks**:
1. **Cron Health** - Jobs with >3 failures, dead paths, 2x interval overdue
2. **Proxy/Gateway** - Network connectivity, gateway PID alive
3. **Disk/Memory** - >80% usage → auto-clean + alert
3. **Stale Files** - Files with Revisit overdue >2x threshold
4. **Error Backlog** - Recent errors >10 in last 24h

**Output**: `cache/maintenance_light_YYYY-MM-DD.json` + Telegram alert if issues

## On-Contact Fix (Every Edit)

**Rule**: When you edit any file with a Revisit line → update it immediately

**Pattern**:
```bash
# Before editing
# After editing: update Revisit line date and trigger if changed
sed -i 's/> Revisit: .* Last touched: .*/> Revisit: when <new-trigger>. Last touched: 2026-07-02./' file.py
```

## Sync Script (sync_expiry.py)

**Purpose**: Regenerate `scripts/cache/expiry.md` from all Revisit: lines

**Usage**:
```bash
python scripts/cache/sync_expiry.py
```

**Output**: expiry.md with all files organized by layer, triggers, dates, status

## Implementation Status

- ✅ Revisit lines on 50+ core files
- ✅ expiry.md registry created
- ✅ Layered rot model documented
- 🔄 sync_expiry.py needs writing
- 🔄 Monthly maintain-os workflow needs cron setup
- 🔄 Weekly light scan needs cron setup
- 🔄 Telegram interview bot needs implementation