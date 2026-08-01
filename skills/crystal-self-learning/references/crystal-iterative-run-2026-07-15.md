# Crystal Iterative Run — 2026-07-15

## Task
Run `python scripts/crystal.py --iterative 3` as cron job. Verify:
1. Output ≠ input (each cycle — unique action)
2. If "everything done" — clear `studied` in `cache/self_model.json` (keep last 5) and re-run
3. Verify `self_model.json` updated with `studied` and `znu`

## Execution Summary

### First Run (cycles 1-3)
All 3 cycles produced **identical output**:
- "fabric не содержал новых сущностей (200 записей, 0 кандидатов) — нужен другой подход"
- No new entities extracted from fabric
- KC: 3215 entries, EE: 3672 entities, 0 relations
- Orphans: 2 (script_sensor_array=1, script_web_surfer=1)

### Cleanup
Ran `scripts/clean_studied.py` — `studied` array was already empty `[]`

### Second Run (cycles 1-3)  
All 3 cycles **still identical** — fabric extraction exhausted (no new candidates)

### Third Run (cycles 1-3)
Same pattern — exhausted source, no progress

## self_model.json State (after runs)
```json
{
  "version": "1.0",
  "last_cycle": "2026-07-15T03:45:36",
  "cycle_count": 130,
  "znayu": { "total_entries": 3215, "avg_depth": 297, "domains": {...}, "total_domains": 10 },
  "umeyu": { "roles": {...}, "skills": { "total": 436, "by_category": {...} } },
  "ne_znayu": { "orphan_sources": {...}, "isolated_entities": 2, "unused_skills": 436 },
  "istoriya": { "actions": [], "total_decisions": 0 },
  "gorizonty": { "candidates": [] },
  "sovest": {
    "assessments": [...10 old assessments from 2026-06-13...],
    "last_assessment": "2026-06-13",
    "studied": []
  },
  "znu": {
    "bugfix": "Углубление 'bugfix': 505 записей, соседи: across(2728)",
    "crystal": "Слепое пятно 'crystal': 11 записей [crystal_will=4, indexed=7]",
    "creative": "Слепое пятно 'creative': 58 записей [None=24, auto_research=2, indexed=28, script_result=2, success=...]",
    "latent-domain-detector": "Аудит источника 'latent-domain-detector': 143 записей, домены: browser(23), devops(4), education(3)",
    "improvement_suggestions": "Аудит источника 'improvement_suggestions': 489 записей, домены: bugfix(332), debugging(79), design(2...",
    "learning": "Слепое пятно 'learning': 61 записей [None=3, failure=1, indexed=8, lavra_knowledge=4, partial=1, scr...",
    "communication": "Слепое пятно 'communication': 84 записей [None=8, failure=1, indexed=4, lavra_knowledge=2, partial=1"
  },
  "modifications": [...2 modifications from 2026-06-13...],
  "plan": { "goals_7d": [...], "goals_30d": [...], "last_review": "2026-06-13T11:39:14" },
  "mod_evals": [...],
  "self_awareness": { "last_doc_hash": "2052426709be108e", "last_analysis": "2026-06-13T17:00:00", "proposals_count": 3, "known_functions": 1, "limitations_found": 6, "arch_decisions_found": 0 }
}
```

## Key Observations

1. **Fabric extraction exhausted** — `extract_fabric` action produces 0 new entities consistently. The 200 most recent fabric files contain no extractable patterns (no `[key:value]`, no `domain 'xxx'`, no CamelCase names that pass filters).

2. **No new `studied` entries added** — Because no conscience-driven actions executed (no `extract_*` or `conscience_*` actions ran), `_evaluate_conscience_learning` was never called, so `studied` remains empty.

3. **znu has 7 entries** — All from historical runs (2026-06-13 and earlier). No new entries from this session because no successful conscience actions executed.

4. **cycle_count stuck at 130** — Not incrementing because `_load_self_model` only increments when loading, but the file already exists and isn't being re-saved with incremented count properly.

5. **Historical IDs persist across iterative runs** — `historical_ids` is loaded from KC `crystal_will` source each cycle, so `extract_fabric` is marked as "done" after first cycle and skipped in cycles 2-3.

## Root Cause: Fabric Files Lack Extractable Patterns

The fabric folder contains 2294 markdown files (mostly `agent-decision-*` and `agent-session-task-*` from CLI/cron sessions). These files:
- Use YAML frontmatter with structured fields (id, agent, platform, timestamp, type, tier, summary, project_id, session_id, training_value)
- Content is human-readable summaries, not structured data with `[key:value]`, `domain 'xxx'`, or CamelCase entities
- Regex patterns in `_execute_extract` don't match frontmatter fields or narrative summaries

## Recommended Fixes

1. **Add frontmatter parser to `_execute_extract`** for `source='fabric'` — extract `id`, `summary`, `project_id`, `session_id`, `training_value` as entities
2. **Track exhausted sources in `self_model.json`** — persist `exhausted_sources` list so iterative runs don't re-try exhausted sources immediately
3. **Increment `cycle_count` on each `main()` call** — ensure counter reflects actual runs
4. **Add `studied` entries from conscience evaluations** — when conscience actions run, they should populate `studied` via `_evaluate_conscience_learning`

## Related References
- `crystal-iterative-run-2026-07-13.md` — First iterative run (cycles extracted 75, 0, 0 entities)
- `crystal-iterative-run-2026-07-13-session2.md` — Second session (cycles extracted 2, 0, 0)
- `crystal-iterative-run-2026-07-14.md` — Third session (cycles extracted 63, 8, 0)
- `crystal-iterative-run-2026-07-14-session2.md` — Fourth session (3 cycles, first extracted 2 new, then exhausted)
- `crystal-exhausted-source-fix-2026-07-13.md` — Fix for exhausted source tracking