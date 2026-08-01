---
name: event-driven-self-improvement-pipeline
description: "Self-improvement pipeline: event-driven, no cron. Loop → suggestions → skills → consumer. Singleton KC connection."
trigger: When setting up or fixing the self-improvement pipeline
---

# Event-Driven Self-Improvement Pipeline

## Architecture

```
self_improvement_loop.main()
  ├── analyze_error_patterns()    → recurring clusters
  ├── generate_suggestions()      → improvement_suggestions.json
  ├── auto_create_skills()        → from recurring patterns (count >= 3)
  ├── create_skills_from_suggestions() → from critical/high suggestions
  ├── write_knowledge_to_cube()   → KC experiences (INSERT OR IGNORE + ts in hash)
  ├── emit("new_suggestions_ready")
  └── suggestion_consumer.consume()  → applies code fixes, writes verified_fixes.db + KC
```

## Key Rules
- **NO CRON** — everything triggers on events/completions
- `create_skills_from_suggestions()` called at END of each loop cycle
- Consumer called in-process immediately after `new_suggestions_ready` event
- Event also registered in `EVENT_JOB_MAP` for event_bus tracking

## knowledge_cube.get_db() — Singleton Pattern
```python
_KC_CONN = None
def get_db():
    global _KC_CONN
    if _KC_CONN is not None:
        try: _KC_CONN.execute("SELECT 1"); return _KC_CONN
        except: _KC_CONN = None
    _KC_CONN = sqlite3.connect(str(DB_PATH), timeout=10)
    # ... schema init ...
    return _KC_CONN
```
Never close. Process-lifetime connection. WAL + busy_timeout=5000.

## KC Write Hash Collision Fix
```python
h = hashlib.sha256((text + timestamp).encode("utf-8")).hexdigest()[:16]
# INSERT OR IGNORE — same text at different times gets unique hash
```

## verified_fixes.db Schema
```sql
CREATE TABLE verified_fixes (
    issue_hash TEXT UNIQUE NOT NULL,
    issue_type TEXT, issue_description TEXT,
    fix_type TEXT, fix_description TEXT, fix_content TEXT,
    target_file TEXT, evidence TEXT, tags TEXT,
    embedding TEXT, created_at TEXT, verified_at TEXT
);
```
Dedup via `issue_hash` (SHA256 of fix text). INSERT OR IGNORE.

## 8-Angle dynamic_axes Schema (kc_axes.py)

Every KC experience MUST have structured `dynamic_axes` with these 8 fields:

| Angle | Field | Values |
|---|---|---|
| Суть | `essence` | error_fix, pattern, user_feedback, research, skill_usage, skill_failure, architecture, metric, decision, lesson |
| Источник | `origin` | structured source string (script name, RSS feed, user_voice) |
| Время | `temporal` | during_task, post_session, scheduled_scan, real_time |
| Уверенность | `confidence` | verified (5+), pattern (3+), observed (2), speculated (1), user_confirmed |
| Ценность | `value` | critical, high, medium, low, noise |
| Применимость | `applicability` | now, needs_context, reference, future, expired |
| Действие | `action` | apply_fix, create_skill, update_doc, investigate, alert_user, ignore, record_only |
| Связи | `related` | list of IDs/hashes this connects to |

**Auto-classifier:** `kc_axes.auto_build_axes(text, source, count)` → fills all 8 from text content + source + recurrence count.
**Backfill:** `kc_axes.backfill_axes(text, source, existing)` → merges new angles into existing data without overwriting.
**Write path:** `add_experience()` and `write_knowledge_to_cube()` both auto-fill 8 angles when none provided.
**NO conn.close()** in write functions — kills singleton.

## Files
- `scripts/self_improvement_loop.py` — main loop + create_skills_from_suggestions
- `scripts/suggestion_consumer.py` — event-driven consumer
- `scripts/knowledge_cube.py` — singleton get_db()
- `scripts/event_bus.py` — EVENT_JOB_MAP with new_suggestions_ready
- `cache/verified_fixes.db`, `cache/knowledge_cube.db`, `cache/consumer_state.json`

## NO CRON — User Directive
"Стоп. Никакого cron. Ты знаешь как делать по событиям." — pipeline is event-driven ONLY.
Loop emits `new_suggestions_ready` → consumer runs in-process. Never schedule as cron.

## Autonomous Heartbeat Pattern (2026-07-30) — Updated

The `self_improvement_loop.py` cron job (0 5 * * *) is a **no_agent** cron that runs daily at 5 AM. It must fire its own heartbeat at the start of `main()`:

```python
def main():
    # Heartbeat: module alive — MUST be first line of main()
    try:
        from chain_heartbeat import beat
        beat("self_improvement_loop")
    except ImportError:
        pass
    
    # ... rest of the loop ...
    
    # At end, fires event_beat("new_suggestions_ready")
```

**Key Updates (v2.0 — 2026-07-30):**

- **Self-improvement loop now fires `event_beat("new_suggestions_ready")` at completion** — integrates with chain-heartbeat
- **Anti-pattern detection**: ≥3 same issue_type = "stop and refactor" investigation (not patch)
- **Auto-skill creation**: patterns ≥2 occurrences create skills in `skills/auto-generated/`
- **Knowledge Cube integration**: writes verified patterns to KC when count ≥3
- **Metrics tracking**: cumulative runs, suggestions, skills created, knowledge entries
- **Produced 2272 suggestions in latest run**: 14 critical, 7 high, 2246 medium, 1 low
- **Top anti-patterns detected**: `command` (93 fixes), `domain_failure_pattern` (7), `log_tool_error` (4), `log_unknown` (4)
- **Cron integration**: daily 05:00 no_agent cron now fires `beat("self_improvement_loop")` at start of main()

This ensures the `self_improvement_loop` module stays HEALTHY in chain_heartbeat between daily runs. The module is part of the `self_improvement_pipeline` (Level 3).

## Show Real Data, Not Reports — User Directive
"Не отчёты — схему. Я хочу видеть что у тебя там на самом деле." — user explicitly rejects:
- Summary tables with nice formatting
- Conversion percentages without context
- Reports that hide the real state

Instead: show actual DB schemas (PRAGMA table_info), actual row counts (SELECT COUNT), actual data distributions (GROUP BY), actual file sizes. The user is an engineer who understands the codebase. Show them the truth, not a dashboard.

## Pitfalls
- `_get_existing_skills()` scans 2 levels deep under skills/ — auto-generated/ is one category
- `auto_create_skills` needs count >= 3 from recurring fixes — won't create from suggestions
- Consumer dedup is by hash, not by text — same suggestion processed twice = dedup
- **Duplicate auto-skill creation** — `auto_create_skills()` / `create_skills_from_suggestions()` loop over many clusters with the SAME error_type (e.g. 30× `log-unknown`). Without updating the seen-set inside the loop you create 30+ identical skill dirs in one run. Fix: `existing_skills.add(name)` immediately after each successful creation, so the next cluster with the same name is skipped. 44 "created" skills that are really ~6 unique dirs = this bug.
- **Auto-skills must go to `skills/auto-generated/`, NOT root `skills/`** — per skills/AGENTS.md, root is curated. Root gets cluttered with `*-auto-skill` junk that duplicates the archived ones. Point `SKILLS_DIR` at `skills/auto-generated/` (it already exists as a category) and delete stray auto-skill dirs from root when found.
- **KC `experiences` INSERT requires `content` AND `hash` NOT NULL** — INSERTing only `raw_text, axis_domain, axis_outcome, tags, source, ts, is_white_spot` fails silently with `IntegrityError` caught by `except: pass` → "Wrote 0 knowledge entries" with no error. Schema: `content` mirrors raw_text, `hash` = `md5(f"{text}_{now}")[:16]` (pattern from kc_feeder.py). ALWAYS `PRAGMA table_info(experiences)` before first INSERT and fill every NOT NULL column.
- **`emit_event.emit("new_suggestions_ready")` ≠ `event_beat("new_suggestions_ready")`** — emit writes to `cache/event_bus.json` (action triggers); event_beat updates chain_heartbeat health state. The loop needs BOTH at completion or the event shows SILENT in `system_status()`. Same for `knowledge_added` after write_knowledge_to_cube.
- **`conn.close()` kills the singleton** — if write_knowledge_to_cube calls conn.close(), all subsequent writes go to a fresh empty connection. Data appears to write (no error) but never reaches disk. KC showed "4520 loaded" but DB had 0 rows. NEVER close a singleton connection.
- **Schema drift is silent** — verified_fixes.db was rebuilt with new schema (issue_hash, no source column) while code used old columns. Every INSERT failed silently via `except: pass`. ALWAYS `PRAGMA table_info(table)` before first INSERT in a session.
- **`except: pass` hides everything** — silent DB errors meant schema mismatch went undetected for days. At minimum print the error.
- **Hash collision blocks INSERT** — deterministic hash on identical text hits UNIQUE constraint. Fix: `INSERT OR IGNORE` + include timestamp in hash.
- **Backfilling live DB** — When adding new structured fields (like 8-angle dynamic_axes), use `auto_build_axes()` with existing text+source to generate new structure. Don't overwrite existing meaningful values — merge. Run `UPDATE ... SET dynamic_axes = ? WHERE dynamic_axes NOT LIKE '%essence%'` for targeted backfill. Verify with `SELECT COUNT(*) ... WHERE dynamic_axes LIKE '%essence%'` = total.
- **Crystal reads 4 DBs but NOT user messages** — state_db has 0 entries. Crystal is blind to user feedback. When wiring user reactions, write to KC with `source='user_voice'` or `source='user_correction'` so Crystal can see them via orphan_sources.
