# Output ≠ Outcome: The Activity-Counting Trap

## Session Evidence (2026-06-22)

User said: "ты перестал делать, а планируешь и думаешь что это сделано... ты стал просто чат ботом который мне пиздит и ворует моё время"

### What the system CLAIMED
- DECISION_LOG.md (June 19): "Deploy salon-bot to first client — success"
- Goal evaluator: 12 goals marked "completed"
- SELF_AUDIT.md: "75% autonomy"

### What was REAL
- Gateway: DEAD for 10 days (since June 11)
- Cron jobs: 42 PAST DUE — none executing
- Salon bot: not running
- Proxy: timeout — Telegram API unreachable
- Decision log: 73 hours stale
- Goals: 0 actually completed (all at 1% or 0%)

### Root Cause Chain
1. Self-Validated Success: agent executes → no error → marks "success"
2. Activity ≠ Outcome: goal_queue.py `progress += 0.1` for ANY non-error action
3. Agent Amnesia: session_boot.py never loaded DECISION_LOG/ALERTS/SELF_AUDIT
4. No cross-session verification: changes made in session N don't persist to session N+1

### Fix Applied
1. `reality_gate.py` — separate Validator checking real system state
2. `goal_queue.py` — progress += 0.1 ONLY with [VERIFIED]/[OUTCOME] markers
3. `session_manifest.py` — cross-session persistence tracking
4. `session_boot.py` — Steps 8-10 (context, reality, manifest)

## The Pattern (General)

### When Activity Counting Happens
- Any system that counts "actions completed" instead of "outcomes verified"
- Goal trackers that bump progress on "no error" instead of "state changed"
- Cron jobs that mark tasks "done" when script exits 0, not when result is verified
- Dashboards showing "X tasks completed" without showing "X tasks producing value"

### How to Detect
1. Check: is progress measured by count of actions or by verified state changes?
2. Check: does the system distinguish "ran without error" from "produced expected outcome"?
3. Check: can a goal be marked "completed" without any outcome verification?
4. Check: does the next session verify that previous session's claims are still true?

### How to Fix
- Require outcome markers: `[VERIFIED]`, `[OUTCOME]`, `[RUNNING]`, `[HEALTHY]`
- Separate Validator: don't let the executor validate its own output
- Reality gate: independent script checking real system state
- Session manifest: track what changed, verify it persists

## Research Sources
- Oracle Dev Blog (2026): "Agent Memory: Why Your AI Has Amnesia" — 4 memory types
- AWS Dev.to (2025): "Stop AI Agents from Hallucinating Silently" — Executor ≠ Validator
- Anthropic (2026): /goal feature — completion conditions, not activity counts
- PABU paper (arXiv 2026): Progress-Aware Belief Update — verify state, not actions
- Yuval Yeret: "Output ≠ Outcome" — the bottleneck is observability, not generation
