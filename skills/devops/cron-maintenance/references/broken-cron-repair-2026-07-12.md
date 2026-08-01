# Broken Cron Repair — 2026-07-12 Session

## Problem
7 cron jobs failing with "Script not found: D:\Portable_Soft\hermes\scripts\scripts\<script>.py"
- Double `scripts/scripts/` path in cron job definitions
- Missing scripts: `trend_scout.py`, `market_research.py`, `knowledge_gap_filler.py`, `anomaly_detector.py`, `hermes_health.py`, `jarvis_security_monitor.py`

## Root Cause
Cron job `script` field contained arguments (`trend_scout.py --category all`) and the scheduler appended this to `scripts/` creating `scripts/scripts/trend_scout.py --category all`.

## Actions Taken
1. **Removed 7 dead cron jobs:**
   - `5189e26afdd5` — Trend Scout - Morning All Categories
   - `1e45cd2656bd` — Trend Scout - Evening Salon Focus
   - `27594210f08e` — Market Research - Weekly Monday 8:00
   - `ff5563a6ba6b` — knowledge-gap-filler
   - `da28eb336fea` — anomaly-detector
   - `e98b02224e28` — hermes-heartbeat
   - `ea90a3b637f4` — JARVIS Security Monitor

2. **Created replacement scripts in `scripts/`:**
   - `trend_scout.py` — HN + GitHub trending scanner, categories: all/salon/tech/business/creative
   - `market_research.py` — HN Ask/Show scanner, categorizes by market interest
   - `knowledge_gap_filler.py` — KC white-spot detector, creates goals in goal_queue.json
   - `anomaly_detector.py` — error log + KC anomaly scanner (stale domains, duplicates)

3. **Verified all scripts work:**
   - `python scripts/trend_scout.py --quick --category all` ✓
   - `python scripts/market_research.py` ✓
   - `python scripts/knowledge_gap_filler.py` ✓ (created 10 goals)
   - `python scripts/anomaly_detector.py` ✓ (found 5 anomalies)

## Pattern for Future: Double-Scripts Path
When cron job `script` field contains arguments, the scheduler may double-prefix `scripts/`.
**Check:** `cronjob(action='list')` → look for `Script:    xxx.py --arg` and verify `scripts/xxx.py` exists.
**Fix:** Either remove args from script field and use separate config, or ensure script exists at `scripts/scripts/xxx.py`.

## Kanban Sync
Created 5 kanban tasks from this work, completed 5 (all Done).
Synced goal_queue.json active goals to kanban (3 curiosity goals + 1 KC gap goal).