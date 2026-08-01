---
name: skill_usage_analyzer
description: "Analyzes skill usage patterns from feedback_store and logs, identifies why skills are unused, routes to appropriate action system (Suggestion Applier, Crystal, Knowledge Cube, Proactive Doer)."
trigger: "On schedule (daily), or when maintenance_scanner detects unused skills > 14 days"
usage: skill_usage_analyzer
category: self-improvement
---

# Skill Usage Analyzer

Analyzes why skills are not used and routes to appropriate action system. No reports — only actions.

## Core Logic

**Data Sources:**
- `feedback_store.db` — skill usage logs (timestamp, skill, context)
- `improvement_suggestions.json` — generated suggestions
- `.claude/skills/` directory structure — skill metadata

**Threshold:** Skill considered "unused" if no feedback record in last 14 days.

## Root Cause Analysis Priority

| Priority | Cause | Routed To | Action |
|----------|-------|-----------|--------|
| 1 | Broken dependencies | Proactive Doer | Fix deps, restart |
| 2 | No triggers defined | Suggestion Applier | Add event triggers |
| 3 | Not in CLAUDE.md/AGENTS.md | Suggestion Applier | Register skill |
| 4 | Duplicates another skill | Crystal | Merge/delete |
| 5 | No examples/docs | Suggestion Applier | Add examples |
| 6 | Task model shifted | Knowledge Cube | Reassess relevance |

## Integration Points

| System | Queue File | Trigger |
|--------|------------|---------|
| Suggestion Applier | `cache/suggestion_queue.json` | `register_skill`, `add_trigger`, `add_examples` |
| Crystal | `cache/crystal_tasks.json` | `resolve_duplication` |
| Knowledge Cube | `experiences` table (skill_analysis) | `reassess_relevance` |
| Proactive Doer | `cache/proactive_doer_tasks.json` | `fix_dependencies` |

## Verification

- Syntax: `python -m py_compile scripts/skill_usage_analyzer.py`
- Runtime: `python scripts/skill_usage_analyzer.py --analyze --threshold 14 --json`
- Full cycle: `python scripts/skill_usage_analyzer.py --analyze --execute --threshold 14 --json`

## Cron

```json
{
  "name": "skill-usage-analyzer",
  "script": "skill_usage_analyzer.py",
  "schedule": "0 5 * * *",  // Daily 05:00
  "enabled": true
}
```

## Files

- `scripts/skill_usage_analyzer.py` — Main analyzer
- `scripts/suggestion_applier.py` — Applies fixes from queue
- `cache/suggestion_queue.json` — Queue for Suggestion Applier
- `cache/crystal_tasks.json` — Queue for Crystal
- `cache/proactive_doer_tasks.json` — Queue for Proactive Doer

## Key Fixes (2026-07-31)

- **999 days logic fixed**: Now `days_unused = 0` if used <14 days, `999` only if NO feedback record exists
- **Nested payload extraction**: Fixed `payload.payload.action` access in Suggestion Applier
- **Applied log corruption handling**: `load_applied()` handles both list and dict formats
- **Verification logging**: All skill registrations verified by subagent_verifier