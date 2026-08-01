---
name: devops-toolkit
description: "Unified DevOps toolkit for Hermes: chain-heartbeat (event-driven monitoring), proactive-doer (autonomous fix executor), cron-maintenance (scheduled job health), mandatory-system-health-reflex (3-layer health gate), webhook-subscriptions (event-driven agent runs), always-on-agent (background surveillance). One skill to load, six engines at hand."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [devops, monitoring, cron, health-check, webhooks, autonomous, self-healing]
    related_skills: [chain-heartbeat, proactive-doer, cron-maintenance, mandatory-system-health-reflex, webhook-subscriptions, always-on-agent, auto-recovery, process-supervisor, kill-switches, kanban-orchestrator]
  skill_updated: "2026-07-24"
  created_by: "auto_patch_g007"
  component_skills:
    - chain-heartbeat
    - proactive-doer
    - cron-maintenance
    - mandatory-system-health-reflex
    - webhook-subscriptions
    - always-on-agent
---

# DevOps Toolkit — Unified Interface

**One skill to load. Six DevOps engines. Zero context switching.**

This meta-skill wraps the six core DevOps skills into a single loadable unit with a unified command interface.

## Quick Start

```python
# Load once, get all six engines
from hermes_tools import skill_view
skill_view("devops/devops-toolkit")

# Now you have:
# - chain-heartbeat        (5-level event-driven monitoring)
# - proactive-doer         (autonomous fix executor, runs every 15min)
# - cron-maintenance       (scheduled job health & cleanup)
# - mandatory-system-health-reflex (3-layer health gate: syscheck+self_check+AGENTS.md)
# - webhook-subscriptions  (event-driven agent runs via HTTP)
# - always-on-agent        (background surveillance: fast/medium/deep sensors)
```

## Component Skills

| Skill | Purpose | Trigger |
|-------|---------|---------|
| **chain-heartbeat** | 5-level event-driven monitoring (events → modules → pipelines → services → JSON) | Data mutation events: `knowledge_added`, `new_suggestions_ready`, `architecture_scan_complete` |
| **proactive-doer** | Autonomous cron-run fix executor: cleans stale locks, repairs broken JSON, restarts failed jobs, clears stale cache | Cron: `*/15 * * * *` |
| **cron-maintenance** | Scheduled job health: finds dead cron jobs, diagnoses, cleans up | Cron: `0 3 * * *` |
| **mandatory-system-health-reflex** | 3-layer health gate: `chain_heartbeat.self_check()` + `syscheck.py` + AGENTS.md rules | MANDATORY at every session start |
| **webhook-subscriptions** | Dynamic webhook subscriptions: GitHub, Stripe, CI/CD, IoT → Hermes agent runs | HTTP POST to `/webhook/<name>` |
| **always-on-agent** | Background surveillance: fast (30m), medium (1h), deep (6h) sensors. Signal scoring → Telegram | Cron: `*/30`, `0 *`, `0 */6` |

## Key Updates (v3.10/v3.11 — chain-heartbeat)

- **Autonomous cron module heartbeats**: 9 background modules now self-beat in `main()` — `proactive_doer`, `proactive_executor`, `self_healing_monitor`, `autonomous_agent`, `pipeline_cron`, `knowledge_gap_filler`, `anomaly_detector`, `result_producer`, `event_trigger`
- **Manual state recovery pattern**: Direct JSON write to `cache/chain_heartbeat.json` when API hangs on external pings (see `chain-heartbeat/references/manual-state-recovery.md`)
- **event_beat() vs emit_event() distinction clarified**: health monitoring vs action triggering
- **Autonomous operation rules encoded**: parallel first, background by default, self-healing heartbeat, no permission questions

## Unified Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: HEALTH GATE (mandatory-system-health-reflex)           │
│   python scripts/syscheck.py  →  exit 0 = healthy, proceed      │
│   If fail: STOP. Fix before work.                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: EVENT-DRIVEN MONITORING (chain-heartbeat)              │
│   Level 1: Events (knowledge_added, new_suggestions_ready)      │
│   Level 2: Modules (24 modules, heartbeat on scan)              │
│   Level 3: Pipelines (knowledge, self-improvement, action)      │
│   Level 4: External services (BrowserOS, BrowserClaw, OpenRouter)│
│   Level 5: System JSON (cache/system_heartbeat.json)            │
│   No daemons. Events fire at mutation points.                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 3: AUTONOMOUS EXECUTION (proactive-doer + always-on-agent)│
│   proactive-doer (every 15min):                                 │
│     • Clean stale locks (.lock files >1h)                       │
│     • Repair broken JSON (cache/*.json)                         │
│     • Restart failed cron jobs                                  │
│     • Clear stale cache (>24h)                                  │
│   always-on-agent (3 tiers):                                    │
│     • FAST (30m): arbitrage sensors, offer changes              │
│     • MEDIUM (1h): traffic costs, CPA network health            │
│     • DEEP (6h): competitive intel, market shifts               │
│     Signal scored → Telegram if threshold met                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 4: SCHEDULED MAINTENANCE (cron-maintenance)               │
│   Daily 03:00:                                                  │
│     • Dead cron job detection & restart                         │
│     • Log rotation & cleanup                                    │
│     • Stale cache purge                                         │
│     • Job health report → Telegram                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 5: EXTERNAL TRIGGERS (webhook-subscriptions)              │
│   hermes webhook subscribe github-issues \\                     │
│     --events "issues" \\                                        │
│     --prompt "New issue #{issue.number}: {issue.title}..." \\   │
│     --deliver telegram --deliver-chat-id "-100123..."           │
│   Auto-HMAC, hot-reload, idempotent delivery                    │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Commands Reference

### Health Gate (run FIRST every session)
```bash
python scripts/syscheck.py
# OR from Python:
from scripts.chain_heartbeat import self_check
self_check()  # prints table, returns dict, exits 1 if unhealthy
```

### Chain Heartbeat Status
```bash
python -c "
from scripts.chain_heartbeat import system_status
st = system_status()
s = st['summary']
print(f'Events: {s[\"events_healthy\"]}/{s[\"events_total\"]}')
print(f'Modules: {s[\"modules_healthy\"]}/{s[\"modules_total\"]}')
print(f'Alerts: {s[\"alerts_active\"]}')
"
```

### Webhook Management
```bash
# List
hermes webhook list

# Create (GitHub issues example)
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "New GitHub issue #{issue.number}: {issue.title}\n\nAction: {action}\nAuthor: {issue.user.login}\nBody:\n{issue.body}\n\nPlease triage." \
  --deliver telegram --deliver-chat-id "-100123456789"

# Test
hermes webhook test github-issues --payload '{"issue":{"number":42,"title":"Test","user":{"login":"user"},"body":"test body"},"action":"opened"}'
```

### Always-On Agent (background surveillance)
```bash
# Check cron jobs
crontab -l | grep always-on

# Fast sensor (30m): CPA offer changes, arbitrage gaps
# Medium sensor (1h): traffic costs, network health
# Deep sensor (6h): competitive intel, market shifts
```

### Proactive Doer (runs automatically every 15min)
```bash
# Manual run
python scripts/utilities/proactive_doer.py

# What it does:
# 1. Finds .lock files older than 1h → removes
# 2. Scans cache/*.json for parse errors → repairs
# 3. Checks cron jobs in jobs.json → restarts dead ones
# 4. Clears cache files older than 24h
```

### Cron Maintenance
```bash
# Manual run
python scripts/cron-maintenance_cron.py

# What it does:
# 1. Reads cron/jobs.json
# 2. Checks each job's last run & exit code
# 3. Reports dead/stuck jobs
# 4. Attempts restart for failed jobs
# 5. Sends Telegram report
```

## Integration with Knowledge Cube

After ANY DevOps action, log to KC:

```python
from scripts.event_evolution import on_task_complete
on_task_complete(
    content="Restarted dead cron job 'arbitrage-sensors' (exit code 137). Proactive-doer caught it.",
    tags=["devops", "cron", "self_healing", "proactive_doer", "success"],
    source="agent"
)
```

## Anti-Patterns (from 80 DevOps failures)

| Anti-Pattern | Countermeasure |
|--------------|----------------|
| Skip syscheck, start working | **Layer 1 is mandatory**. 3-layer gate blocks work on unhealthy system |
| Wait for cron to report dead job | **Proactive-doer runs every 15min**. Catches dead jobs before cron does |
| Poll for changes | **Chain-heartbeat is event-driven**. Events fire at mutation points (kc_rag.upsert, self_improvement_loop.main) |
| Manual webhook config | **Dynamic subscriptions persist to ~/.hermes/webhook_subscriptions.json**, hot-reload |
| Single health check | **3-layer gate**: syscheck + self_check + AGENTS.md rules |

## Defensive Infrastructure Layer (v2026-07-29)

Four cross-platform reliability modules added to eliminate recurring failure classes:

| Module | Purpose | Eliminates |
|--------|---------|------------|
| `scripts/fs_utils.py` | Atomic writes, safe I/O, file locking, atomic JSON updates, path resolution | Filesystem/path bugs |
| `scripts/tool_registry.py` | Tool discovery, version checking, fallback chains, pre-flight checks | "command not found" surprises |
| `scripts/process_manager.py` | Heartbeat monitoring, timeout handling, graceful kill, restart logic | Subprocess hangs |
| `scripts/platform_utils.py` | Cross-platform abstractions (shell, paths, memory, disk, process kill) | Windows-specific blindness |

**Usage (mandatory per DIRECTIVE 0x16):**
```python
# NEVER call open(), shutil.*, subprocess.run() directly
from scripts.fs_utils import safe_write_json, atomic_write, file_lock
from scripts.tool_registry import check_tool, require_tool, run_tool
from scripts.process_manager import ProcessConfig, get_process_manager
from scripts.platform_utils import run_command, kill_process, is_windows
```

**DIRECTIVE 0x16: DEFENSIVE_INFRASTRUCTURE** — Use these abstractions for ALL file I/O, tool calls, subprocesses, cross-platform ops. Never call raw stdlib functions directly.

## YouTube Pipeline Resilience (v2026-07-29)

Applied yt-dlp-rescue (CRtheHILLS/yt-dlp-rescue) battle-tested fixes for YouTube SABR + bot detection:

```python
# Player client rotation (most reliable first)
player_clients = ["tv", "web_embedded", "android_vr", "tv_downgraded", "web_creator", "mweb"]

# Skip webpage request → fewer HTTP calls, less rate limiting
player_skip = "webpage"

# Force IPv4 for cloud servers
force_ipv4 = True

# Sort-based format selection (resilient to SABR format ID changes)
format_sort = "res:1080"
```

**Fallback Chain:**
1. oembed (200ms, metadata only)
2. curl + SOCKS5 proxy + HTML regex
3. yt-dlp with rescue args + PO Token server
4. Local faster-whisper for audio transcription

**PO Token Server (for bot detection bypass):**
```bash
export YT_DLP_POT_PROVIDER_URL="http://127.0.0.1:4416"
# Critical: Without this env var, the server runs but yt-dlp doesn't know it exists!
```

---

**Origin:** DevOps domain — 183 entries, 80 failures (44% failure rate), 24 successes
**Created:** 2026-07-24 via auto_patch_g007
**Target:** g-007 Unlock: devops (next mature key after debugging)