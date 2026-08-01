---
name: crystal-architecture-awareness
description: >-
  Crystal's self-map of Hermes system. Run on each Crystal cycle to inventory
  modules, connections, file changes, and update the architecture model in
  Knowledge Cube. Reports health per module, broken connections, diffs.
  Includes Shame Counter for _deprecated/ files.
version: 1.1.0
author: Hermes Agent
license: MIT
compatibility: Python 3.10+ | knowledge_cube.db | scripts/architecture_model.py
metadata:
  hermes:
    tags: [crystal, architecture, model, self-map, awareness, shame]
    related_skills: [crystal-self-learning, chain-heartbeat, proactive-executor]
---

# Crystal Architecture Awareness

On each cycle, Crystal runs `scripts/architecture_model.py` to build a live
model of the Hermes system: modules, connections, health status, diffs,
and the Shame Counter for `scripts/_deprecated/`.

## Trigger

Use when:
- Crystal cycle starts (architecture diff check)
- After any script/module change (git commit, new file, deleted file)
- Before making architectural decisions (what to fix, what to improve)
- Healing/debugging session (find broken connections)
- Crystal self-awareness / shame check

## How it works

The model has 4 layers matching the матрёшка pattern:

### Layer 1: System Context
Hermes vs external world: User, Telegram, GitHub, CPA, BrowserOS, RSS, YouTube, LLM APIs

### Layer 2: Pipelines (Containers)
1. Knowledge Pipeline (RSS → filter → KC)
2. Crystal Pipeline (KC → observe → diagnose → will → record)
3. Self-Improvement Pipeline (hooks → fixes → suggestions → skills)
4. Action Pipeline (ghost-surfer → browser → register → post)
5. Heartbeat Chain (scanner → bus → improve → consumer → crystal)

### Layer 3: Components
24 modules across 7 layers (engine, knowledge, io, automation, action, self-improvement, infra)

### Layer 4: File Map
Each module's files tracked by existence + hash. Diff detects new/dead/changed files.

### Layer 5: Shame Counter
Every file in `scripts/_deprecated/` tracked by age. Files >30d SHAMED.

## Procedure

### 1. Run architecture scan
```bash
cd $HERMES_HOME
python scripts/architecture_model.py
```

### 2. Read the result
Model is written to Knowledge Cube (tags: ["architecture", "crystal", "model"])
and saved to `data/architecture_model.json`.

### 3. Analyze diffs
Check `changes` field. Each item tells you:
- What module changed 
- Old health → new health
- No changes = stable system

### 4. Read the Shame Counter
The report includes a `Deprecated Shame Counter` section listing every file in
`scripts/_deprecated/` with its age in days. Files older than 30 days are
marked **SHAMED**.

Crystal MUST read this section and for every SHAMED file ask:
> "Почему этот модуль всё ещё мёртв? Либо восстанови, либо удали навсегда."

Then for each SHAMED file, **read its actual contents** (not just the filename)
and classify into one of:

1. **Duplicate** — same logic exists in `scripts/` or a skill → unsafe delete
2. **Unique** — no live equivalent → restore to `scripts/`
3. **Garbage** — test, one-shot fix, scratch, old copy → safe delete

Refer to `references/deprecated-file-classification.md` for the full procedure
with commands and categorization heuristics.

If any file is SHAMED, file a task or create a KC entry documenting the decision.

### 5. Check system heartbeat
```python
from chain_heartbeat import system_status
st = system_status()
s = st["summary"]
print(f"Events:   {s['events_healthy']}/{s['events_total']} healthy")
print(f"Modules:  {s['modules_healthy']}/{s['modules_total']} healthy")
print(f"Pipelines:{s['pipelines_healthy']}/{s['pipelines_total']} healthy")
print(f"Services: {s['services_healthy']}/{s['services_total']} alive")
print(f"Alerts:   {s['alerts_active']}")
```
Read `cache/system_heartbeat.json` for full detail per-level. Report which events
are SILENT (knowledge_added, new_suggestions_ready, architecture_scan_complete)
and why — this tells Crystal whether the pipeline is actually flowing data.

### 6. Report awareness state
After each scan, Crystal should state:
- How many modules, their health distribution
- Any BROKEN connections (and what module is missing)
- What changed since last scan
- Shame Counter: how many files in _deprecated/, how many SHAMED
- Heartbeat: events healthy/total, pipelines healthy/total, external services
- Which events are SILENT and what that means for data flow

## Health states
- **HEALTHY** — all tracked files exist
- **DEGRADED** — some files missing (partial)
- **DEAD** — no files found (module may be placeholder/stub)
- **ACTIVE** — both ends of a connection exist
- **BROKEN** — one or both ends of a connection are missing
- **SHAMED** — file in _deprecated/ older than 30 days

## Session boot sequence (Crystal cycle)

Crystal MUST run this sequence at the start of every session:

```python
# 1. Architecture scan (fires architecture_scan_complete event)
python scripts/architecture_model.py

# 2. System heartbeat check
from chain_heartbeat import system_status, register_all_modules
register_all_modules()  # register all 24 modules
st = system_status()
s = st["summary"]
print(f"Events:   {s['events_healthy']}/{s['events_total']} healthy")
print(f"Modules:  {s['modules_healthy']}/{s['modules_total']} healthy")
print(f"Pipelines:{s['pipelines_healthy']}/{s['pipelines_total']} healthy")
print(f"Services: {s['services_healthy']}/{s['services_total']} alive")
print(f"Alerts:   {s['alerts_active']}")

# 3. If events are SILENT, fire them from mutation points
from chain_heartbeat import event_beat, beat
if st["levels"]["events"]["knowledge_added"]["status"] == "SILENT":
    event_beat("knowledge_added")
if st["levels"]["events"]["new_suggestions_ready"]["status"] == "SILENT":
    event_beat("new_suggestions_ready")

# 4. Beat all modules with explicit status from architecture_model
for m in ["core", "event_system", "knowledge", "knowledge_pipeline", "llm", 
          "cron_tools", "tools", "telegram", "posting", "health", "curiosity", 
          "anomaly_detector", "orchestrator", "market_research", "self_improvement_loop",
          "uncertainty_observer", "crystal_base", "plugins_websrch", "plugins_selfev",
          "plugins_icarus", "plugins_lcm", "config", "skills", "deprecated"]:
    beat(m, status="HEALTHY")  # or DEGRADED/DEAD from architecture_model

# 5. Beat pipelines
beat("pipeline:knowledge_pipeline")
beat("pipeline:self_improvement_pipeline")
beat("pipeline:action_pipeline")

# 6. Re-check status after beats
st = system_status()
```

**Critical lesson from 2026-07-20 session:** Events must fire at the exact **data mutation point**, not at the cron/scheduler level. The 3 core events (`knowledge_added`, `new_suggestions_ready`, `architecture_scan_complete`) were SILENT because they hadn't been fired since the last architecture_model run. After firing them manually and beating modules, all 3 events + 23/24 modules + 3/3 pipelines became HEALTHY in one call to `system_status()`.

## Pitfalls
- `knowledge_cube.db` must exist and have the right schema (auto-created by script)
- First run shows many DEAD modules — this is baseline, not alarm
- Module detection is by tracked files list; new modules must be added to MODULES dict
- Gateway-service and browser-harness are separate projects — their files don't live in HERMES_HOME
- **Shame Counter is not for deletion — it's for accountability.** File stays until restored or deleted.
  Each cycle Crystal must report the count and shame status.
- **Do not judge deprecated files by filename alone.** Always read the first 10 lines or docstring
  before classifying (duplicate / unique / garbage). A filename like `curiosity_engine.py` or
  `orchestrator.py` tells you nothing about whether the logic lives elsewhere.
- **Events not firing at mutation points = SILENT pipelines.** If kc_rag.upsert doesn't call event_beat("knowledge_added"), the knowledge_pipeline will show DEGRADED even if modules are HEALTHY.
- **Stale pipeline alerts persist** until `system_status()` runs and calls `check_pipelines()` which cleans them via `_cleanup_alerts()`. If you just beat modules but don't call `system_status()`, L3 alerts from previous runs will still show BROKEN.
