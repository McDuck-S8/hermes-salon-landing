# Knowledge Cube + Crystal — Real Architecture (2026-07-18)

## knowledge_cube.db (11 MB)

### experiences (4567 rows) — main table
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | autoincrement |
| ts | TEXT NOT NULL | timestamp |
| content | TEXT NOT NULL | experience text |
| raw_text | TEXT NOT NULL | original text |
| hash | TEXT UNIQUE NOT NULL | SHA256[:16], dedup key |
| axis_time_hour | INTEGER | 0-23 |
| axis_time_dow | INTEGER | 0=Mon |
| axis_domain | TEXT | bugfix/skill/creative/communication/debugging/... |
| axis_outcome | TEXT | failure/success/unknown/indexed/neutral |
| dynamic_axes | TEXT | JSON {} |
| is_white_spot | INTEGER | 1=white spot |
| white_spot_cluster_id | TEXT | FK to clusters |
| source | TEXT | improvement_suggestions/skill-indexer/rss_*/script_*/... |
| confidence | REAL | 0-1 |
| tags | TEXT | JSON array |
| importance | REAL | 0-10 |
| expiration_date | TEXT | |
| verification_method | TEXT | manual/auto |

### dimensions (5 rows) — coordinate axes
- time_hour, time_dow, domain, outcome (base)
- error_category (auto_cluster)

### white_spot_clusters (45 rows)
- pending=20, researched=23, developing=2

### kc_entries (419 rows) — secondary table
- tools=211, issues=70, external=60, finance=10, social-media=9

### Data distribution
- Domains: bugfix=1624, skill=787, debugging=461, creative=366, communication=309
- Outcomes: failure=2838, indexed=796, unknown=537, success=260
- Sources: improvement_suggestions=2467, skill-indexer=796, white-spot-explorer=157

## verified_fixes.db (112 KB)
- verified_fixes: 55 rows
- issue_hash (TEXT UNIQUE) — SHA256 dedup
- issue_type: command=42, domain_failure_pattern=7, log_tool_error=3
- fix_type: command=40, investigation=7, guard=5

## events.db (3 MB)
- events: 8860 rows (event_type, timestamp, data, processed)
- triggers: 6 rules (task_complete→capture_knowledge, error_occurred→capture_investigation, ...)

## event_bus.json (877 KB)
- pending: 1199 items, stats: 23 event types

## Crystal (crystal.py, 3177 lines)
NOT a table. Python script — 4-phase consciousness cycle:
1. observe() — snapshot all 4 cubes (KC + entity_engine + fler_engine + fabric)
2. diagnose(snap) — what's broken, growing, dying
3. will(snap, diag) — what actions to take
4. record(...) — write back to KC

Reads: knowledge_cube.db, entity_engine.db, fler_engine.db, fabric/
Writes: knowledge_cube.db (decisions, self-modifications)

Crystal skills (20 dirs under skills/crystal*) — auto-evolved from KC domain groups.
crystal (800 entries), crystal_will (598 entries), etc.

## Flow
hooks.py → event_evolution → verified_fixes.db
self_improvement_loop → suggestions → create_skills_from_suggestions → skills/
self_improvement_loop → emit(new_suggestions_ready) → suggestion_consumer → verified_fixes.db + KC
crystal.py → observe KC → diagnose → will → record KC (closed loop)
