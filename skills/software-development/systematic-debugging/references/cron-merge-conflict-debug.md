# Debugging Session: cron/scheduler.py Git Merge Conflict

## Symptom
- Auto-wake reported "427 error mentions in 24h"
- `hermes cron list` crashed with SyntaxError
- Gateway failed to start with `cron/scheduler.py line 1 <<<<<<< Updated upstream`

## Root Cause Chain
1. `gateway run` → imports `cron.scheduler` → SyntaxError on line 1
2. Line 1 was `<<<<<<< Updated upstream` — leftover from failed `git stash pop`
3. File had 3 conflict markers: `<<<<<<<` (L1), `=======` (L2309), `>>>>>>> Stashed changes` (L4578)
4. git status showed `UU cron/scheduler.py` (unmerged, both modified)
5. File was 196KB (upstream + stashed copy concatenated)

## Fix
- Extracted upstream version (L2–L2308) and concatenated with everything after `>>>>>>>` marker
- Kept upstream (HEAD) — stash was old WIP with only timeout 120→300s change
- `git add cron/scheduler.py` resolved the UU status
- File shrunk from 196KB → 99KB (removed duplicate)

## Key Insight
The error spike was entirely caused by one stale conflict marker. 498 errors/24h in proactive_executor were all downstream of this single root cause. Always check git status when unexpected import errors appear.

## Commands Used
```bash
# Discovery
ps aux | grep -i hermes
ls -la logs/
grep -c "error" logs/*.log    # count errors per log

# Conflict analysis
cd hermes-agent
git status --short            # showed UU cron/scheduler.py
git stash list                # stash@{0}: WIP on main: 72154ad87
head -1 cron/scheduler.py     # showed <<<<<<<

# Resolution
# Remove conflict markers programmatically, keep upstream version
git add cron/scheduler.py
```

## Related
- self-evolution plugin had `api_base: https://openclaude.gitlawb.com/v1` (dead gateway) instead of `https://opencode.ai/zen/v1` — always check `.env` and config before saying something is missing.
