# Event-Driven Ripple Engine Pattern

**Date:** 2026-07-23
**Session:** User corrected cron-based approach → replaced with event-driven

## Problem

Ripple Engine (morning report generator) was running on cron (every 15 min). User said:
> "Не нужно ждать ни 15 минут, ни тем более cron. Отчёт должен генерироваться не по таймеру, а по событию."

The user's analogy: a driver who watches the flight arrivals board, not his watch. "Самолёт приземлился → он уже у выхода."

## Solution

Remove cron. Hook into existing event_beat() calls:

1. **`knowledge_added`** (fired by kc_rag.upsert(), cube_feeder, hermes_hooks)  
   → `ripple_consumer.on_knowledge_added()` — accumulator with threshold=3
   - After 3 events → runs morning_report.py → saves cache
   
2. **`new_suggestions_ready`** (fired by self_improvement_loop.main())  
   → `ripple_consumer.on_suggestions_ready()` — always triggers report

## Architecture

```
DATA ENTRY POINT            EVENT                     RIPPLE CONSUMER
─────────────────    ──────────────────    ──────────────────────────────
kc_rag.upsert()  ──► knowledge_added  ──► on_knowledge_added() [cnt: 1→2→3]
cube_feeder.py   ──► knowledge_added  ──►   ↓ when count >= 3
hermes_hooks     ──► knowledge_added  ──► morning_report.py → cache JSON
                                           ↓ also beats events to keep
                                             heartbeat alive

self_improvement  ──► new_suggestions  ──► on_suggestions_ready() [always]
loop.main()                                  ↓
                                           morning_report.py → cache JSON
```

## Cache files

- `cache/latest_morning_report.json` — always the latest report, machine-readable
- `cache/ripple_trigger.json` — trigger state (pending_count, last_generated)

## Key design decisions

1. **No cron. No timers anywhere.** Events fire only when data mutates. If nothing happens, system sleeps. That's correct.
2. **Threshold=3 for knowledge_added.** Prevents report regeneration on every single entry. After 3 new entries, report updates.
3. **Suggestions always trigger.** New suggestions are high-signal events. Report regenerates immediately.
4. **Heartbeat beating.** When ripple_consumer generates a report, it also beats `knowledge_added` + `new_suggestions_ready` events to keep the heartbeat system alive.
5. **Cache-first at boot.** auto_boot_scan reads `latest_morning_report.json`. Never runs analysis. If cache >1h stale without recent events, runs one-shot update.

## Files

- `scripts/ripple_consumer.py` — event-driven report trigger
- `scripts/morning_report.py` — report generator (called by consumer)
- `scripts/auto_boot_scan.py` — reads cache at boot
- `cache/latest_morning_report.json` — latest report
- `cache/ripple_trigger.json` — trigger state

## Wiring

Event hooks added to:
- `scripts/kc_rag.py:244` — after event_beat("knowledge_added")
- `scripts/self_improvement_loop.py:966` — after event_beat("new_suggestions_ready")
- `scripts/cube_feeder.py:555,734` — after event_beat("knowledge_added")
- `scripts/hermes_hooks.py:89` — after event_beat("knowledge_added")
