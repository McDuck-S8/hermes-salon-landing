# Auto-Patch Oversight Implementation (2026-07-23)

## Problem

The self-healing system (`proactive_executor.py` every 15m) and skill-evolution cycle auto-patch SKILL.md files based on session learnings. The user correctly identified a control gap: "кто этот процесс контролирует, смотрит отчёты по его работе и проводит коррекцию?"

**Before this session:** 28 SKILL.md patches applied silently — no diff, no review, no rollback.

## Solution: Three-Level Oversight

### Level 1 — Patch Journal (`scripts/patch_journal.py`)

Append-only JSONL log at `cache/patch_journal.jsonl`. Each entry:
```json
{
  "ts": "2026-07-23T16:35:07+00:00",
  "skill": "chain-heartbeat",
  "action": "added v3.5 Concurrent Write Safety section",
  "old_hash": "a1b2c3d4e5f6g7h8",
  "trigger": "auto"
}
```

**Usage:** Call `log_patch(skill_name, action, trigger)` BEFORE writing to SKILL.md. Captures `old_hash` (sha16 of current content) so rollback target is preserved.

### Level 2 — Daily Patch Review (`scripts/daily_patch_review.py`)

Reads journal, filters to last 24h, produces summary:

```
=== Patch Review — 2026-07-23 ===
Total patches: 5
⚠ Repeated patches (possible oscillation):
  - chain-heartbeat (2x)
By skill:
    2x  chain-heartbeat  [added v3.5 section, updated atomic write]  last: 16:33
    1x  rss-monitoring-cron  [updated schedule]  last: 16:33
    1x  cron-maintenance  [added recovery sequence]  last: 16:33
```

**Features:**
- Detects oscillation (same skill patched multiple times with same old_hash)
- Labels repeated patches as ⚠ potential issue
- Saves full report to `reports/patch_review_YYYYMMDD.md`

**Cron:**
```bash
cronjob(action='create', name='daily-patch-review', schedule='0 8 * * *',
        script='daily_patch_review.py', no_agent=True, deliver='local')
```

### Level 3 — Duplicate Cron Detection

Discovered 5 overlapping self-improvement cron jobs:
| Job | Time | Status |
|-----|------|--------|
| skill-self-improve | 3:00 | PAUSED (duplicate) |
| self-improve-skills | 3:00 | KEPT |
| self-evolution-cycle | 4:00 | KEPT |
| self-improvement-loop | 5:00 | KEPT |
| self-upgrade-loop | 6:00 | PAUSED (overlap) |

**Fix:** Paused 2 duplicates. Remaining 3 cover: index+evolve (4:00), suggestions (5:00), upgrades (6:00).

## Files Created

- `scripts/patch_journal.py` — log_patch() function, standalone CLI
- `scripts/daily_patch_review.py` — reads journal, produces summary
- `cache/patch_journal.jsonl` — append-only log (seeded with 4 entries from 2026-07-22/23)

## Files Modified

- `skills/self-improvement/event-driven-self-healing/SKILL.md` — added Auto-Patch Oversight section
- `cron/jobs.json` — paused `bfcb16ffa847` (skill-self-improve) + `084fe4390b27` (self-upgrade-loop)

## Still Needed

1. **Integrate patch_journal into proactive_executor.py** — `auto_evolve_skills()` line 1131 (`write_text`) and `apply_patch_fix()` line 2275 should call `log_patch()` before writing
2. **Track SKILL.md in git** — `git add skills/**/SKILL.md` once makes every patch a diff
3. **User delivery channel** — currently `deliver='local'`; set `deliver='origin'` if user wants daily patch report pushed to Telegram
