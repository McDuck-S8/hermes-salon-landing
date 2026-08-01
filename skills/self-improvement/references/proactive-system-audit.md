# Proactive System Audit — Executable Checklist

Use this checklist when the user asks "check the system" / "audit stability" / "test proactivity".

## 1. Cron Scheduler Alive?

```bash
# Windows
tasklist | grep python
```

Output should show hermes gateway process (PID from `~/.hermes/cron/.gateway`).
No process = dead scheduler regardless of `cronjob list`.

## 2. All Data Sources Have Real Content

Check each DB:

```bash
# Events DB
python3 -c "import sqlite3; c=sqlite3.connect('cache/events.db'); print('Events:', c.execute('SELECT COUNT(*) FROM events').fetchone()[0]); print('Triggers:', c.execute('SELECT COUNT(*) FROM triggers').fetchone()[0]); print('Pending:', c.execute('SELECT COUNT(*) FROM events WHERE processed=0').fetchone()[0])"

# Knowledge Cube
python3 -c "import sqlite3; c=sqlite3.connect('cache/knowledge_cube.db'); print('Knowledge:', c.execute('SELECT COUNT(*) FROM experiences').fetchone()[0])"

# Core Engine
python3 -c "import sqlite3; c=sqlite3.connect('cache/core_engine.db'); print('Gaps:', c.execute('SELECT COUNT(*) FROM gaps').fetchone()[0]); print('Actions:', c.execute('SELECT COUNT(*) FROM proactive_actions').fetchone()[0])"

# Session DB
python3 -c "import sqlite3; c=sqlite3.connect(str(Path.home())+'/.hermes/state.db'); print('Sessions:', c.execute('SELECT COUNT(*) FROM sessions').fetchone()[0])"
```

## 3. Cron Jobs Actually Running

```bash
hermes cron list
```

Check:
- `last_run_at` is RECENT (not 3+ days ago)
- `last_status` is "ok" (not "error")
- Jobs with `no_agent=True` + script reliably pass
- LLM-based jobs often fail silently — inspect output

## 4. Event Pipeline Works

```bash
cd scripts && python3 -c "
from event_evolution import process_pending_events
result = process_pending_events()
print(f'Processed: {result[\"processed\"]}/{result[\"total\"]}')
print(f'Errors: {result[\"errors\"]}')
"
```

## 5. Event-Driven Trigger Present

Check if the event-trigger cron exists and is recent:

```bash
hermes cron list | grep event-trigger
```

Required: schedule `every 2m`, no_agent=True, script=event_trigger.py

## 6. All 17 Standard Cron Jobs Present

| Job | Schedule | Mode | Status |
|---|---|---|---|
| event-trigger | every 2m | no_agent | Should be ok |
| system-watcher | every 60m | no_agent | Should be ok |
| unified-system-cycle | every 120m | no_agent | Should be ok |
| subconscious-loop | every 120m | no_agent | Should be ok |
| auto-fetch-sessions | every 60m | no_agent | Should be ok |
| nightly-self-analysis | 0 2 * * * | no_agent | Should be ok |
| morning-report | 0 8 * * * | no_agent | Should be ok |
| dream-memory-consolidation | 0 3 * * * | no_agent | Should be ok |
| memory-consolidation | 0 3 * * * | no_agent | Should be ok |
| skill-evolution | 0 4 * * * | no_agent | Should be ok |
| self-assessment | 0 1 * * * | no_agent | Should be ok |
| update-runtime-context | 30 4 * * * | no_agent | Should be ok |
| cube-feeder | 15 4 * * * | no_agent | Should be ok |
| dimension-discovery | 45 4 * * * | no_agent | Should be ok |
| nightly-brain-scan | 0 3 * * * | no_agent | Should be ok |
| cube-session-ingester | 0 */6 * * * | no_agent | Should be ok |
| free-api-health-check | every 360m | no_agent | Should be ok |

## Proactivity Score

| Dimension | Max | Score | Criteria |
|---|---|---|---|
| Events processed | 10 | — | Pending=0, triggers have recent last_triggered |
| Autonomous cycle | 10 | — | All 3 layers running on schedule |
| Error handling | 10 | — | Errors produce events, events fire knowledge capture |
| User notification | 10 | — | Results reach user (Telegram or deliver=origin) |
| Knowledge utilization | 10 | — | Knowledge cube feeds into current work |

Total: /50. 40+ = truly autonomous.

## What "Real Proactivity" Requires

Ranked by impact:

1. **Proactive actions executor** — engine generates suggested actions, but
   nothing executes them. Need a component that reads proactive_actions table
   and runs them.
2. **User notification** — results go to local files, not to the user.
   Without notification, the system is working in a vacuum.
3. **Knowledge cube active use** — 600+ records sitting unused. Need recall
   at session start.
4. **True event-driven** — 2m polling is near-real-time but not event-driven.
   True event-driven requires hooks at task completion firing into the
   processing pipeline.
