# Crystal.py Audit — 2026-06-13

## Current Architecture (unified crystal.py, ~1893 lines)

```
observe()    → snapshot KC/EE/FL/Fabric (lines 34-204)
diagnose()   → tensions, insights (lines 211-299)
forecast()   → growth predictions (lines 306-335)
horizon()    → evolutionary phase (lines 337-436)
will()       → DECIDE what to do (lines 533-795)
record()     → save to KC (lines 1718-1765)
render()     → human-readable output (lines 1772-1841)
```

## will() Internal Flow (5 steps)

### Step 0: Self-Understanding (lines 540-542)
- `_load_will_history()` — loads last 50 `source='crystal_will'` from KC
- `_self_reflect(history, snap)` — builds text context (last 10 decisions, repeats, exhausted sources)

### Step 1: Context (lines 544-548)
- `historical_ids` = set of all action_ids from history
- `done_sources` = all historical_ids (filters everything already done)

### Step 2: Predefined Actions (lines 550-586)
| action_id | Condition |
|-----------|-----------|
| `extract_improvement_suggestions` | orphans > 10 AND source not done |
| `extract_dimension_proposals` | orphans > 5 AND source not done |
| `init_fler` | Fler empty AND script exists |

### Step 3: Self-Discovery (lines 588-712)
Only runs if Step 2 produced no candidates.

- **3a**: `_self_discover()` — orphan sources, fabric, agency, clusters, inventory (lines 798-945)
- **3b**: `understand_intents` — if state_db orphans > 20
- **3c**: `refine_intents` — if understand_intents done AND >40% "other"
- **3d**: `recognize_agents` — if extract_agency_agents done AND concepts > 5× agents
- **3e**: `adopt_persona` — if recognize_agents done AND agents > 10
- **3f**: `analyze_architecture` — if adopt_persona done
- **3g**: `_decide_script()` — 6 scripts: cube_feeder, knowledge_gap_filler, cube_categorizer, proactive_doer, cube_to_memory, explore_white_spot
- **3h**: Bridge to autonomous_agent — runs next undone script

### Step 4: Selection (lines 714-736)
- If candidates empty → `_generate_tactical_tasks()`
- Weight: `impact_score / effort_score` (low=1, medium=2, high=3)
- Sort by weight descending, pick `candidates[0]`

### Step 5: Execution (lines 738-795)
Hardcoded routing:
```
extract_* → _execute_extract(source)
init_fler → _execute_init_fler()
understand_intents → _execute_understand_intents()
refine_intents → _execute_refine_intents()
recognize_agents → _execute_recognize_agents()
adopt_persona → _execute_adopt_persona(fl)
analyze_architecture → _execute_analyze_architecture()
script → _execute_script(name, args)
task_for_agent → _write_agent_task(...)
else → fallback (just logs)
```

## _self_discover Candidates (lines 798-945)

| Candidate | Condition | ID |
|-----------|-----------|----|
| Orphan sources | orphan_by_source[src] ≥ 5 AND src not done | `extract_{src}` |
| Fabric | ~/fabric exists AND files > 5 | `extract_fabric` |
| Agency | external/agency-agents exists AND files > 10 | `extract_agency_agents` |
| Clusters | improvement_suggestions patterns | `explore_cluster_{pat}` |
| Isolated agents | (counted but NOT added to discovered — bug) | — |
| Inventory tools | inventory items > 5 | `explore_inventory_tools` |

## _generate_tactical_tasks (lines 1599-1711)

| Task | Condition | Script |
|------|-----------|--------|
| `tactical_categorize` | orphans > 10% | cube_categorizer.py |
| `tactical_expand_domains` | domains < 8 | explore_white_spot.py |
| `tactical_feed` | velocity < 100/day | cube_feeder.py |
| `tactical_analyze_kc` | total > 1000 | (none) |
| `tactical_report_{YYYYMMDD}` | unique by date | (none) |
| `tactical_research` | **FALLBACK — no guard** | (none) |

## CRITICAL BUGS

### Bug 1: tactical_research Infinite Loop
`tactical_research` is a fallback with NO `historical_ids` check. When all other tactical tasks are filtered, it generates every cycle:
```python
if not tactical:
    tactical.append({'id': 'tactical_research', ...})  # NO guard!
```
**Fix required:** Add `'tactical_research' not in historical_ids` check.

### Bug 2: _write_agent_task Dead Bridge
Writes to `cache/crystal_tasks.json` but nothing reads it:
- No polling mechanism
- No file watcher
- No cron trigger
- Tasks accumulate forever, never executed

### Bug 3: Execution Block Hardcoding
10+ `elif` branches for each action_id. Every new action requires code change. Not scalable.

### Bug 4: isolated_agents Not Added
`_self_discover` counts isolated agents but never adds a candidate for them. Variable `isolated` is computed but unused.

## Why It Repeats

```
Step 2: all extract_* done → candidates empty
Step 3: all candidates in historical_ids → candidates empty
Step 4: candidates empty → _generate_tactical_tasks()
  → tactical_categorize: condition not met
  → tactical_research: NO GUARD → generates every time
  → _write_agent_task: writes JSON → nobody reads
→ Next cycle: same thing
```

## will_history Content (20+ action_ids)
All previously executed actions are in `historical_ids`, blocking re-selection. The only escape is `tactical_research` which has no guard.
