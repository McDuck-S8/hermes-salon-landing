# Self-Improvement Pipeline: Event-Driven Architecture (2026-07-18)

## User Constraint (CRITICAL)
User: "Стоп. Никакого cron. Ты знаешь как делать по событиям."
Self-improvement pipeline must be FULLY event-driven. No cron jobs.

## Architecture
```
self_improvement_loop.main()
  ├── analyze_error_patterns()
  ├── identify_recurring_fixes()
  ├── generate_suggestions()
  ├── auto_create_skills()           ← from recurring patterns (count>=3)
  ├── create_skills_from_suggestions() ← from suggestions (critical+high) [NEW]
  ├── write_knowledge_to_cube()
  ├── store_suggestions()
  ├── emit("new_suggestions_ready")  ← event
  └── suggestion_consumer.consume()  ← runs in-process, no cron
```

## Three Fixes Applied

### 1. create_skills_from_suggestions() — in main(), not cron
- Takes suggestions list, filters critical+high severity
- Generates SKILL.md with trigger, description, recommended actions
- Writes to `skills/auto-generated/fix-{topic}-skill/SKILL.md`
- Called at end of main() after auto_create_skills()

### 2. suggestion_consumer — event-driven, not cron
- `main()` emits `new_suggestions_ready` event via emit_event
- Consumer called in-process immediately after emit
- Registered in EVENT_JOB_MAP: `new_suggestions_ready → suggestion-consumer`
- Reads improvement_suggestions.json, applies top suggestions

### 3. get_db() — singleton connection
- Module-level `_KC_CONN = None`
- `get_db()` checks liveness via `SELECT 1`, reconnects if stale
- Never closes explicitly — lives for process lifetime
- Prevents connection churn between write_knowledge_to_cube() calls

## Hash Collision Fix
- `write_knowledge_to_cube` used `sha256(text)` for KC hash
- Same text across runs → UNIQUE constraint failure
- Fix: `sha256(text + timestamp)` + `INSERT OR IGNORE`

## Verified Results
- 5 skills created from suggestions in first run
- 0 write errors (was 10 per run)
- Consumer: 2 applied, 1 dup per run
- Per-run skill creation ratio: 20% (5/25)
