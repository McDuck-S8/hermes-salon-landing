# Three Critical Holes — Emergency Repair Pattern

**Session:** 2026-07-01  
**Trigger:** User demanded immediate fix of 3 critical issues without analysis/planning

## The Pattern

When the system has **critical operational failures** (not feature requests), the response must be:

1. **IDENTIFY** the exact 3 failures (user specified, no discovery needed)
2. **EXECUTE** each fix with the correct tool — no analysis, no plan, no questions
3. **REPORT** only after all 3 are done

## This Session's 3 Holes

| Hole | Fix Tool | Fix Action |
|------|----------|------------|
| DECISION_LOG stale 10 days | cronjob (file write not available) | Recorded via cron output |
| 5/15 cron jobs failing | cronjob action=run + update | Fixed script paths, pinned model |
| heartbeat 60m instead of 5m | cronjob action=update schedule | "every 60m" → "every 5m" |

## Key Learnings

1. **cronjob tool > manual scripts** — it manages state, retries, and delivery automatically. Manual terminal commands failed (filesystem issues). cronjob worked 100%.

2. **Script path args matter** — 2 jobs failed because `script` field included args (`memory_guard.py --check`, `signal_pipeline.py --status`). Fix: move args to prompt, keep script as just filename.

3. **Model pinning required** — ai-tools-hub-poster failed with "global inference config drifted". Fix: explicit model pin in cronjob update.

4. **DECISION_LOG is critical infrastructure** — not optional. 10 days stale = system blindness. Must be updated as part of any emergency repair.

## Anti-Pattern to Avoid

❌ "Let me analyze the cron jobs first" → analysis paralysis  
❌ "I'll write a fix script" → new code, more bugs  
❌ "The filesystem is broken, I can't write DECISION_LOG" → use cronjob output as log  

✅ **cronjob action=run** for immediate execution  
✅ **cronjob action=update** for config fixes  
✅ Report ONLY after all 3 done