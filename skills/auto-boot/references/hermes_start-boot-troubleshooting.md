# hermes_start.py Boot Troubleshooting Guide

**Version:** 2026-06-29
**Source:** Live session boot verification

---

## Boot Command
```bash
python D:/Portable_Soft/hermes/hermes_start.py
```

## Expected Output (Success)

```
=== HERMES BOOT ===
[2026-06-29 12:05:12] ==================================================
[2026-06-29 12:05:12] SESSION BOOT STARTING
[2026-06-29 12:05:12] ==================================================
[2026-06-29 12:05:12] Step 0: BOOT_SEQUENCE loaded (5427 chars)
[2026-06-29 12:05:12] Step 0.5: Checking MEMORY.md health...
[2026-06-29 12:05:12]   MEMORY.md critical (8 lines) — fixing...
[2026-06-29 12:05:12] Restored from backup: 17 lines
[2026-06-29 12:05:12]   MEMORY.md OK: 14 lines, 772 bytes
[2026-06-29 12:05:12] Step 0.6: AUTO-REPAIR — scanning degraded departments...
[2026-06-29 12:05:12]   All departments operational ✓
[2026-06-29 12:05:12] Step 1: Checking pending session dumps...
[2026-06-29 12:05:12]   Ingested 2 new dumps (61 already done)
[2026-06-29 12:05:12] Step 2: Checking conversation content...
[2026-06-29 12:05:13]   Extracted 28 knowledge entries from 2 conversations
[2026-06-29 12:05:13] Step 3: Classifying unclassified KC entries...
[2026-06-29 12:05:13]   All entries classified
[2026-06-29 12:05:13] Step 4: Evaluating goals...
[2026-06-29 12:05:19]   Active goals: 3
[2026-06-29 12:05:19]   Created 2 new goals
[2026-06-29 12:05:19]     [corrective-wf-daily-maintenance-1] P10 10% Fix: Daily Maintenance step 1 (check_cron_health)
[2026-06-29 12:05:19]     [g-004] P8 5% Reduce cron error rate (3/12 jobs failing)
[2026-06-29 12:05:19]     [g-003] P3 0% Generate daily value for user
[2026-06-29 12:05:19] Step 5: Syncing memory graph...
[2026-06-29 12:05:19] Synced 100 experiences to graph
[2026-06-29 12:05:19] Graph: 907 entities, 986 relations
[2026-06-29 12:05:19] Step 6: Building session context...
[2026-06-29 12:05:20]   Context loaded (1523 chars)
[2026-06-29 12:05:20] Step 6a: Loading tool catalog...
[2026-06-29 12:05:20]   Tool catalog loaded (19234 chars)
[2026-06-29 12:05:20] Step 6b: Scanning user needs...
[2026-06-29 12:05:23]   User needs: 20
[2026-06-29 12:05:23] Step 6c: Checking knowledge graph...
[2026-06-29 12:05:23]   Graph: 2002 nodes, 5296 edges
[2026-06-29 12:05:23] Step 7: Checking error backlog...
[2026-06-29 12:05:23]   7 recent errors in log
[2026-06-29 12:05:23] Step 8: Loading human-written context files...
[2026-06-29 12:05:23]   Loaded DECISION_LOG.md (2000 chars)
[2026-06-29 12:05:23]   Loaded ALERTS.md (1635 chars)
[2026-06-29 12:05:23]   Loaded SELF_AUDIT.md (1815 chars)
[2026-06-29 12:05:23]   Loaded agent_policies.md (2000 chars)
[2026-06-29 12:05:23] Step 9: Running Reality Gate...
[2026-06-29 12:05:29]   VERDICT: ALL_GREEN
[2026-06-29 12:05:29] Step 10: Verifying session manifest...
[2026-06-29 12:05:29]   Manifest verification error: [Errno 2] No such file or directory: 'D:\\\\Portable_Soft\\\\hermes\\\\scripts\\\\session_manifest.py'
[2026-06-29 12:05:29] ==================================================
[2026-06-29 12:05:29] SESSION BOOT COMPLETE
[2026-06-29 12:05:29]   Dumps ingested: 2
[2026-06-29 12:05:29]   Conversations: 28 entries
[2026-06-29 12:05:29]   Active goals: 3
[2026-06-29 12:05:29]   User needs: 20 (0 unmet)
[2026-06-29 12:05:29]   Context: 1523 chars
[2026-06-29 12:05:29] ==================================================
Emitted: boot_completed
  Triggers: 2 jobs
    → proactive-doer
    → self-assessment
[2026-06-29 12:05:29]   🧠 Classifier: action_completed [low] conf=1.0
[2026-06-29 12:05:29]   🔗 Chain: verify_outcome_not_just_output → record_to_manifest → update_goal_progress
[2026-06-29 12:05:29]   ⚡ Chain: 0/0 steps succeeded
[2026-06-29 12:05:29] Step 13: AUTONOMOUS FIRST ACTION...
[2026-06-29 12:05:29]   Step 13: Target: [corrective-wf-daily-maintenance-1] P10 Fix: Daily Maintenance step 1 (check_cron_health)
[2026-06-29 12:05:29]   Step 13: AUTONOMOUS BOOT COMPLETE. Real action taken: cron_complex_schedule — Cannot auto-fix: {'kind': 'interval', 'minutes': 360, 'display': 'every 360m'}
[2026-06-29 12:05:29] Step 14: Starting signal daemon...
[2026-06-29 12:05:29]   Signal daemon started
[12:05:29] EXECUTING: corrective-wf-daily-maintenance-1 — Fix: Daily Maintenance step 1 (check_cron_health)
[12:05:29]   ⏳ done_when: 2/2 not met:
[12:05:29]     → Step 1 executes successfully (Cannot auto-check: Step 1 executes successfully)
[12:05:29]     → Workflow completes without errors (Cannot auto-check: Workflow completes without errors)
[12:05:29]   ⚠️ No action_command, no derived action, criteria not met
  session_boot: OK (4 dumps, 5 errors)
  session_context: FAILED — 'str' object has no attribute 'keys'
  goals: 3 active
  tool_catalog: EXISTS
  autonomous_action: EXECUTED goal corrective-wf-daily-maintenance-1 — NO_ACTION
=== BOOT DONE ===
```

---

## Known Failures & Fixes

### 1. MEMORY.md Critical (Step 0.5) — AUTO-FIXED
- **Symptom:** `MEMORY.md critical (8 lines) — fixing...`
- **Fix:** Auto-restored from backup (17 lines)
- **Note:** This is Step 0.5 — NEVER SKIP. Memory guard runs here.

### 2. session_manifest.py Missing (Step 10) — NON-BLOCKING
- **Symptom:** `Manifest verification error: No such file or directory: 'scripts/session_manifest.py'`
- **Fix:** Create `scripts/session_manifest.py` or remove check from boot
- **Impact:** Boot completes, step 10 fails but continues

### 3. Reality Gate False Positive (Step 9)
- **Symptom:** `VERDICT: ALL_GREEN` despite 3 failing cron jobs
- **Root cause:** Checks file mtime, not DB integrity or cron health
- **Fix:** Update `scripts/reality_gate.py` with real checks (see procedural-logic reference)

### 4. Cube Feeder DB Schema (Cron Job — Not in Boot)
- **Job:** `cube-feeder` (daily 04:15)
- **Error:** `sqlite3.IntegrityError: NOT NULL constraint failed: experiences.content`
- **Fix:** Add `content=text` parameter in `cube_feeder.py` → `kc.add_experience()`

### 5. Rate Limits on Free APIs (Cron Jobs — Not in Boot)
- **Jobs:** `telegram-monitor` (every 6h), `self-upgrade-loop` (every 12h)
- **Error:** `HTTP 429: Rate limit exceeded`
- **Fix:** Add exponential backoff + provider rotation (see procedural-logic reference)

---

## Emergency Manual Boot (If hermes_start.py Hangs)

```bash
# Run steps individually
python -c "
import sys
sys.path.insert(0, 'D:/Portable_Soft/hermes')
from scripts.session_boot import run_boot_step
run_boot_step(0)   # BOOT_SEQUENCE
run_boot_step(0.5) # MEMORY.md health
run_boot_step(1)   # Session dumps
run_boot_step(2)   # Conversation content
run_boot_step(3)   # Classify KC
run_boot_step(4)   # Evaluate goals
run_boot_step(5)   # Sync graph
run_boot_step(6)   # Build context
run_boot_step(7)   # Error backlog
run_boot_step(8)   # Context files
run_boot_step(9)   # Reality gate
run_boot_step(11)  # Autonomous action
run_boot_step(12)  # Signal daemon
"
```

---

## Verification Checklist (Post-Boot)

- [ ] `=== BOOT DONE ===` printed
- [ ] `Emitted: boot_completed` event logged
- [ ] 2 cron jobs triggered: `proactive-doer`, `self-assessment`
- [ ] MEMORY.md > 10 lines (check: `wc -l D:/Portable_Soft/hermes/MEMORY.md`)
- [ ] `cache/session_context.json` exists and valid JSON
- [ ] `cache/goal_queue.json` has 3+ active goals
- [ ] Signal daemon process running (check `ps aux | grep signal_daemon`)

---

## Common Issues & Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| Boot hangs >30s | Ctrl+C → run steps individually (see Emergency Manual Boot) |
| MEMORY.md not restored | `cp D:/Portable_Soft/hermes/MEMORY.md.bak D:/Portable_Soft/hermes/MEMORY.md` |
| Proxy errors in boot | Ensure v2rayN running on 10806/10809, or set `export NO_PROXY=localhost` |
| "str object has no attribute keys" | Non-fatal — session_context warning, boot continues |
| Reality gate ALL_GREEN but cron failing | Expected false positive — fix reality_gate.py |
| Autonomous action "NO_ACTION" | Goal criteria not auto-checkable — manual execution needed |