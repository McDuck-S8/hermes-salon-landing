# Window Spam from Cron (2026-07-04)

## Problem
Hermes gateway runs cron jobs as a background thread (every 60s tick). Each `no_agent: true` job spawns a **separate Python subprocess** when triggered. Multiple jobs with short intervals (1m, 2m, 5m) cause "window spam" — dozens of python.exe/pythonw.exe processes flooding Task Manager.

## Root Cause
Gateway PID holds cron ticker; each tick checks due jobs; each due job spawns subprocess. The ticker runs in `gateway/run.py` → `_start_cron_ticker()` → `InProcessCronScheduler().start()`.

## Fixes
1. Pause problematic jobs: `cronjob(action='pause', job_id=...)`
2. Increase intervals: edit `jobs.json` → `schedule.minutes`
3. Stop gateway entirely: `hermes gateway stop` (kills ticker + all spawned processes)
4. Convert polling jobs to event-driven (signal_daemon pattern)

## Diagnosis
```bash
# Check gateway PID
cat gateway.pid

# Check ticker heartbeat
cat cron/ticker_heartbeat  # epoch timestamp

# Kill all python processes if needed
taskkill /F /IM python.exe /IM pythonw.exe
```