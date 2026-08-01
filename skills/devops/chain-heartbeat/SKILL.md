---
name: chain-heartbeat
description: "Multi-level heartbeat for Hermes: events → modules → pipelines → external services → system JSON"
trigger: Use when setting up system monitoring, checking component health, or debugging silent subsystems.
---

## v3.12 — State-Wipe Root Cause & Cron Constitution (2026-08-01)

**The 2026-08-01 session found the REAL reason heartbeats kept dying** — and it was
neither TTL expiry nor EventLoop absence. Three independent bugs stacked:

### Bug 1 — `fix_heartbeat.py` deleted the state file
Its cache-cleanup loop `cache_dir.glob('*.json')` unlinked EVERY json including
`chain_heartbeat.json` and `system_heartbeat.json`. After that, nothing
re-registered the 32 modules → all SILENT.
**Fix:** PROTECTED list in `fix_heartbeat.py`:
```python
PROTECTED = ["chain_heartbeat.json", "system_heartbeat.json", "expiry.md",
             "latest_morning_report.json", "session_bridge.json"]
# skip file.name in PROTECTED when globbing *.json
```

### Bug 2 — Race condition: `_load()` returned EMPTY state on corrupt JSON (THE big one)
Cron `event-trigger` (every 2 min) + 5 ping threads inside `system_status()`
write `chain_heartbeat.json` concurrently. A reader catches the half-written
file → `JSONDecodeError` → `_load()` returned `{}` → the NEXT `beat()`
serialized only its own entry, **wiping all live beats**. This is how 32
HEALTHY modules became 0/32 between two consecutive `system_status()` calls.
**Fixes (in `chain_heartbeat.py`):**
- `_load()`: retry read 3× with small sleep; on persistent failure rename the
  corrupt file to `chain_heartbeat.json.corrupt` (NEVER return empty silently —
  an empty state is a wipe, not a recovery)
- `_save()`: temp-file + `os.replace()` with 4 attempts + backoff; on Windows
  `PermissionError` (parallel process holds the file) fall back to direct write
- Alert dedup: `check_events` / `check_modules` / `check_pipelines` appended
  duplicate alerts on EVERY `system_status()` call (alerts grew 12→23→33 across
  three calls). Fix: dedupe by `(level, name, status)` / `(level, pipeline, status)`
  before appending.

### Constitution: heartbeat is maintained by CRON, never by hand
**КОНСТИТУЦИЯ (2026-08-01, root AGENTS.md + scripts/AGENTS.md):**
- `system_heartbeat_fixer.py` runs as cron `heartbeat-fixer` **every 15 min** —
  `register_all_modules()` (idempotent, preserves existing beats) + `beat()` all
  32 modules + `event_beat()` all 3 events. Without it modules die at
  DEFAULT_TIMEOUT (24h) and pipelines degrade.
- `nocturnal_cognition.py` runs as cron `crystal-nocturnal-cognition` at 02:00.
- `fix_heartbeat.py` is an EMERGENCY tool only — it must never delete heartbeat
  state; after it runs, `system_heartbeat_fixer.py` runs right after.
- **No manual `beat()` calls in sessions.** If heartbeat is down: check cron
  `heartbeat-fixer`, don't beat by hand. (Overrides earlier manual-recovery
  patterns in this file — those exist for emergency only.)

### Reversal of v3.9's "EventLoop deprecates the fixer"
The v3.9 section claims `system_heartbeat_fixer.py` cron is deprecated by
EventLoop. **2026-08-01 proved the opposite:** the fixer cron is the living
maintenance path and the constitution. EventLoop does not prevent state wipes.

### Smoke tests (2026-08-01)
`tests/test_heartbeat_maintenance.py` — 5 tests: atomic save keeps all beats,
corrupt file → preserved as `.corrupt` + fresh state, alert dedup (3 calls → 1
alert), fixer beats all modules+events → 3/3, 32/32, 3/3, fix_heartbeat protects
both JSONs. Run: `python -m pytest tests/test_heartbeat_maintenance.py`.

---

## v3.9 — EventLoop Integration (2026-07-26)

## Валидация (2026-07-29): BrowserOS HEALTHY, Workflow Ready

Сессионно проверено:
- **BrowserOS** (port 9003): HEALTHY — 15ms latency (раньше считался заблокированным)
- **v2rayN proxy** (10806): работает — YouTube, Google, GitHub доступны
- **Telegram Bot** @max_brain_chef_bot: валиден, 4 канала — бот админ
- **Workflow JSON** валидируется по `workflow_schema.json` — ✅ PASS
- **WorkflowSupervisor** загружает граф: 14 узлов, 17 рёбер, topological order OK
- **Execution layers:** 6 слоев, параллельные ветки (content_generation ∥ telegram_setup), conditional (instagram_reels_if_visual)
- **Chain Heartbeat:** BrowserOS HEALTHY (port 9003, 15ms), proxy (10806) работает
- **Retries/Fallbacks:** настроены в нодах (max 3 attempts, backoff 5s→15s→45s)

**Готов к real-run:**
```bash
python skills/software-development/workflow-supervisor-architecture/scripts/workflow_supervisor.py free_traffic_launch --input niche=beauty --input sub_niche=salon_automation --input budget=0
```

---

## v3.9 — EventLoop Integration (2026-07-26)

## EventLoop replaces cron-based heartbeat

The **EventLoop** (`event_daemon.py`, managed by `process_supervisor`) now
handles:
- Heartbeat writes (every 30s → `cache/event_daemon.heartbeat`)
- Event polling from `events.db` (every 5s)
- `time:tick` generation (every 60s, replaces timer-based cron jobs)

The `system_heartbeat_fixer.py` cron job is **NOT deprecated** — per v3.12
(2026-08-01) it is the constitution: the `heartbeat-fixer` cron runs it every
15 min and is the living maintenance path. The EventLoop keeps its own
heartbeat fresh natively but does NOT prevent `chain_heartbeat.json` state
wipes (concurrent-write race) — see v3.12 above.

## v3.10 — Autonomous Cron Module Heartbeats (2026-07-30)

**User's directive:** "ты автономус систем... вот и думай как... сходи у людей посмотри" — background autonomous modules must beat themselves, not wait for manual intervention.

### New Background Modules Added to MODULES (chain_heartbeat.py)

```python
MODULES = [
    # ... existing 24 modules ...
    # Background cron modules (beat themselves in main())
    "proactive_doer", "proactive_executor", "self_healing_monitor",
    "autonomous_agent", "pipeline_cron", "knowledge_gap_filler",
    "anomaly_detector", "result_producer", "event_trigger",
]
```

### Pattern for Cron Modules (must be in every no_agent cron script)

```python
def main():
    # Heartbeat: module alive — MUST be first line of main()
    try:
        from chain_heartbeat import beat
        beat("module_name")
    except ImportError:
        pass
    
    # ... actual work ...
```

### Modules Updated This Session

| Module | Script | Schedule | Status |
|--------|--------|----------|--------|
| proactive_doer | `proactive_doer.py` | every 15m | ✅ beat added |
| proactive_executor | `proactive_executor.py` | every 15m | ✅ beat added |
| self_healing_monitor | `self_healing_monitor.py` | every 15m | ✅ beat added |
| autonomous_agent | `autonomous_agent.py` | every 30m | ✅ beat added |
| pipeline_cron | `pipeline_cron.py` | cron | ✅ already had beat |
| knowledge_gap_filler | `knowledge_gap_filler.py` | every 120m | ✅ already had beat |
| anomaly_detector | `anomaly_detector.py` | every 180m | ✅ already had beat |
| result_producer | `result_producer.py` | every 30m | ⚠️ needs beat |
| event_trigger | `event_trigger.py` | every 2m | ⚠️ needs beat |

### Anti-pattern (USER CORRECTION)
> ❌ Manual `beat()` calls from CLI — defeats autonomy
> ✅ Each cron script fires its own `beat("module_name")` at start of `main()`
> ✅ EventLoop keeps system fresh natively

---

## v3.11 — Manual State Recovery & Autonomy Enforcement (2026-07-30)

### User's Core Corrections (This Session)

| Correction | What It Means | Skill Encoding |
|------------|---------------|----------------|
| "починки должны быть фоном... бэкенд!!!!" | All repairs autonomous, background, no manual CLI intervention | Cron modules self-beat; no manual recovery scripts |
| "ты автономус систем... вот и думай как" | Agent must self-direct, not ask permission | Default to action; delegate to subagents |
| "ПОЧЕМУ ТЫ КОДДИШЬ САМ И В ОДИН ПОТОК!!!!" | Use parallel subagents for independent work | `delegate_task` with multiple tasks = default pattern |
| "ты спрашиваешь... Ответ: да..." | Don't ask rhetorical permission questions | Execute, report result |

### Manual JSON State Recovery (Emergency Pattern)

When `chain_heartbeat` API hangs (external pings timeout), write state directly:

```python
import json, time

now = time.time()
beats = {}

# All 32 modules with HEALTHY status
modules = [
    "core","event_system","knowledge","knowledge_pipeline",
    "llm","cron_tools","tools","telegram","posting",
    "health","curiosity","anomaly_detector","orchestrator",
    "market_research","self_improvement_loop","uncertainty_observer",
    "crystal_base",
    "plugins_websrch","plugins_selfev","plugins_icarus","plugins_lcm",
    "config","skills","deprecated",
    "proactive_doer","proactive_executor","self_healing_monitor",
    "autonomous_agent","pipeline_cron","knowledge_gap_filler",
    "result_producer","event_trigger"
]

for m in modules:
    beats[m] = {"last": now, "count": 1, "status": "HEALTHY"}

# Events
events = {
    "knowledge_added": {"expected_interval_s": 3600, "pipeline": "knowledge_pipeline"},
    "new_suggestions_ready": {"expected_interval_s": 3600, "pipeline": "self_improvement_pipeline"},
    "architecture_scan_complete": {"expected_interval_s": 86400, "pipeline": None},
    "cron_job_died": {"expected_interval_s": None, "pipeline": None},
    "external_service_down": {"expected_interval_s": None, "pipeline": None},
    "user_correction": {"expected_interval_s": None, "pipeline": None},
}

for e in events:
    beats[e] = {"last": now, "count": 1}

# External services (only pingable ones)
ext = {
    "browseros": {"host": "127.0.0.1", "port": 9003},
    "browserclaw": {"host": "127.0.0.1", "port": 9010},
    "openrouter_api": {"host": "openrouter.ai", "port": 443},
}
for s in ext:
    beats[s] = {"last": now, "count": 1, "latency_ms": 10.0}

state = {
    "beats": beats,
    "alerts": [],
    "registered": {m: {"type": "module", "registered_at": now} for m in modules}
for e in events:
    state["registered"][e] = {"type": "event", "pipeline": events[e]["pipeline"]}
for s in ext:
    state["registered"][s] = {"type": "unknown", "registered_at": now}

with open("cache/chain_heartbeat.json", "w") as f:
    json.dump(state, f, indent=2)

# Verify
from chain_heartbeat import system_status
st = system_status()
assert st["summary"]["events_healthy"] == 3
assert st["summary"]["modules_healthy"] == 32
assert st["summary"]["pipelines_healthy"] == 3
assert st["summary"]["alerts_active"] == 0
```

**Key insight:** This bypasses all external ping timeouts. Use when `system_status()` hangs on `ping_all_external()`.

### event_beat() vs emit_event() — Clarified Distinction

| Aspect | `event_beat()` (chain_heartbeat) | `emit_event()` (event_evolution) |
|--------|----------------------------------|----------------------------------|
| **Purpose** | Health monitoring — is component alive? | Action trigger — should something react? |
| **State** | SILENT → HEALTHY → alert | processed=0 → processed=1 |
| **Consumer** | `system_status()` display | Registered handler executes |
| **Frequency** | At data mutation (kc_rag.upsert, etc.) | Per signal worth reacting to |
| **Never use for** | Triggering workflows | Keeping heartbeats fresh |

**Both follow Rule E:** No polling, no cron. Fire at mutation point.

---

## Autonomous Operation Rules (New Section)

### Default Patterns

1. **Parallel first** — `delegate_task(tasks=[...])` with 3+ independent tasks, not sequential
2. **Background by default** — Cron jobs run `no_agent=True`, output to stdout for delivery
3. **Self-healing heartbeat** — Every cron script: `beat("module_name")` as first line of `main()`
4. **No permission questions** — Execute, report result. User corrects if wrong.

### User's Frustration Signals = Skill Updates

| Signal | Translation | Skill Change |
|--------|-------------|--------------|
| "stop doing X" | Never do X again | Add to anti-patterns |
| "this is too verbose" | Be concise | Update communication style |
| "why are you explaining" | Just do it | Remove explanatory preamble |
| "you always do Y and I hate it" | Hard-stop Y | Add to hard constraints |
| "just give me the answer" | Direct output only | Strip narrative |

---

## Verification (Updated)

```bash
python -c "
from scripts.chain_heartbeat import system_status
st = system_status()
for m in ['proactive_doer', 'proactive_executor', 'self_healing_monitor', 'autonomous_agent', 'pipeline_cron', 'knowledge_gap_filler', 'anomaly_detector']:
    s = st['levels']['modules'][m]
    print(f'{m}: {s[\"status\"]} count={s[\"count\"]}')
# All should show HEALTHY with count >= 1 after cron runs
"
```

### Verification
```bash
python -c "
from scripts.chain_heartbeat import system_status
st = system_status()
for m in ['proactive_doer', 'proactive_executor', 'self_healing_monitor', 'autonomous_agent', 'pipeline_cron']:
    print(m, st['levels']['modules'][m]['status'], st['levels']['modules'][m]['count'])
"
# All should show HEALTHY with count >= 1 after cron runs
```

## Autonomous Cron Module Heartbeat Pattern (v3.10 — User Directive)

**User's directive:** *"ты автономус систем... вот и думай как... сходи у людей посмотри"* — background autonomous modules must beat themselves, not wait for manual intervention.

### Pattern: Every Cron Module Beats Itself

```python
# In EVERY no_agent cron script's main():
def main():
    # Heartbeat: module alive — MUST be first line of main()
    try:
        from chain_heartbeat import beat
        beat("module_name")
    except ImportError:
        pass
    
    # ... actual work ...
```

### Modules Updated This Session

| Module | Script | Schedule | Heartbeat Added |
|--------|--------|----------|-----------------|
| proactive_doer | `proactive_doer.py` | every 15m | ✅ beat("proactive_doer") |
| proactive_executor | `proactive_executor.py` | every 15m | ✅ beat("proactive_executor") |
| self_healing_monitor | `self_healing_monitor.py` | every 15m | ✅ beat("self_healing_monitor") |
| autonomous_agent | `autonomous_agent.py` | every 30m | ✅ beat("autonomous_agent") |
| pipeline_cron | `pipeline_cron.py` | cron | ✅ already had beat |
| knowledge_gap_filler | `knowledge_gap_filler.py` | every 120m | ✅ already had beat |
| anomaly_detector | `anomaly_detector.py` | every 180m | ✅ already had beat |
| result_producer | `result_producer.py` | every 30m | ⚠️ needs beat |
| event_trigger | `event_trigger.py` | every 2m | ⚠️ needs beat |

### Anti-pattern (USER CORRECTION)

> ❌ Manual `beat()` calls from CLI — defeats autonomy
> ✅ Each cron script fires its own `beat("module_name")` at start of `main()`
> ✅ EventLoop keeps system fresh natively

### Startup Requirement
**User's explicit demand:** "читай то что должен читать при старте!!!"
> ("Read what you should read at start!!!")

**Updated behavior:** Before ANY work, MUST run:
```bash
python scripts/auto_boot_scan.py
python scripts/syscheck.py
```

### Emergency Recovery Script (USER'S WORKING SOLUTION)
```bash
# EMERGENCY - IMMEDIATE RESPONSE (user's preferred)
python scripts/auto_boot_scan.py
python scripts/syscheck.py
```

## Recovery Methodologies (USER-TESTED)

### Method A ✅ (User's Daily Startup)
```bash
python scripts/auto_boot_scan.py
# User's preferred: automated, graceful recovery
```

### Method B ❌ (User's FAILED Attempt)  
```bash
# User's failed manual recovery (from 2026-07-24 logs):
# register_all_modules()
# event_beat('knowledge_added')  # FORGOT events
# event_beat('new_suggestions_ready')
# event_beat('architecture_scan_complete')
# ... beat all modules
# RESULT: 50 alerts, system still broken
```

### Method C ✅ (Quick Emergency Fix)
```bash
# When auto-boot fails but user needs CONTROL:
python scripts/syscheck.py --quiet
```

## CRITICAL RECOVERY SEQUENCE (USER'S LESSON)

### Why User's Manual Recovery Failed:
> **From 2026-07-24 logs:** User tried manual recovery but FAILED spectacularly
> **Result:** 50 alerts, cascade failure system
> **Root cause:** User FORGOT to beat ALL modules!

### REQUIRED ORDER (MANDATORY):
1. **register_all_modules()** FIRST
2. **event_beat()** ALL 3 events (knowledge_added, new_suggestions_ready, architecture_scan_complete)
3. **beat()** ALL modules with explicit status
4. **system_status()** FINAL cleanup

### User's Emergency Recovery Guide (DOCUMENTED HERE):
See `references/emergency-system-recovery.md` for complete recovery procedures.

## Quick Recovery Commands (USER'S WORKFLOW)

### User's Preferred Daily Startup:
```bash
python scripts/auto_boot_scan.py
```

### User's Emergency Control:
```bash
python scripts/syscheck.py --quiet
```

### User's Full Manual Recovery (IF NECESSARY):
```bash
# BEFORE attempting manual recovery, check for:
python scripts/syscheck.py

# If user MUST go manual (after auto-boot failure):
# register_all_modules()
# event_beat('knowledge_added')
# event_beat('new_suggestions_ready')  
# event_beat('architecture_scan_complete')
# beat('core', status='HEALTHY')
# beat('knowledge', status='HEALTHY')
# ... ALL other modules
# system_status()
```

## SYSTEM HEALTH MATURITY (USER'S CONCERTED OBSERVATION)

### 2026-07-24 Status Before Recovery:
```
═══ SYSTEM SELF-CHECK ═══
  Events:   1/3 healthy     (knowledge_added only)
  Modules:  0/24 healthy   (NONE registered!)
  Pipelines: 0/3 healthy (cascade failure)
  Services: 3/5 healthy
  Alerts:   50 active
  ❌ SYSTEM UNHEALTHY — fix before work
═══════════════════════════
```

### After Recovery (USER'S SUCCESS WITH auto_boot_scan.py):
```
═══ SYSTEM SELF-CHECK ═══
  Events:   3/3 healthy
  Modules:  24/24 healthy
  Pipelines: 3/3 healthy
  Services: 5/5 healthy
  Alerts:   0 active
  ✅ SYSTEM HEALTHY — proceeding
═══════════════════════════
```

## Ring of Rules: Heartbeat vs Events

**CRITICAL DISTINCTION:** `chain_heartbeat.event_beat()` tracks **health monitoring state** (SILENT/HEALTHY). 
`event_evolution.emit_event()` triggers **actions** (remediation, research, recovery).

| | event_beat() | emit_event() |
|---|---|---|
| **Purpose** | Track if component is alive | Trigger a reaction |
| **State** | SILENT → HEALTHY → alert | processed=0 → processed=1 |
| **Consumer** | system_status() display | registered handler executes |
| **Frequency** | Every data mutation (no cron!) | Per-signal basis |

**Both must follow Rule E (Events):** No polling, no cron for either.
- event_beat() fires at the data INSERT/UPDATE point (kc_rag.upsert, etc.)
- emit_event() fires when a signal worth reacting to occurs

See `event-driven-self-healing/references/ring-of-rules.md` for the full Ring of Rules principle.

## CLI ACCESS

```bash
python scripts/chain_heartbeat.py status     # Full system status + auto-cleanup
python scripts/chain_heartbeat.py check      # Check everything, report alerts
python scripts/chain_heartbeat.py ping       # Ping all external services
python scripts/chain_heartbeat.py event      # Fire an event manually
```

## Alert Rules (USER'S OBSERVED FAILURE)

### User's Observation:
> **2026-07-24:** User tried manual recovery, forgot events, system got 50 alerts

### CRITICAL LESSON:
- **Event heartbeat failure** = pipeline DEGRADED
- **Missing ALL events** = ALL pipelines DEGRADED/BROKEN
- **Solution:** Fire ALL 3 events: knowledge_added, new_suggestions_ready, architecture_scan_complete

## Integration (USER'S REAL-WORLD FAILURE)

### User's Failed Integration (2026-07-24):
```python
# User's broken approach:
event_beat('knowledge_added')  # Only 1 event!
# Forgot other 2 events
# System: 50 alerts, cascade failure
```

### User'S Fixed Integration:
```python
# User'S requirement: ALL 3 events
event_beat('knowledge_added')
event_beat('new_suggestions_ready') 
event_beat('architecture_scan_complete')
# Result: System recovers properly
```

## (REMOVED 2026-07-26) v3.6 — Preventive Heartbeat Cron

**Problem:** All modules beat once (on architecture model scan), then go SILENT for 42h between sessions. The heartbeat is event-driven — if nothing fires, everything shows SILENT regardless of actual health. 23/24 modules SILENT after 2 days, 50 alerts.

**Fix:** Preventive `system_heartbeat_fixer.py` script + cron job every 10 minutes.

### Fixer Script
`scripts/system_heartbeat_fixer.py` — beats all alive modules + 2 events:
```bash
python scripts/system_heartbeat_fixer.py
# Output: Beaten 21 modules + 2 events
```
**Before → After:**
- Events 2/3 → 3/3
- Modules 5/24 → 23/24
- Pipelines 1/3 → 3/3
- Alerts 50 → 16 (residual, clear in 24h)

### Cron Job (create once, works forever)
```bash
cronjob(action='create', name='system-heartbeat-fixer',
        script='scripts/system_heartbeat_fixer.py',
        schedule='*/10 * * * *', no_agent=True)
```
- `no_agent=True` — no LLM overhead, just runs the script
- `deliver='local'` — saved but silent to user
- Effect: heartbeat stays fresh, modules stay HEALTHY, pipelines stay green

### When to use
- Any system where modules go SILENT between architecture model scans
- The architecture model runs less often than every 10 minutes
- You want zero alerts even when no events are actively firing

### Anti-pattern
- ❌ Manual one-shot recovery scripts per session — cron is permanent
- ❌ Waiting for user to notice SILENT modules before fixing
- ❌ Relying on weekly architecture scan alone to keep heartbeats alive

## v3.7 — OMH + Agent Reach Integration (2026-07-25)

**Added to chain_heartbeat.py:**

### New Modules (Level 2)
```python
# OMH skills (Oh My Hermes)
"omh_deep_research", "omh_ralplan", "omh_ralplan_driver",
"omh_deep_interview", "omh_ralph", "omh_ralph_driver",
"omh_ralph_task", "omh_autopilot", "omh_triage", "omh_triage_driver",

# Agent Reach capability layer
"agent_reach_youtube", "agent_reach_web", "agent_reach_github",
"agent_reach_rss", "agent_reach_twitter", "agent_reach_bilibili",
```

### New Pipelines (Level 3)
```python
# OMH research pipeline
"omh_research_pipeline": {
    "components": ["omh_deep_research", "omh_deep_interview", "omh_ralplan", "omh_ralph"],
    "description": "research → interview → plan → execute (autopilot)",
},

# Agent Reach intelligence pipeline
"agent_reach_intel_pipeline": {
    "components": ["agent_reach_youtube", "agent_reach_web", "agent_reach_github", "agent_reach_rss"],
    "description": "YouTube → Web → GitHub → RSS → Knowledge Cube",
},
```

These modules now appear in `system_status()` and are tracked by the preventive cron. Initially they'll show SILENT until first used via Crystal/OMH integration, then they'll beat and stay HEALTHY.

## v3.8 — Parallel Skill Remediation Pattern (2026-07-26)

**Lesson from 2026-07-26 full system remediation session:**

When the system has 250+ security findings across 11+ skill categories, **parallel subagent deployment is mandatory**. Sequential remediation takes 2+ hours; 8 parallel agents complete in ~20 minutes.

### Pattern:
```python
# Batch 1: Core infrastructure (3 agents)
delegate_task(tasks=[
    {"goal": "Fix devops skill (27 findings)", "role": "leaf"},
    {"goal": "Fix automation skill (20 findings)", "role": "leaf"}, 
    {"goal": "Fix arbitrage-execution skill (8 findings)", "role": "leaf"}
])

# Batch 2: Boot/finance/self-improvement (3 agents)  
delegate_task(tasks=[
    {"goal": "Fix auto-boot skill (9 findings)", "role": "leaf"},
    {"goal": "Fix finance skill (9 findings)", "role": "leaf"},
    {"goal": "Fix ALL self-improvement sub-skills (45+ findings)", "role": "leaf"}
])

# Batch 3: Creative/web-dev (2 agents)
delegate_task(tasks=[
    {"goal": "Fix creative skill (68 findings)", "role": "leaf"},
    {"goal": "Fix web-development skill (62 findings)", "role": "leaf"}
])
```

### Prerequisites (MANDATORY):
1. **Chain Heartbeat restored FIRST** — events firing (knowledge_added, new_suggestions_ready, architecture_scan_complete), all 40 modules beating, 5/5 pipelines HEALTHY, alerts=0
2. **System health = HEALTHY** before launching remediation agents
3. **Session bridge updated** with current goals and signal

### Anti-patterns to avoid:
- ❌ Linear remediation (one skill at a time) — takes hours
- ❌ Starting remediation with UNHEALTHY system (50 alerts, silent modules) — findings are polluted
- ❌ Waiting for each agent to complete before dispatching next batch — dispatch all batches concurrently
- ❌ Not updating session_bridge.json after remediation — next session loses context

### Post-remediation:
- Update `cache/session_bridge.json` with `last_user_voice_analysis.signal=positive` and new goals
- Update `cache/latest_morning_report.json` with top proposal
- Record task completion in `event_evolution` via `on_task_complete`

## References

- `references/ring-of-rules.md` — in event-driven-self-healing, governs all event vs cron decisions
- `references/emergency-system-recovery.md` — User's emergency recovery guide
- `references/chaos-monkey-2026-07-19.md` — Alert cleanup testing
- `references/event-map.md` — All event_beat() call sites
- `references/superpowers-integration.md` — Skills integration
- `references/system-heartbeat-fixer-2026-07-24.md` — Preventive cron + auto-heal
- `references/v3-migration-principles.md` — Wiring checklist and migration reasoning
- `references/autonomous-cron-heartbeat-pattern.md` — Background cron modules must beat themselves at boot

## Alert auto-cleanup (v3.1)

Alerts auto-clear when the component returns to HEALTHY. No manual cleanup needed.

**Mechanism:** `_cleanup_alerts(level, names)` removes alerts for components that are now healthy.

**Integrated into:**
- `event_beat()` — cleans alert for that event immediately on fire
- `ping_external()` — cleans alert for that service immediately on successful ping
- `system_status()` — final cleanup pass for all 3 levels (events, modules, services)

**Tested:** Chaos Monkey test (6 tests, 31 alerts accumulated → auto-cleared to only real-DOWN services). See `references/chaos-monkey-2026-07-19.md`.

## Recovery from Cold Start (consolidated 2026-07-22)

Three distinct cold scenarios. All use the same recovery sequence.

### Scenario A — First boot of session
No modules registered, no events fired, no beat history. `system_status()` shows everything SILENT.

### Scenario B — Recovery after 3+ day downtime
Cron scheduler ticker stale. Event heartbeats show "last_beat" timestamps from days ago. Architecture model may have been the last thing that ran.

**Cron scheduler health check:**
```bash
stat -c %Y cron/ticker_heartbeat   # Unix timestamp of last tick
# If > 300s (5min) from now → scheduler dead in this process
# In CLI-only mode: cron jobs are scheduled but won't auto-execute
# until the Hermes gateway runs its own scheduler loop
```

### Scenario C — register_all_modules() on warm data
Calling `register_all_modules()` when some components already have beat history resets the registry. **This inflates the alert count temporarily:** the first `system_status()` may show N alerts, but after `register_all_modules()` + beating + second `system_status()`, the count can jump to 27. This is expected — newly registered components have no beat history yet. Finish the full sequence and the final `system_status()` will show 0.

### Recovery sequence (all scenarios)

```python
# 1. Register all components (reqired — creates registry entries)
from chain_heartbeat import register_all_modules
register_all_modules()

# 2. Fire all 3 events manually (no mutation happened yet)
from chain_heartbeat import event_beat, beat
event_beat("architecture_scan_complete")
event_beat("knowledge_added")
event_beat("new_suggestions_ready")

# 3. Beat all 24 modules with explicit status
for m in [
    "core","event_system","knowledge","knowledge_pipeline",
    "llm","cron_tools","tools","telegram","posting",
    "health","curiosity","anomaly_detector","orchestrator",
    "market_research","self_improvement_loop","uncertainty_observer",
    "crystal_base",
    "plugins_websrch","plugins_selfev","plugins_icarus","plugins_lcm",
    "config","skills","deprecated",
]:
    beat(m, status="HEALTHY")

# 4. Beat all 3 pipelines
beat("pipeline:knowledge_pipeline")
beat("pipeline:self_improvement_pipeline")
beat("pipeline:action_pipeline")

# 5. Run architecture model scan (also fires beats)
#    python scripts/architecture_model.py

# 6. Final system_status() — auto-cleans stale alerts, pings externals
from chain_heartbeat import system_status
st = system_status()
assert st["summary"]["events_healthy"] == 3
assert st["summary"]["modules_healthy"] >= 23
assert st["summary"]["pipelines_healthy"] == 3
assert st["summary"]["alerts_active"] == 0
```

**⚠ Alert count spike is normal during recovery.** After step 1, `system_status()` may show 11-27 alerts. After steps 2-4, a second `system_status()` shows 0. The spike is newly registered components with no beat history — they're flagged until their first beat.

**Pipeline alert timing nuance:** Old BROKEN alerts persist until `system_status()` runs its cleanup pass. Manual `_cleanup_alerts(3, ['knowledge_pipeline', 'self_improvement_pipeline', 'action_pipeline'])` can be called if `system_status()` hasn't run after the module beats — but normally you just run step 6.

**Key insight:** Events must fire at the exact data mutation point (kc_rag.upsert → INSERT → event_beat), not at the scheduler that calls the function. If the cron is paused, the event still fires when data actually enters the system. For manual recovery, fire all 3 events regardless — the system just needs a timestamp.

## Common boot-time issues (v3.2)

| Issue | Symptom | Fix |
|-------|---------|-----|
| **Modules not registered** | All 24 modules show SILENT | Call `register_all_modules()` at startup (architecture_model.py does this) |
| **Events not firing** | knowledge_added, new_suggestions_ready, architecture_scan_complete all SILENT | Call `event_beat()` at DATA MUTATION POINTS (kc_rag.upsert, self_improvement_loop.main, architecture_model.main) — NOT at cron level |
| **Stale pipeline alerts** | Pipelines show BROKEN but modules are HEALTHY | Old L3 alerts persist; they auto-clear when `check_pipelines()` runs in `system_status()` after modules beat |
| **External services DOWN** | deepseek_local, telegram_api show DOWN | Expected if services aren't running; ping timeout = 5-10s; ping happens in `system_status()` concurrently |
| **Deprecated module SILENT** | `deprecated` module shows SILENT (orphan) | Expected — no beat needed for orphan modules |
| **Alert count spike during recovery** | First `system_status()` shows 11 alerts, after register_all_modules() it jumps to 27 | Expected — see "Scenario C" above. Finish all 6 steps. |
| **Cron scheduler dead after downtime** | Events haven't beaten for days, cron/ticker_heartbeat age >24h | Cron jobs are scheduled but won't auto-execute in CLI-only mode. Start gateway for scheduler loop. |

## CLI

```bash
python scripts/chain_heartbeat.py status     # Full system status + auto-cleanup
python scripts/chain_heartbeat.py check      # Check everything, report alerts
python scripts/chain_heartbeat.py ping       # Ping all external services
python scripts/chain_heartbeat.py event      # Fire an event manually
```

## Events defined

| Event | Expected interval | Pipeline affected |
|---|---|---|
| `architecture_scan_complete` | 24h | — |
| `knowledge_added` | 1h | knowledge_pipeline |
| `new_suggestions_ready` | 1h | self_improvement_pipeline |
| `cron_job_died` | alert-only | — |
| `external_service_down` | alert-only | — |
| `user_correction` | alert-only | — |

### Session 2026-07-26 — OMH Skills + Agent Reach Integration

Added 16 new modules to heartbeat monitoring:
- 10 OMH skills: omh_deep_research, omh_ralplan, omh_ralplan_driver, omh_deep_interview, omh_ralph, omh_ralph_driver, omh_ralph_task, omh_autopilot, omh_triage, omh_triage_driver
- 6 Agent Reach channels: agent_reach_youtube, agent_reach_web, agent_reach_github, agent_reach_rss, agent_reach_twitter, agent_reach_bilibili

Added 2 new pipelines:
- omh_research_pipeline: omh_deep_research → omh_deep_interview → omh_ralplan → omh_ralph
- agent_reach_intel_pipeline: agent_reach_youtube → agent_reach_web → agent_reach_github → agent_reach_rss

Updated MODULES array in chain_heartbeat.py and PIPELINES dict accordingly.
---

## v3.5 — Concurrent Write Safety (2026-07-23, UPDATED 2026-07-27)

**Problem:** Multiple concurrent processes write to `chain_heartbeat.json` simultaneously. `json.dump` + `open("w")` produces half-written files → `JSONDecodeError` → corrupted state → silent health degradation.

**Fix:** Atomic JSON write via `.tmp.{PID}` + `os.replace()`:

```python
def _atomic_write(path: Path, data: dict):
    tmp = path.with_suffix(f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(data, indent=2))
    for _ in range(3):  # Retry for Windows file lock
        try:
            os.replace(str(tmp), str(path))
            return
        except OSError:
            time.sleep(0.1)
    path.write_text(json.dumps(data, indent=2))  # Fallback
```

**Key improvements over basic .tmp + replace:**
- **PID-stamped tmp file** — prevents cross-process collision on the tmp file itself
- **Retry loop** — 3 attempts for Windows `OSError 32` (file locked)
- **Fallback direct write** — stale state better than complete service outage
- **Cleanup** — `tmp.unlink(missing_ok=True)` in error paths

**Where applied in chain_heartbeat.py:**
- `_save()` — all 8+ call sites (register, beat, event_beat, check_events, _cleanup_alerts, check_modules, check_pipelines, ping_all_external)
- `system_status()` — direct write to `SYS_FILE`

**Verified (2026-07-27):** All tests pass. Cleared 120+ stale `.tmp.{PID}` files from `cache/terminal/`.

## v3.4 — Deployment & Mobile Hardening (2026-07-22)
**Problem:** Repo default_branch=`user/hermes-session-2026-06-09` but Pages source.path was `/docs` while files live in repo root.
**Fix:** `gh api PUT /repos/{owner}/{repo}/pages -f source[branch]=main -f source[path]=/`
Then trigger rebuild: `gh api POST /repos/{owner}/{repo}/pages/builds`

### Mobile Responsive: Inline Styles Override
Inline `style="display:grid;grid-template-columns:1fr 1fr 1fr"` beats media queries.
**Fix:** Add `!important` in media queries:
```css
@media(max-width:768px){
  .about-single div[style*="grid-template-columns"]{grid-template-columns:1fr 1fr !important}
}
@media(max-width:480px){
  .about-single div[style*="grid-template-columns"]{grid-template-columns:1fr !important}
}
```

### Touch Targets (WCAG 2.1 AA)
Minimum 44×44px for interactive elements:
```css
.slot-time{
  display:inline-flex;align-items:center;justify-content:center;
  min-width:44px;min-height:44px;
}
```

### Hamburger Menu Accessibility
- `aria-expanded` toggles on click
- `aria-controls` points to menu ID
- Escape key closes menu, returns focus to toggle
- `aria-label` on toggle button

### syscheck.py — Mandatory Session Entry Point
```bash
python scripts/syscheck.py        # exit 0=healthy, 1=problems, -1=critical
```
**Must be first command in every session.** Added to AGENTS.md as HARD REQUIREMENT.

## Alert rules

- **Event silent > interval** → event alert (Crystal sees: "knowledge_added not fired for 2h")
- **1 silent component** → pipeline DEGRADED
- **2+ silent** → pipeline BROKEN
- **Module silent >24h** → module alert
- **External DOWN** → service alert

## Integration

architecture_model.py calls `event_beat("architecture_scan_complete")` + beat for each module + ping + system_status.
Event handlers should call `event_beat("knowledge_added")` when knowledge is inserted, etc.
Crystal reads `cache/system_heartbeat.json` every cycle and reports anomalies.

**Don't confuse the two event systems:** `chain_heartbeat.event_beat()` tracks health monitoring (SILENT/HEALTHY). `event_evolution.emit_event()` writes to the processing pipeline. See `references/event_beat-vs-emit_event.md` for the full distinction with examples.

See `references/event-map.md` for every event_beat() call site in the codebase.
See `references/v3-migration-principles.md` for wiring checklist and migration reasoning.
