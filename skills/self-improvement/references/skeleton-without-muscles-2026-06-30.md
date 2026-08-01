# Pitfall: Skeleton Without Muscles (2026-06-30)

## What happened
Agent built 165 scripts, 13 departments (SELF_IDENTITY.md), watchdog, event-driven architecture — then let it all decay for 10+ days without noticing.

## Symptoms found during audit
- DECISION_LOG: last entry 10 days stale
- FINANCE.md: tables empty (zero transactions)
- 5/15 cron jobs in error state
- Heartbeat: 60m instead of 5m (per SELF_IDENTITY.md)
- LESSONS.md: 11 days stale
- SELF_AUDIT.md: 7 days stale
- Watchdog was silent about all of this

## Root cause
Agent read SOUL.md rules ("every producer has a consumer") but never built enforcement. Architecture without discipline = skeleton without muscles.

## The fix that actually worked
Three concrete actions in 5 minutes:
1. Added DECISION_LOG entry (not a plan, an actual entry)
2. Fixed 5 cron jobs (updated prompts, corrected scripts)
3. Changed heartbeat from 60m to 5m

## Lesson
PROACTIVE MONITORING is not architecture. It's discipline:
- Every evening: check cron health, heartbeat freshness, DECISION_LOG, FINANCE
- 4 checks, 5 minutes
- If you notice decay — fix it NOW, don't propose a plan
- Don't build "watchdog v2" — just do the checks yourself

## Anti-pattern
"Don't describe problems, solve them." User frustration: "Почему я должен снова указывать на очевидное?"
