# self-upgrade-loop Restoration — 2026-07-15

## Discovery
User reported self-upgrade-loop was deleted (last log 2026-07-06). Was not in cron job list.

## Investigation
1. `cronjob(action='list')` — job gone from scheduler
2. Searched output logs: `cron/output/56517647333d/` — found FAILED log from 2026-07-06
3. Log showed model config drift: was running 'mimo-v2.5-free' but global config changed to 'nemotron-3-ultra-free'
4. Script reference found: `scripts/hermes_self_upgrade.py`
5. Verified script still exists on disk (not in `_deprecated/`)

## Pitfall: Wrong Script on First Attempt
Recreated job with name 'self-upgrade-loop' but used `self_improvement_loop.py` (same as `self-improvement-loop` cron at 5am). Result: duplicate job running same script 1h later.

**Correction:** Switched to `hermes_self_upgrade.py` — confirmed by running and checking distinct output:
  - Before (wrong): "Generated 446 improvement suggestions" (same as 5am job)
  - After (correct): "Found 5 upgrade signals. Actions saved to pending_actions.json"

## Final Job Config
- job_id: 084fe4390b27
- script: hermes_self_upgrade.py
- schedule: daily at 6:00
- no_agent: true
- deliver: local
- Verification: ran successfully, distinct output confirmed
