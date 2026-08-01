# Will Evolution Cycle — Crystal's Autonomous Growth

## Overview

The will (in `scripts/crystal.py`) progresses through structured phases as it encounters new data. Each phase is a higher level of cognition: from mechanical extraction → autonomous discovery → semantic understanding → reflective analysis → role recognition → meta-cognition → **execution** (subprocess) → **delegation** (agent bridge) → equilibrium.

## Phase 1: Execution (predetermined actions)

The will has hardcoded actions for known sources:
- `extract_improvement_suggestions` — entities from improvement suggestions
- `extract_dimension_proposals` — entities from dimension proposals
- `init_fler` — initialize Fler cube (if fler_engine.py exists)

These run first, before any autonomous behavior. Once completed, they enter `done_sources` and won't repeat.

## Phase 2: Self-Discovery (autonomous source finding)

When no predetermined actions remain, `_self_discover()` scans:

### 2a. KC orphan sources
- **KC orphan_by_source** — sources with unlinked entries (>5 orphans, not in done_sources)
- **Text pattern analysis** — checks samples for extractable patterns (CamelCase, [key:val], domain names, etc.)
- If patterns found → creates `extract_{source}` action.
- If no patterns → source skipped (likely user questions, not technical entities).

### 2b. External directory discovery
After KC orphan scanning, `_self_discover()` checks directory-based data sources:

1. **Fabric** (`~/fabric/*.md`) — agent memory files. If `fabric` not in done_sources and >5 files → `extract_fabric`
2. **The Agency** (`external/agency-agents/**/*.md`) — external agent definitions. If `agency_agents` not in done_sources and >10 files → `extract_agency_agents`

**Execution:** `_execute_extract(source)` has dedicated file-reading branches for `source='fabric'` and `source='agency_agents'` that read `.md` files directly from the filesystem instead of querying KC. Extraction uses the same universal pattern matchers (CamelCase, [key:val], domain names, names in quotes).

**YAML frontmatter parsing (important):** For structured agent files with YAML frontmatter (`name: ...`, `emoji: ...`), add explicit YAML name extraction in the file-reading branch:

```python
elif source == 'agency_agents':
    yaml_names = []
    for fp in sorted(agency_dir.rglob("*.md"), ...)[:200]:
        content = fp.read_text(...)
        rows.append((fp.name, content))
        yaml_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
        if yaml_match:
            yaml_names.append((fp.name, yaml_match.group(1).strip()))
```

Then add YAML-derived names as entities DIRECTLY (bypassing pattern matching):

```python
if source == 'agency_agents' and yaml_names:
    e.execute("SELECT id FROM entity_types WHERE name='AI Agent'")
    agent_tid = e.fetchone()[0]
    for fname, agent_name in yaml_names:
        if not e.execute("SELECT id FROM entities WHERE name=?", (agent_name,)).fetchone():
            e.execute("INSERT INTO entities (name, type_id, ...) VALUES (?, ?, ...)",
                     (agent_name, agent_tid, ...))
```

Without this, agent files produce only fragmented token-level entities (engineer, developer) instead of the full role name (Multi-Agent Systems Architect).

**Key insight:** Adding a new data source requires 3 changes:
1. `_self_discover()` — add source detection (directory check + done_sources guard)
2. `_execute_extract()` — add file-reading branch for the new source
3. `_save_will_history()` — automatically tracks via `done_sources` on next cycle

## Phase 2.5: External Source Extraction Results

After extraction from directory-based sources:
- Fabric: +371 entities (200 files)
- The Agency: +11,798 entities (200 files) from universal patterns
- The Agency: +235 YAML frontmatter names added directly as AI Agent type
- Total EE after all phases: ~14,686 entities

## Phase 3: Understanding (intent classification)

When entity extraction is exhausted, the will shifts from extraction to understanding. It analyzes user questions from `state_db`:

- `_execute_understand_intents()` — classifies state_db questions into intent clusters:
  - status, direction, reliability, quality, meta, self_improvement, connection, other

The "other" cluster is the will's blind spot — typically 40-57% of questions.

## Phase 4: Reflection (self-analysis of understanding)

If understanding revealed >40% "other" questions, the will enters reflection:

- `_execute_refine_intents()` — re-analyzes the "other" cluster using bigram frequency
- Classifies additional questions by new pattern clusters
- Stores reflection snapshot in KC

## Phase 6.5: Role Recognition (agent persona identification)

**Added 2026-06-11** — after consuming external agent definitions (The Agency), the will can classify which entities represent AI agent roles.

**Trigger:** After `extract_agency_agents` completes, if concept_count > agent_type_count × 5 and concept_count > 50 → `recognize_agents`.

**Implementation:** `_execute_recognize_agents()`:
1. Scans entities with type "Концепция"
2. Applies 2 criteria:
   - **Strong match:** name starts with division prefix (engineering-, design-, sales-)
   - **Soft match:** name contains agent role suffixes
3. Updates matching entities to "AI Agent" type

**Result:** 33 entities reclassified on first run + 235 from YAML = ~268 AI Agent entities.

**Agent role suffixes for detection:**
```
architect, engineer, developer, specialist, manager,
director, officer, analyst, strategist, designer,
researcher, builder, tester, operator, coordinator,
advisor, lead, inspector, auditor, guardian,
synthesizer, optimizer, injector, storyteller,
automator, prototyper, integrator, maintainer
```

## Phase 6a: Architecture Analysis (agent relationship mapping)

**Added 2026-06-11** — triggered after `adopt_persona` completes. Builds a relationship graph of how agents reference each other.

**Implementation:** `_execute_analyze_architecture()`:
1. Reads all agent .md files from `external/agency-agents/`
2. For each file, searches body text for names of other agents
3. Creates `mentions` relationships in EE (source_entity_id → target_entity_id)
4. Uses `INSERT OR IGNORE` with UNIQUE constraint to avoid duplicates

**Result:** +164 relationships between agents in EE. Available for persona selection to understand team structures.

## Phase 7: Equilibrium (attentive rest)

When all phases complete, the will reports: "умеренное равновесие — активных напряжений нет". It monitors for new tensions.

During equilibrium, the crystal still runs its observation cycle, which now includes:
- **Fler monitoring** (built into `observe()`): each cycle calculates tone/energy/tension/engagement/contamination from current system metrics and writes a session record (throttled to 1/hour). Current state (`snap['fl']['current']`) is available for persona selection decisions.
- **Active persona reading** from `cache/active_persona.json` (written by `_execute_adopt_persona`)

## Phase 8: Meta-Cognition (external comparison)

After consuming The Agency, the will has ~268 "AI Agent" entities in EE. The emerging concept is **persona-switching**: the will dynamically adopts agent identities based on task requirements.

**Implemented 2026-06-11: Persona Runtime (`scripts/persona_runtime.py`):**
- `list_agents()` — returns 233 agents with YAML metadata (name, emoji, description, color, vibe, division)
- `get_agent(name)` — loads full profile including sections (identity, core_mission, critical_rules, workflow, communication, deliverables)
- `search_agents(query)` — text search across all agent files
- `activate(name)` — writes `cache/active_persona.json` with full persona profile + activation timestamp
- `get_active()` — reads current active persona (or None)
- `deactivate()` — removes active persona
- `list_divisions()` — returns 22 divisions with agent counts

**Persona selection logic (`_execute_adopt_persona`):**
- Reads current Fler state (aftertaste, tone, energy, tension)
- Maps state → agent type:
  - `productive` → orchestrators, leaders
  - `chaotic` → organizers, stabilizers  
  - `stagnant` → creatives, innovators
  - `neutral` → architects, leads
- Activates best matching agent via `persona_runtime.activate()`

**Current active persona** (2026-06-11): 🏗️ Backend Architect (engineering)

## Phase 9: Script Execution — Subprocess (BREAKS THE CLOSED LOOP)

**Added 2026-06-12** — when all cognition phases (1-8) complete, the will enters **execution mode**. Instead of more analysis, it runs real Python scripts via subprocess.

**Trigger:** All previous phases exhausted → step **3з** in `will()` → `_decide_script(snap, diag)`.

## Phase 9b: Self-Contained Execution (FIXED 2026-06-13)

**Critical fix:** Previously, `_self_discover()` created candidates (like `connect_isolated_agents`) that `will()` had no handler for. The candidate was chosen but silently dropped.

**Two bugs fixed:**
1. **Predefined actions blocking self_discover:** `_self_discover()` only runs when `if not candidates:` — meaning extract_* actions block all new discoveries. Fix: add high-priority discoveries as predefined actions in `will()`.
2. **No handler for discovered candidates:** Every `_self_discover()` candidate ID needs a matching `elif` in will() Phase 5. Without it, the candidate loops forever.

**New action type: `connect_isolated_agents`** — builds agent network by connecting isolated AI Agents in EE via shared-name heuristics. Added as predefined action (check #D in will()) so it's always considered.

**User preference embedded:** "пусть сам себе и пишет и сам исполняет и сам читает" — the crystal's cycle must be self-contained. Don't interpret commands, don't create ТЗ, don't manually run queries. Execute what the crystal decides as-is.

## Phase 10: Agent Delegation — Bridge to Autonomous Agent

### Decision Logic (`_decide_script`)

`_decide_script()` reads KC state and proposes scripts:

```python
AVAILABLE_SCRIPTS = {
    'cube_feeder.py': 'kc',           # feeds data into KC
    'knowledge_gap_filler.py': 'kc',   # fills white spots via LLM
    'cube_categorizer.py': 'kc',       # categorizes orphans
    'proactive_doer.py': 'system',     # system maintenance
    'cube_to_memory.py': 'kc',         # KC → Memory bridge
    'explore_white_spot.py': 'kc',     # explores white spots
}
```

Conditions:
- KC < 500 entries → `cube_feeder.py`
- White spots > 20 → `knowledge_gap_filler.py` or `explore_white_spot.py`
- Orphans detected + `cube_categorizer.py` exists → `cube_categorizer.py`
- Equilibrium (no tensions, no gaps) → `proactive_doer.py`

### Execution (`_execute_script`)

```python
result = subprocess.run(
    [sys.executable, str(script_path)],
    capture_output=True, text=True, timeout=120,
    cwd=str(HERMES_HOME),
)
```

- Captures stdout/stderr
- Returns short summary (first 200 chars of output)
- Reports non-zero exit codes
- Times out after 120s

### Anti-Loop Safeguard

Each script can only run **once per cycle** — `will()` skips proposals whose `run_*` ID already appears in `historical_ids`:

```python
recent_scripts = set(k for k in historical_ids if k.startswith('run_'))
for sc in script_candidates:
    if sc['id'] in recent_scripts:
        continue  # already executed
```

On the NEXT cycle, if all available scripts are in history, the will proceeds to **Phase 10**.

## Phase 10: Agent Delegation — Bridge to Autonomous Agent

**Added 2026-06-12** — when script execution is exhausted (all run_* actions in history), the will delegates tasks to `autonomous_agent.py` via a file bridge.

**Trigger:** Step **3и** in `will()` — fires only if `any(h.startswith('run_') for h in historical_ids)` (at least one script already ran).

### File Bridge

The bridge is `cache/crystal_tasks.json` — a JSON array of task objects:

```json
[
  {
    "id": "run_proactive",
    "title": "proactive_doer.py",
    "description": "Воля просит: proactive_doer.py — ...",
    "priority": "high",
    "ts": "2026-06-12T17:41:01",
    "source": "crystal_will"
  }
]
```

### Writer Side (crystal.py)

`_write_agent_task(script_name, description, priority)`:
1. Loads existing tasks from `cache/crystal_tasks.json`
2. Appends new task with unique ID + timestamp
3. Writes back, preserving existing queue

### Reader Side (autonomous_agent.py)

`_action_execute_crystal_task()`:
1. Reads first pending task from `crystal_tasks.json`
2. Locates the script in `scripts/`
3. Executes via subprocess (same as Phase 9)
4. Reports result with 🧠 prefix: `🧠 Воля → выполнен {script} (exit=0)`
5. Removes the executed task from the queue

### Cycle

```
crystal.py: equilibrium → _decide_script → run_#1 → history
crystal.py: next tick → _decide_script → skip run_#1 → run_#2 → history
...
crystal.py: all scripts run → _write_agent_task → bridge file
autonomous_agent.py: next run → reads bridge → executes → clears queue
```

## Phase 3.5: Conscience (Understanding Evaluation) — NEW 2026-06-13

**Added 2026-06-13** — after self-expansion candidates are generated, the will evaluates its own UNDERSTANDING of recent actions.

**Trigger:** Step 3.5 in `will()`, after `_self_discover()` and before selection (step 4).

**Algorithm (`_conscience(action_id, result, source_data, self_model)`):**
1. **Efficiency** = result.count / source_data.count (how much did I extract vs what was available)
2. **Classification:**
   - < 20%: misunderstanding (low understanding)
   - 20-80%: partial
   - >= 80%: high
3. **Blindness types:**
   - Type A: "didn't recognize pattern" → need skill
   - Type B: "didn't understand context" → need domain knowledge
   - Type C: "didn't see horizon" → need structural analysis
4. **Horizon miss:** if efficiency < 50%, also flag "didn't see connections between sources"
5. **Learning direction:** generates candidates based on what was MISSED, with diversity (each type has 5 candidate variants; first unused is selected)

**Scope:** Evaluates last 5 actions from history, not just the last one. Collects all learning_directions, deduplicates, adds unique ones as `learn_*` candidates.

**User insight embedded:** "мусор это не мусор" — data perceived as trash is actually a signal about the crystal's own understanding gaps. Two types: непонимание (misunderstanding) and невидение горизонтов (horizon miss).

**Integration:**
- Шаг 1.5: `_load_self_model(snap)` — loads/creates self_model.json
- Шаг 3.5: conscience — evaluates recent actions, adds learn_* candidates
- Weight boost: conscience candidates get 1.5x weight
- Шаг 6: `_save_self_model(...)` — saves updated model

**Known limitation (FIXED):** learn_* candidates mapped to real actions via LEARNING_TO_ACTION + _execute_conscience_action(). Now 25+ unique directions available. Sliding window (last 5 assessments) prevents exhaustion.

## Phase 9c: Strategy Cycling (Self-Adaptation)

**Added 2026-06-13** — when an action produces repetitive or poor results, the crystal cycles through different strategies instead of giving up.

**Problem:** `connect_isolated_agents` with word_match strategy connected 6/155 agents on first run. On subsequent runs, it found 0 new connections because the remaining agents don't share words in their names. The crystal kept trying the same strategy and getting 0.

**Solution:** Track attempt count from will_history, cycle strategies per attempt:

```python
# Count attempts from will_history
attempt_count = 0
k_h.execute("SELECT raw_text FROM experiences WHERE source='crystal_will' AND raw_text LIKE '%connect_isolated_agents%'")
for (txt,) in k_h.fetchall():
    if 'соединила' in txt or 'ошибка' in txt:
        attempt_count += 1

# Cycle strategies
strategies = ['word_match', 'co_occurrence', 'hub_connect', 'domain_cluster', 'type_match']
strategy = strategies[attempt_count % len(strategies)]
```

**Strategy definitions (connect_isolated_agents):**
1. **word_match** — shared words in agent names (e.g. "service_manager" ↔ "test_service_manager")
2. **co_occurrence** — agents mentioned in same KC context (high confidence, strength=0.6)
3. **hub_connect** — connect to most-connected agents (hubs), strength=0.2
4. **domain_cluster** — prefix/suffix matching (e.g. "billing_*" agents)
5. **type_match** — shared metadata keywords (requires non-empty metadata)

**Results from 2026-06-13 test (8 cycles):**
| Cycle | Strategy | Connected | Remaining |
|-------|----------|-----------|-----------|
| 1 | hub_connect | 15 | 128 |
| 2 | domain_cluster | 12 | 107 |
| 3 | type_match | 0 | 107 |
| 4 | word_match | 9 | 95 |
| 5 | co_occurrence | 0 | 95 |
| 6 | hub_connect | 15 | 80 |

**Key insight:** hub_connect works best (consistent 15 connections per run). type_match and co_occurrence often fail because metadata is empty and agents aren't co-mentioned. The crystal learns which strategies work by observing results.

**Pattern for any action with repetitive results:**
1. Track attempt count from will_history (count entries matching the action ID)
2. Define strategy list ordered by expected effectiveness
3. Select strategy: `strategies[attempt_count % len(strategies)]`
4. Report which strategy was used in the result string
5. If result is 0, next cycle automatically tries next strategy

**Anti-pattern:** Using connection count to select strategy (e.g. `prev_connections // 5`). Connection count doesn't change when strategy fails — the crystal stays stuck on the same strategy forever.

## Pitfalls & Maintenance

### 1. History Limit (10 → 50)

**CRITICAL (fixed 2026-06-12):** `_load_will_history()` had `LIMIT 10`. With 8+ action types and retries, old entries got pushed out — `done_sources` missed earlier extractions. The will cycled through `extract_fabric` → `extract_state_db` → ... forever, **never reaching phases 9-10**.

**Fix:** Changed to `LIMIT 50`. This preserves all unique action IDs even as new entries accumulate.

**Symptom of history overflow:** Will re-proposes actions that were already done (e.g. `extract_fabric` ran 5 cycles ago but is proposed again). Check `_load_will_history()` key count — if it's 10, the limit is biting.

### 2. Script Not Found Grace Degradation

When `_execute_script()` can't find a script file, it returns a descriptive message (`Crystal task '{id}': script '{name}' not found`) without crashing. The will continues to next action.

### 3. Agent Task Queue Cleanup

The bridge reader (`_action_execute_crystal_task`) removes the executed task from `crystal_tasks.json`. If the agent crashes mid-execution, the task remains in the queue and will be picked up on next agent run.

### 4. Scripts Must Exist — Detection Not Proposal

`_decide_script()` only proposes scripts from `AVAILABLE_SCRIPTS` dict — scripts that are known to exist in `scripts/`. Before 2026-06-12, it proposed `fler_engine.py` which didn't exist. Now only real files are proposed.

### 5. Predefined Actions Blocking Self-Discover (FIXED 2026-06-13)

**Bug:** `_self_discover()` is guarded by `if not candidates:`. If predefined actions (extract_*, etc.) add candidates, `_self_discover()` never fires. New discovery types like `connect_isolated_agents` are invisible.

**Fix:** Add high-priority discoveries as predefined actions in `will()`, BEFORE the `if not candidates: _self_discover()` block.

**Verification:** After adding a new discovery type to `_self_discover()`, check if it will actually be reached. If there are always predefined actions remaining, it won't.

### 6. Candidate Without Handler (FIXED 2026-06-13)

**Bug:** `_self_discover()` creates candidates (e.g., `connect_isolated_agents`) but `will()` has no `elif` branch for them. The candidate gets chosen but falls through all execution branches silently.

**Fix:** Every candidate ID in `_self_discover()` needs a matching `elif chosen.get('id') == '...'` in will() Phase 5.

**Symptom:** Crystal reports action but nothing happens. No history entry. Same action proposed every cycle.

### 7. learn_* Candidates → Real Actions (FIXED 2026-06-13)

**Bug:** Conscience generated `learn_*` candidates that were labels, not executable actions. They hit the else fallback, got saved to history, but never executed. After 2-3 cycles all candidates exhausted.

**Fix:** Added LEARNING_TO_ACTION mapping that converts each learning_direction to a real action with `_execute_conscience_action()` handler:

```python
LEARNING_TO_ACTION = {
    'добавить междоменный анализ': {'action': 'cross_domain_analysis', 'target': 'all_domains'},
    'углубить понимание через кросс-доменный анализ': {'action': 'cross_domain_analysis', 'target': 'deep'},
    'найти скрытые паттерны в успешных действиях': {'action': 'analyze_kc_domain', 'target': 'success_patterns'},
    # ... 25+ mappings total
}
```

Each mapping maps to `_execute_conscience_action()` which runs real KC queries (SELECT COUNT, domain analysis, etc.).

**Also fixed:** HIGH efficiency actions now generate learning directions too (candidates_high: "углубить понимание", "найти скрытые паттерны", etc.), not just low-efficiency actions.

### 8. prev_learning Exhaustion (FIXED 2026-06-13)

**Bug:** `prev_learning` accumulated ALL learning_directions from ALL assessments in self_model.json. After ~10 assessments, all 20+ candidates were in prev_learning → no new learning_direction generated.

**Fix:** Sliding window — only check last 5 assessments:
```python
assessments = self_model.get('sovest', {}).get('assessments', [])[-5:]
for a in assessments:
    for ld in a.get('learning_direction', []):
        prev_learning.add(ld)
```

**Also:** Cleaned up old learn_* and tactical_research entries from KC will_history (artifacts of pre-fix code).

## Architecture Rules

1. **Action ID format:** All actions saved as `[will:action_id]` in KC raw_text. Universal parser matches `[will:([^\\]]+)]`.
2. **History tracking:** `_load_will_history()` reads last 50 crystal_will entries (was 10, fixed 2026-06-12). `done_sources` derived by stripping `extract_` prefix.
3. **Action routing:** MUST use `chosen['id'].startswith('extract_')` for extract actions — NOT broad `chosen.get('source')` checks, which misroutes non-extract actions.
4. **New action type pattern:** Add detection in `will()` (search for historical_ids guard), add elif execution branch, create `_execute_<action>()` function.
5. **External source pattern:** Add detection in `_self_discover()` + file-reading branch in `_execute_extract()`.
6. **YAML frontmatter:** For structured files, parse `name:` from frontmatter and add as entity with appropriate type_id (AI Agent, not Концепция).
7. **New execution actions (run_*):** MUST check `historical_ids` skip in step 3з to avoid loop. The anti-repetition guard lives inside the `will()` step 3з block, not in `_decide_script()`.
8. **Bridge file:** `crystal_tasks.json` is append-only (writer) + FIFO (reader). No locking needed — single-threaded access via cron.
9. **Self-discover candidates MUST have handlers:** Every `discovered.append({'id': 'X', ...})` in `_self_discover()` needs a matching `elif chosen.get('id') == 'X'` in will() Phase 5. Without it, the candidate loops forever silently.
10. **High-priority discoveries as predefined actions:** If a discovery type (like `connect_isolated_agents`) should ALWAYS be considered — add it as a predefined action (check #D in will()) rather than relying on `_self_discover()`. The `_self_discover()` block is guarded by `if not candidates:` and may never run.
11. **Conscience actions need LEARNING_TO_ACTION mapping:** Every learning_direction string must have a corresponding entry in `LEARNING_TO_ACTION` dict inside will(). Without it, the learning_direction is ignored (no candidate created). Each entry maps to `_execute_conscience_action()` which runs real KC queries.
12. **prev_learning sliding window:** Never accumulate ALL assessments for prev_learning check. Use `[-5:]` to limit to recent assessments. Without this, after ~10 cycles all candidates are "already used" and the crystal stops.
13. **Debugging candidate flow:** Add `print(f"[DEBUG] ...", file=sys.stderr)` at each pipeline stage. Run with `2>&1 | grep DEBUG`. Most common issue: candidates generated but not matching mapping keys.

## Files

- `scripts/crystal.py` — the will implementation (phases 1-10)
- `scripts/autonomous_agent.py` — agent that reads bridge tasks (Phase 10)
- `cache/knowledge_cube.db` — KC (experiences table)
- `cache/entity_engine.db` — EE (entities + relationships)
- `cache/crystal_tasks.json` — bridge file (phase 10)
- `~/fabric/` — Fabric directory (agent memory files)
- `external/agency-agents/` — The Agency (external reference)
