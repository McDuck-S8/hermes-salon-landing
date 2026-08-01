# Analysis → Rewrite Trap (2026-06-14)

## Signal

The user says "ты от работающей и дающей надежды на результат.... накодил так что нужно всё переписывать?" followed by repeated "далее продолжай" (keep going, stop analyzing).

## Pattern

Agent identifies real problems in existing code, then starts planning a comprehensive rewrite/redesign instead of fixing what's already running. Symptoms:

- Writing multi-phase plans with options A/B/C
- Analyzing root causes without touching code
- Presenting "what's wrong" without "what I just fixed"
- Using "skipped, no auto-run possible" as a stop condition instead of fixing the blocker

## Why It Fails

The working system PROMISES value ("дающая надежды на результат"). The user sees plans, not progress. Analysis paralysis produces documents, not working improvements.

## Root Cause

Agent treats "understand the problem" and "fix the problem" as separate phases. But the user treats them as one motion — understand THROUGH building, not before building.

## Rule

When the system works but has gaps:

1. **RUN existing code first** — see what actually breaks, not what you theorize breaks
2. **Fix the smallest thing** that unblocks the pipeline (a missing arg, a wrong path, a stale file)
3. **Run again** — see what breaks next
4. **Repeat**
5. **NEVER present a multi-phase plan** unless explicitly asked for one
6. **"далее продолжай"** means KEEP BUILDING, not KEEP ANALYZING
7. **A fix that doesn't execute** (blocked by safe_patterns, missing --domain flag, path duplication) is not analyzed — it's FIXED

## Example

Session 2026-06-14: Knowledge Application Engine had gaps:
- llm_analyst generated unified diffs with "entry1, entry2" — **fixed prompt**
- knowledge_gap_filler.py had no --domain arg — **added argparse**
- safe_patterns didn't include gap scripts — **added 5 patterns**
- cron scripts path duplicated as scripts/scripts/ — **removed prefix**
- llm-analyst cron was stuck in the past — **reset next_run_at**

Every fix was under 20 lines. Zero architectural redesigns. KC grew from 3295 → 3320.
