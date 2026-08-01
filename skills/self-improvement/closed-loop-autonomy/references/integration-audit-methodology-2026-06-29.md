# Integration Audit Methodology

**Source:** Session 2026-06-29 — systematic audit after "build-restart-rebuild" cycle.
**Trigger:** User said "блять вчера строили строили построили ... рестарт и не работает."

## The Problem

Event-driven agent systems have a unique failure mode: all modules exist, all code is
correct in isolation, but the CONNECTIONS between them are broken. The system looks
healthy when you check each component, but nothing actually flows through the pipeline.

## Module Connection Map (Hermes-specific)

```
signal_scanner.py
  └── EMITS → event_bus.json (via event_bus.emit("new_external_signal"))

event_bus.json
  └── PENDING → event_bus.py process (called by cron or heartbeat)
  └── DIRECT_EVENT_HANDLERS["new_external_signal"] → _run_rd_dev_processors()
      └── subprocess.run(rd_processor.py)
      └── subprocess.run(dev_processor.py)

rd_processor.py
  └── READS → ARBITRAGE_WORKSHOP.md (checks for UNVERIFIED bricks)
  └── WRITES → ARBITRAGE_WORKSHOP.md (adds bricks)
  └── Does NOT write to knowledge_cube ❌

dev_processor.py
  └── READS → ARBITRAGE_WORKSHOP.md (compares with SELF_IDENTITY.md)
  └── WRITES → goal_queue.json (creates goals)
  └── Does NOT write to knowledge_cube ❌

goal_executor.py
  └── READS → goal_queue.json (gets active goals)
  └── WRITES → goal_queue.json (updates status)
  └── WRITES → feedback_store.json (records outcome)
  └── Does NOT write to knowledge_cube ❌

bayesian_scorer.py
  └── READS → cache/scorer_history.json (priors)
  └── READS → knowledge_cube.db (success rates)
  └── WRITES → cache/scorer_history.json (updates)

cube_feeder.py
  └── READS → cache/event_bus.json (processed events)
  └── WRITES → knowledge_cube.db (adds entries)
  └── Called by cron (cube-feeder, 15 4 * * *)

signal_daemon.py
  └── CALLS → signal_scanner.scan_once()
  └── EMITS → event_bus.json
  └── Runs as background process (PID file)
  └── NO supervisor — if dead, stays dead ❌
```

## Bugs Found (2026-06-29)

### Bug 1: event-heartbeat runs wrong script
- **Cron job:** event-heartbeat (every 2m)
- **Script:** hermes_heartbeat.py
- **What hermes_heartbeat.py does:** checks network, gateway, disk — health check
- **What it should do:** call event_bus.py process to drain pending events
- **Impact:** 11 events stuck in pending forever. Signal pipeline completely broken.
- **Fix:** Change script= to event_bus.py or add event_bus.py process call inside hermes_heartbeat.py

### Bug 2: event_bus.process() hangs
- **Root cause:** imports session_recall which indexes 5000+ messages on import
- **Timeout:** >30s for indexing, process() never completes
- **Impact:** Even if the right cron job calls process, it times out
- **Fix:** Lazy import session_recall inside try/except, skip enrichment on timeout

### Bug 3: signal_daemon dead, no restart
- **Root cause:** background process, no supervisor, no watchdog
- **State:** PID file stale, 35 consecutive empty scans, backoff 600s
- **Impact:** No new signals detected. System blind.
- **Fix:** procedural_executor should check daemon liveness and restart

### Bug 4: goal_executor marks NO_ACTION as failed
- **Root cause:** execute_goal() returns NO_ACTION → save_goals sets status='failed'
- **Impact:** 0 active, 0 completed, all failed after any executor run
- **Fix:** status='skipped' for NO_ACTION, not 'failed'

### Bug 5: feedback_store format mismatch
- **Old format:** numeric outcomes (1.0, -0.5) from procedural executor
- **New format:** string outcomes ("completed", "derived_failed") from goal_executor
- **Impact:** score_signal() can't load history correctly
- **Fix:** normalize all outcomes to numeric on write

### Bug 6: rd_processor and dev_processor don't write to KC
- **Impact:** Knowledge Cube doesn't grow from signal processing
- **Fix:** Add KC write in processors, or add cube_feeder call after processing

## Audit Template

```python
# Quick integration audit — run at session start after restart
def audit_integrations():
    issues = []
    
    # 1. Check cron scripts exist and match purpose
    jobs = json.loads(Path("cron/jobs.json").read_text()).get("jobs", [])
    for j in jobs:
        script = j.get("script", "")
        if script and not (Path("scripts") / script).exists():
            issues.append(f"CRON '{j['name']}' → {script} NOT FOUND")
    
    # 2. Check event bus stuck
    eb = json.loads(Path("cache/event_bus.json").read_text())
    pending = len(eb.get("pending", []))
    if pending > 5:
        issues.append(f"EVENT BUS: {pending} events stuck")
    
    # 3. Check goal queue health
    gq = json.loads(Path("cache/goal_queue.json").read_text())
    statuses = {}
    for g in gq.get("goals", []):
        s = g.get("status", "?")
        statuses[s] = statuses.get(s, 0) + 1
    if statuses.get("active", 0) == 0 and statuses.get("failed", 0) > 0:
        issues.append(f"GOALS: all failed/empty, queue dead")
    
    # 4. Check feedback format
    fb = json.loads(Path("cache/feedback_store.json").read_text())
    formats = set(type(e.get("outcome")).__name__ for e in fb.get("entries", []))
    if formats - {"int", "float"}:
        issues.append(f"FEEDBACK: mixed formats {formats}")
    
    # 5. Check daemon liveness
    for daemon in ["signal_daemon"]:
        r = subprocess.run(["pgrep", "-f", daemon], capture_output=True, text=True)
        if not r.stdout.strip():
            issues.append(f"DAEMON: {daemon} DEAD")
    
    return issues
```

## Lessons

1. **Never trust cron job names** — always verify the actual script matches the job purpose
2. **Always check event_bus pending** — >5 pending for >5 min = processing broken
3. **Never mark NO_ACTION as failed** — use 'skipped' for goals without commands
4. **Supervise daemon processes** — background processes need watchdog restart
5. **Normalize feedback formats** — all outcomes should be numeric for scorer history
6. **Lazy imports for slow modules** — session_recall indexing blocks event processing
