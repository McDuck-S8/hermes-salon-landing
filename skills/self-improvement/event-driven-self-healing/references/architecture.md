# Event-Driven Self-Healing Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HERMES EVENT-DRIVEN HEALING                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────────────────┐   │
│   │   CRON JOBS  │────▶│  PROCEDURAL  │────▶│       EVENT BUS          │   │
│   │  (jobs.json) │     │  EXECUTOR    │     │   (event_bus.py)         │   │
│   └──────────────┘     │ (5 min loop) │     └───────────┬──────────────┘   │
│                        └──────────────┘                 │                  │
│                                 │                       │                  │
│                    ┌────────────┴────────────┐          │                  │
│                    ▼                         ▼          ▼                  │
│           ┌─────────────────┐       ┌─────────────────┐ ┌─────────────┐   │
│           │  TRIGGER-012    │       │   OTHER         │ │   EVENTS    │   │
│           │ cron_job_health │       │  TRIGGERS       │ │  EMITTED    │   │
│           └────────┬────────┘       └─────────────────┘ └──────┬──────┘   │
│                    │                                             │          │
│                    ▼                                             ▼          │
│           ┌─────────────────┐                           ┌─────────────────┐  │
│           │ emit("cron_     │                           │  DIRECT         │  │
│           │  job_died", {   │                           │  HANDLERS       │  │
│           │  job_id,        │                           │  (instant,      │  │
│           │  job_name,      │                           │   no cron)      │  │
│           │  last_error})   │                           └────────┬────────┘  │
│           └────────┬────────┘                                    │          │
│                    │                                             │          │
│                    ▼                                             ▼          │
│           ┌─────────────────┐                           ┌─────────────────┐  │
│           │ EVENT_JOB_MAP   │                           │ _handle_*()     │  │
│           │ cron_job_died:  │                           │ - boost_goal()  │  │
│           │   [procedural-  │                           │ - run           │  │
│           │    executor,    │                           │   procedural_   │  │
│           │    self-healing]│                           │   executor      │  │
│           └────────┬────────┘                           │ - log ALERTS    │  │
│                    │                                   └────────┬────────┘  │
│                    ▼                                            │          │
│           ┌─────────────────┐                                   │          │
│           │ CRON BACKUP     │                                   ▼          │
│           │ (runs on next   │                           ┌─────────────────┐  │
│           │  scheduled tick)│                           │ BAYESIAN SCORER │  │
│           └─────────────────┘                           │ (bayesian_      │  │
│                                                         │  scorer.py)     │  │
│                                                         │ - boost_goal()  │  │
│                                                         │   +2 for 15min  │  │
│                                                         │   goal_queue    │  │
│                                                         │   priority      │  │
│                                                         └─────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Event Flow Details

### 1. Cron Job Death Detection
```
CRON JOB (error + missed run)
       │
       ▼
procedural_executor.py:trigger_cron_job_health()  [every 5 min]
       │
       ├──▶ emit("cron_job_died", payload)
       │
       ├──▶ Auto-fix job: next_run_at = now+5min, status=pending
       │
       └──▶ Log ALERTS.md: "TRIGGER-012: Cron job 'X' was dead — auto-restarted"
```

### 2. Event Processing
```
event_bus.py:process_events()
       │
       ├──▶ EVENT_JOB_MAP → queues cron jobs (backup)
       │
       └──▶ DIRECT_EVENT_HANDLERS → runs IMMEDIATELY
               │
               ├──▶ _handle_cron_job_died()
               │       ├──▶ boost_goal("g-001", +2, 15min)
               │       └──▶ subprocess: procedural_executor --run cron_health
               │
               ├──▶ _handle_heartbeat_missed()
               │       ├──▶ boost_goal("g-001", +1.5, 10min)
               │       └──▶ subprocess: procedural_executor --run signal_daemon
               │
               └──▶ _handle_knowledge_cube_stale()
                       └──▶ subprocess: cube_feeder.py
```

### 3. Bayesian Priority Boost
```
bayesian_scorer.py:boost_goal(goal_id, boost, duration)
       │
       ├──▶ Load goals from cache/goal_queue.json
       │
       ├──▶ Find goal by ID
       │
       ├──▶ goal["priority"] = min(10, current + boost)
       │
       ├──▶ goal["boosted_until"] = now + duration
       │
       ├──▶ goal["boost_reason"] = "Auto-boost from event at <timestamp>"
       │
       ├──▶ goal["updated_at"] = now
       │
       └──▶ Save with _backup_file() → atomic write
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Procedural trigger every 5 min** | Matches existing `procedural-executor` cron job schedule |
| **Direct handlers (not cron)** | Instant recovery — no waiting for next cron tick |
| **Bayesian boost +2 for 15min** | Strong enough to jump queue, short enough to auto-expire |
| **Auto-restart job in trigger** | Self-healing happens BEFORE event processing completes |
| **ALERTS.md logging** | Human-visible audit trail of autonomous recoveries |
| **procedural_feedback.jsonl** | Machine-readable for pattern analysis |

## Failure Modes & Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Event handler timeout (10s) | Logs "⚠ handler timed out" | Increase `_DIRECT_HANDLER_TIMEOUT` or optimize subprocess |
| boost_goal import error | `_backup_file` not defined | Added helper to bayesian_scorer.py |
| Timezone parse error | `next_run_at` ISO format varies | Use `.replace("Z", "").split("+")[0]` |
| Goal not found | boost_goal target missing | Logs warning, continues |
| Duplicate event emission | Same dead job detected twice | Event deduplication in event_bus (id-based) |

## Monitoring Commands

```bash
# Full system health
python scripts/procedural_executor.py

# Watch real-time events
python scripts/event_bus.py pending

# Check recent recoveries
tail -20 cache/ALERTS.md | grep TRIGGER-012

# Verify goal boosts
python -c "
import sys; sys.path.insert(0,'scripts')
from bayesian_scorer import _load_goals_from_file
for g in _load_goals_from_file():
    if g.get('boosted_until'):
        print(f'{g[\"id\"]}: priority={g[\"priority\"]}, boosted_until={g[\"boosted_until\"]}')
"
```