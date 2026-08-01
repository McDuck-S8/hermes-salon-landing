# Knowledge Cube — 8-Angle Schema Reference

## experiences table (4583 rows, 11MB)

| Field | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| ts | TEXT | ISO timestamp |
| content | TEXT | Experience text |
| raw_text | TEXT | Original text |
| hash | TEXT UNIQUE | SHA256(content+timestamp)[:16] |
| axis_time_hour | INTEGER | 0-23 |
| axis_time_dow | INTEGER | 0=Mon |
| axis_domain | TEXT | bugfix/skill/creative/communication/... |
| axis_outcome | TEXT | failure/success/unknown/indexed |
| **dynamic_axes** | TEXT | **JSON with 8 angles** (see below) |
| is_white_spot | INTEGER | 0/1 |
| white_spot_cluster_id | TEXT | |
| source | TEXT | Origin: self_improvement_loop, rss_*, script_*, user_voice |
| confidence | REAL | |
| tags | TEXT | JSON array |
| importance | REAL | 0-10 |
| expiration_date | TEXT | |
| verification_method | TEXT | |

## 8 Angles in dynamic_axes

```json
{
  "essence": "error_fix|pattern|user_feedback|research|skill_usage|skill_failure|architecture|metric|decision|lesson",
  "origin": "self_improvement_loop|user_voice|rss_hackernews|...",
  "temporal": "during_task|post_session|scheduled_scan|real_time",
  "confidence": "verified|pattern|observed|speculated|user_confirmed",
  "value": "critical|high|medium|low|noise",
  "applicability": "now|needs_context|reference|future|expired",
  "action": "apply_fix|create_skill|update_doc|investigate|alert_user|ignore|record_only",
  "related": []
}
```

## Data Distribution (post-backfill 2026-07-18)

By essence: error_fix=2982, skill_usage=650, pattern=522, research=234, metric=90, decision=58, lesson=31, architecture=13
By confidence: speculated=4578, verified=2
By value: medium=4456, critical=68, high=52, low=4
By action: apply_fix=2392, record_only=1289, create_skill=737, update_doc=73, investigate=67, ignore=13, alert_user=9

## Other Tables

- dimensions (5): time_hour, time_dow, domain, outcome, error_category
- white_spot_clusters (45): pending=20, researched=23, developing=2
- kc_entries (419): tools=211, issues=70, external=60, finance=10
- kc_events (3)
- knowledge_cube_fts (4583): FTS5 fulltext

## verified_fixes.db (55 rows, 112KB)

| Field | Type |
|---|---|
| id | INTEGER PK |
| issue_hash | TEXT UNIQUE |
| issue_type | command/domain_failure_pattern/log_tool_error |
| fix_type | guard/fix/investigation/knowledge/error_fix |
| target_file | TEXT |
| created_at | TEXT |
| verified_at | TEXT |
