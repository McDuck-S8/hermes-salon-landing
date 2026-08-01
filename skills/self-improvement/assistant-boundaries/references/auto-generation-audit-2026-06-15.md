# Auto-Generation Pipeline Audit (2026-06-15)

## Problem
Hermes had a self-feeding pipeline of 30+ cron jobs running in background.
Each script produced data that fed the next script — no user ever asked for any of it.

## Numbers
- **30+ cron jobs** running in background
- **14,781 entities** in Entity Cube — 94% were generic `concept` (noise)
- **11,999 relationships** — 68% were `co_occurs_with` (meaningless)
- **219 auto-generated SKILL.md files** — most from auto-evolution
- **4,137 Knowledge Cube entries** — mostly from crystal logs (1,297) + skill-indexer (857)
- **49 white spot clusters** — machine-generated noise

## Cron Jobs Stopped (all paused)

### Daily ron (4am block)
- `cube-feeder` (4:15am) — feeds Knowledge Cube automatically
- `dimension-discovery` (4:45am) — auto-discovers dimensions
- `skill-evolution` (4am) — creates auto-skills
- `update-runtime-context` (4:30am) — updates skill context
- `self-evolution-cycle` (4am) — runs skill_indexer + latent_domain + skill_evolution
- `self-improvement-loop` (5am) — auto-improvement

### Nightly (1-3am block)
- `self-assessment` (1am) — self-assessment
- `nightly-brain-scan` (3am) — brain scan (already broken)
- `memory-consolidation` (3am) — auto-consolidation
- `dream-memory-consolidation` (3am) — dream memory

### Frequent pollers (red flags)
- `event-trigger` — every 2 minutes (!!!) — tight loop
- `llm-analyst` — every 15 minutes (560 completed runs)
- `proactive-doer` — every 15 minutes (74 completed runs)
- `proactive-executor` — every 15 minutes (270+ completed runs)
- `self-healing-monitor` — every 15 minutes
- `result-producer` — every 30 minutes
- `autonomous-agent` — every 30 minutes (50 completed runs)
- `subconscious-loop` — every 120 minutes (140 completed runs)
- `unified-system-cycle` — every 120 minutes (29 completed runs)

### Cube pipeline (every 6h)
- `cube-session-ingester` — ingests sessions into cube
- `cube-categorizer` — categorizes cube entries
- `cube-to-memory` — copies cube to memory

### Other auto-jobs
- `auto-fetch-sessions` — every 60min (245 completed runs)
- `system-watcher` — every 60min
- `knowledge-surfacer` — every 360min (auto-report)
- `knowledge-gap-filler` — every 120min (auto-fill gaps)
- `anomaly-detector` — every 180min (auto-detect)
- `uncertainty-observer` — daily at 9am
- `research-worker` — every 240min (auto-research)
- `crystal-self-learning` — every 360min
- `telegram-delivery` — every 60min
- `system-metrics` — every 360min
- `hermes-heartbeat` — every 60min (already broken)
- `JARVIS Security Monitor` — every 120min (already broken)
- `free-api-health-check` — every 360min
- `Trend Scout` — morning + evening
- `Market Research` — weekly

## Cron Jobs Kept Running
- `salon-bot-watchdog` — keeps bot alive
- `provider-guard` — provider health (one-shot)
- `provider-auto-fallback` — auto-switch provider
- `nightly-self-analysis` — night report to Telegram
- `morning-report` — morning report
- `daily-report` — daily report

## Entity Engine Deleted
- entity_engine.py
- run_entity_analysis.py
- cache/entity_engine.db
- AGENTS.md marked as DELETE ON CONFIRM

## Root Cause
The system was designed as a PROACTIVE data generator — scripts that feed other scripts.
No user ever asked for entity analysis, auto-skills, or white spot detection.
The system was producing "analysis of analysis" — numbers without insight.
