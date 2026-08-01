# Session 2026-07-12 — Timer-to-Event Conversions

## What Broke
- `event_evolution.py` had 4h cooldown on `capture_knowledge` → events queued but never processed (31 pending)
- `agent_daemon.py` had 5-min timer loop + redundant 30s timer → ran agent on timers, not events
- `reality_gate.py` read `kc_entries` table (3 rows) instead of `experiences` (2605) → KC health showed 3 entries
- `hermes_health.py` was a SyntaxError stub (docstring + import on same line)

## Fixes Applied

### 1. event_evolution.py — Remove cooldown completely
```diff
- ("task_complete", "capture_knowledge", 4),  # 4h cooldown
+ ("task_complete", "capture_knowledge", 1),  # 1h (then removed entirely)
```
Ultimately removed `should_trigger` cooldown check entirely — every event fires all matching triggers immediately.

### 2. agent_daemon.py — Restore file watcher with debounce
Three versions in this session:
1. **Original**: file watcher + 5-min timer + 30s timer — noisy, mixed modes
2. **First fix**: file watcher deleted entirely, kept 5-min timer — half-assed (user: "так же наотъебись!!!")
3. **Final fix**: restored watchdog, 30s debounce, no timer, polling only at 30-min silence

Key pattern:
```python
# Event-driven (primary)
if file_events:
    while file_events:  # drain all, keep latest
        last_ts = file_events.pop(0)
    if now - last_ts < 30:  # 30s debounce
        time.sleep(2); continue
    run_agent()

# Polling fallback (safety net only)
if run_count % 360 == 0 and now - last_event_run > 300:  # 30 min, only if no events
    run_agent()
```

### 3. reality_gate.py — Wrong table name
```sql
-- BROKEN: queried legacy table with 3 rows
SELECT COUNT(*) FROM kc_entries
-- FIXED: queried real table
SELECT COUNT(*) FROM experiences
```

### 4. hermes_health.py — Broken stub → working wrapper
Before: `"""Hermes health check stub.""" import sys; sys.exit(0)` (SyntaxError)
After: imports `gate()` from reality_gate, prints JSON or human-readable

## Lessons
- **Delete = half-assed.** When a feature emits noise, don't kill it — fix the noise source and re-enable.
- **Event-driven means NO cooldowns.** Cooldowns are just timers by another name. Every event fires immediately.
- **Health checks must verify their queries.** If a check says "3 entries" and the DB has 7MB, the query is wrong, not the DB.
- **Always verify by running the actual check** after a fix — don't just assert "it must be right now".
