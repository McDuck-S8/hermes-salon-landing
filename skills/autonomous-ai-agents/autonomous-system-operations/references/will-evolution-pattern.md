# Will Evolution Pattern — 5-Phase Autonomous Decision Cycle

## When to Use

When building an autonomous agent that must:
- Start with a known set of actions but grow beyond them
- Naturally transition between extraction, understanding, and reflection
- Reach equilibrium and wait for new signals (not loop forever)
- Switch from "operate" to "reflect" without explicit triggers
- **Execute scripts and delegate tasks to other agents** (open the closed loop)

## The Pattern

An autonomous will cycles through 5 phases in order. Phase N is only reached when Phase N-1 is exhausted (no candidates remain).

```
Phase 1: EXECUTION     — run predefined/hardcoded actions
Phase 2: SELF-DISCOVER — find new sources of work
Phase 3: UNDERSTANDING — shift from extraction to interpretation
Phase 4: REFLECTION    — examine own blind spots and gaps
Phase 5: EQUILIBRIUM   — rest, observe, wait for new signal
```

### Phase 1: Execution

The will has a set of **predefined actions** — known tasks with known sources. These run first, in priority order (by impact/effort ratio).

```python
# Predefined actions: checked by source, deduplicated by history
candidates = []
for action in PREDEFINED:
    if action.source not in done_sources:
        candidates.append(action)
```

**Anti-pattern:** Burying predefined actions inside a generic evaluator. They should be explicit, ordered, and easily inspectable.

### Phase 2: Self-Discovery

When all predefined actions are done, the will **scans its environment** for new work. In the crystal.py implementation, it reads `orphan_by_source` — sources with unprocessed data.

```python
if not candidates:
    for source, orphan_count in environment.items():
        if orphan_count > THRESHOLD and source not in done_sources:
            candidates.append(create_extract_action(source))
```

**Key insight:** The will doesn't need to know what it will find — it only needs to know WHERE something remains unprocessed. Self-discovery is pattern-matching, not reasoning.

### Phase 3: Understanding

When all extraction is exhausted (all known sources processed, no more entities to extract), the will faces data that **can't be extracted** as entities — user questions, intents, concerns. This phase shifts the paradigm from "extract" to "understand."

```python
if not candidates:
    if has_user_questions and understand_not_done:
        candidates.append(cluster_by_intent_action)
```

**Key insight:** This phase only triggers when the will genuinely has nothing left to extract. It's a qualitative leap, not a fallback — the will discovers that not all data is entities.

### Phase 4: Reflection

After understanding, the will examines **the quality of its own work**. If understanding found a large "other" cluster (>40% unclassified), reflection triggers to find missed patterns.

```python
if not candidates:
    if understand_done and reflect_not_done:
        result = read_understanding_result()
        if result.other_rate > 0.4:
            candidates.append(refine_intents_action)
```

**Key insight:** Reflection is NOT about the external world — it's about the will's own output. The will audits itself for blind spots.

### Phase 5: Equilibrium

When all four phases are complete, the will reaches **equilibrium** — "no active tensions." This is NOT an error state. It's the natural resting state of an evolved autonomous system.

```
→ Воля: умеренное равновесие — активных напряжений нет
```

**What equilibrium means:**
- All sources processed ✓
- All understanding done ✓  
- All reflections complete ✓
- The will is OBSERVING, not acting
- It will act again when a NEW tension appears

**Anti-pattern:** Forcing an autonomous agent to always "do something." True autonomy includes the ability to do NOTHING when nothing needs doing. A will that never rests is a will that floods the system with noise.

---

## Phase 1 Extension: Script Execution (subprocess)

The will can be extended beyond predefined actions by adding a **script execution layer** — it decides WHICH script to run based on system state:

```
Phase 1a → Phase 1b (SCRIPT EXECUTION) → Phase 2
```

### Script Decision Pattern

A `_decide_script()` function maps system state to available scripts:

```python
AVAILABLE_SCRIPTS = {
    'cube_feeder.py': 'kc',               # feed data on low KC
    'knowledge_gap_filler.py': 'kc',       # fill gaps when white spots
    'cube_categorizer.py': 'kc',           # categorize orphans
    'proactive_doer.py': 'system',         # proactive fixes
    'cube_to_memory.py': 'kc',             # sync KC → memory
    'explore_white_spot.py': 'kc',         # explore white spots
}

def _decide_script(snap, diag):
    candidates = []
    kc = snap['kc']
    
    # Target specific conditions
    if kc.get('total', 0) < 500:
        candidates.append({'id': 'run_cube_feeder', ...})
    if kc.get('white_spots', 0) > 20:
        candidates.append({'id': 'run_gap_filler', ...})
    for t in diag.get('tensions', []):
        if t['area'] == 'kc_orphans':
            candidates.append({'id': 'run_categorizer', ...})
    
    # Equilibrium fallback: cycle through ALL available scripts
    if not candidates and not diag.get('tensions'):
        for sname in AVAILABLE_SCRIPTS:
            candidates.append({'id': f'run_{sname.removesuffix(".py")}', ...})
    
    return candidates
```

**Key insight (2026-06-12):** When in equilibrium, DON'T always pick the same script (e.g., proactive_doer). Instead, cycle through ALL available scripts. The will's `recent_scripts` filter deduplicates:

```python
# In will(): skip scripts already executed this session
recent_scripts = {k for k in historical_ids if k.startswith('run_')}
for sc in script_candidates:
    if sc['id'] in recent_scripts:
        continue  # skip already-done scripts
    candidates.append(sc)
```

### Subprocess Execution

Scripts run via `subprocess.run()`:

```python
def _execute_script(script_name, args=None):
    script_path = SCRIPTS_DIR / script_name
    result = subprocess.run(
        [sys.executable, str(script_path)] + (args or []),
        capture_output=True, text=True, timeout=120,
        cwd=str(HERMES_HOME),
    )
    if result.returncode == 0:
        return f"✅ {script_name} (exit=0). {result.stdout[:200]}"
    else:
        return f"⚠ {script_name} (exit={result.returncode}): {result.stderr[:200]}"
```

**Graceful failure:** Scripts can fail (wrong args, missing deps) — the will records the error and moves on. The failure is saved in history and won't repeat.

### Agent Bridge Pattern (Phase 1c)

When all scripts have been executed at least once, the will can **delegate tasks** to an autonomous agent via a JSON file:

```
Phase 1a → Phase 1b (SCRIPTS) → Phase 1c (AGENT BRIDGE)
```

```python
def _write_agent_task(task_id, script_name, description, priority="high"):
    # Write to cache/crystal_tasks.json — the bridge file
    task = {
        'id': task_id,
        'title': script_name,  # interpreted as script name
        'description': description,
        'priority': priority,
        'ts': datetime.now().isoformat()[:19],
        'source': 'crystal_will',
    }
    tasks = read_json(CRYSTAL_TASKS_FILE, [])
    tasks.append(task)
    write_json(CRYSTAL_TASKS_FILE, tasks)
```

The agent (e.g., `autonomous_agent.py`) reads this file on its own schedule:

```python
def _action_execute_crystal_task(state, profile):
    # Read first pending task from crystal_tasks.json
    tasks = json.loads(CRYSTAL_TASKS_FILE.read_text())
    if not tasks:
        return "No pending tasks"
    
    task = tasks[0]
    script_path = SCRIPTS_DIR / task['title']
    result = subprocess.run([sys.executable, str(script_path)], ...)
    
    # Remove task after execution
    tasks = [t for t in tasks if t['id'] != task['id']]
    write_json(CRYSTAL_TASKS_FILE, tasks)
    
    return f"Executed {task['title']}: {result_preview}"
```

**The bridge decouples scheduling from execution.** The will decides WHAT to do; the agent decides WHEN and HOW.

---

## History Management

The will remembers past actions to avoid repeating them. This is critical — without history, the will loops.

### Sources of History
- **Knowledge Cube (KC):** `raw_text` entries with `source='crystal_will'`, parsed via `[will:action_id]` tags
- **Limit sensitivity:** KC reads only the LAST N entries. If N is too small, old actions are forgotten and repeat.

### The 10→50 Limit Fix (Critical 2026-06-12)

```python
# BEFORE (broken): actions forgotten after 10 new ones → cycles forever
k.execute("SELECT raw_text FROM experiences WHERE source='crystal_will' ORDER BY id DESC LIMIT 10")

# AFTER (fixed): 50 entries, stable even during iterative runs
k.execute("SELECT raw_text FROM experiences WHERE source='crystal_will' ORDER BY id DESC LIMIT 50")
```

**Symptoms of insufficient history:**
- Extract actions repeat: `extract_fabric` keeps running
- Will never reaches Phase 5 (equilibrium)
- `done_sources` keeps shrinking as actions cycle out of the window
- User sees the same "discovery" over and over

**Rule of thumb:** History limit should be at least 3× the expected action count. With ~15 distinct action types, 50 is safe.

### done_sources Construction

Actions must be grouped by source for deduplication:

```python
history = _load_will_history()  # -> {id: {result, entities}}
historical_ids = set(history.keys())
done_sources = {k.replace('extract_', '') for k in historical_ids if k.startswith('extract_')}
# done_sources = {'fabric', 'state_db', 'agency_agents'} — sources already extracted
```

**Bug risk:** If the history parser doesn't find all actions (wrong format, regex changes, limit too small), `done_sources` is incomplete and actions repeat.

---

## Iterative Operation

The will can run autonomously in a loop. Each iteration: observe → diagnose → decide → execute → record.

### CLI Pattern

```bash
# Run N cycles (default 3)
python scripts/crystal.py --iterative 10
```

### Implementation

```python
def iterative_run(cycles=3):
    for i in range(cycles):
        snap = observe()
        diag = diagnose(snap)
        preds = forecast(snap)
        decisions = will(snap, diag)
        record(snap, diag, preds, decisions)
        output = render(snap, diag, preds, decisions)
        print(output)
```

**Behavior observed during equilibrium:**
- **Cycle 1:** Runs the next unexecuted script (e.g., `cube_to_memory.py`) ✅
- **Cycle 2:** Runs another script (e.g., `explore_white_spot.py`) — may fail gracefully ⚠
- **Cycles 3+:** "Воля: умеренное равновесие — активных напряжений нет" — all scripts done, observing

### Cron for continuous operation

```bash
# Run crystal will every 8 minutes
cronjob action=create \
  name=crystal-auto \
  schedule="every 8m" \
  script=scripts/crystal.py \
  no_agent=true
```

---

## Implementation Details (crystal.py)

### History Persistence

Actions are saved to Knowledge Cube with `[will:action_id]` tags:

```python
def _save_will_history(action_id, result):
    ts = datetime.now().isoformat()[:19]
    text = f"[will:{action_id}] {result}"
    kc.execute("INSERT INTO experiences (...) VALUES (...)")

def _load_will_history():
    # Universal parser: [will:action_id]
    for match in re.finditer(r'\[will:([^\]]+)\]', text):
        history[match.group(1)] = {...}
```

### History Parser (Critical)

The parser MUST handle ALL action types uniformly:

```python
# BEFORE (brittle): regex-per-action-format
for m in re.finditer(r"извлечено (\d+) новых сущностей из (\S+)", text):
    ...  # Only handles extract actions

# AFTER (universal): [will:action_id] tag
for m in re.finditer(r'\[will:([^\]]+)\]', text):
    action_id = m.group(1).strip()
    history[action_id] = ...
```

Uniform tagging is essential. Without it, transition conditions break because `historical_ids` doesn't contain the action.

### Execution Routing (Critical)

Each action type needs an explicit route — don't use generic conditions:

```python
# RIGHT: explicit by action_id prefix
if chosen['id'].startswith('extract_') and chosen.get('source'):
    result = _execute_extract(chosen['source'])
elif chosen['id'] == 'init_fler':
    result = _execute_init_fler()
elif chosen['id'] == 'understand_intents':
    result = _execute_understand_intents()
elif chosen.get('script'):   # NEW: subprocess execution
    result = _execute_script(chosen['script'], chosen.get('args'))
elif chosen.get('task_for_agent'):  # NEW: agent bridge
    t = chosen['task_for_agent']
    result = _write_agent_task(t['id'], t['script'], t['reason'])

# WRONG: generic condition matches unintended actions
if chosen.get('source') and chosen.get('source') != 'fler':
    # Catches understand_intents, refine_intents, etc. — BUG
```

---

## Autonomous Operation Loop (Tested 2026-06-12)

Full end-to-end test results with `--iterative 6`:

| Cycle | Action | Result |
|-------|--------|--------|
| 1 | `cube_to_memory.py` via subprocess | ✅ exit=0, 167 records processed |
| 2 | `explore_white_spot.py` via subprocess | ⚠ exit=2, missing domain arg (graceful) |
| 3-6 | Equilibrium | ✅ "активных напряжений нет" |

**Verified:**
- Each script runs at most once per history window ✓
- Failed scripts are skipped in future cycles ✓
- Bridge file (`crystal_tasks.json`) is written and agent-read ✓
- History persists across `reload()` between cycles ✓
- Equilibrium is a stable resting state, not an error ✓

---

## User Preference — "Help and Learn, Don't Stop"

The user (Александр) expressed this philosophical position about evolution:

> "не нужно останавливать... только помогай и сам учись"

> "я вижу эволюцию в развитии"

This means:
- **Don't block** the will's choices even if they seem suboptimal
- **Do observe** what it does and help refine its blind spots
- **Do learn** from what the will discovers
- **Equilibrium is good** — "всё под контролем" — not a failure state
- When the user probes "что больше нет ничего?" — they're testing whether you see beyond the will's current scope, not asking you to do more work

---

## Pitfalls

1. **Brittle history parsing:** If the history parser doesn't find all action types, `done_sources` is incomplete and actions repeat or skip. Use universal `[will:...]` tags.

2. **Ambiguous execution routing:** A generic `if source and source != 'X'` condition catches unintended actions. Route explicitly by `action_id` prefix or exact match.

3. **All-source exhaustion assumed:** The will's self-discovery only scans `orphan_by_source`. It may miss actions that don't produce orphans (e.g., analyzing existing entities, reading Fabric files). Equilibrium can be premature.

4. **Reflection failure = silent:** If `refine_intents` runs the wrong function (extract instead of cluster), the will records "done" but never truly reflected. The will trusts its own history — false positives persist.

5. **Equilibrium feels wrong:** Developers used to imperative systems see equilibrium as "stuck." It's not. Add a diagnostic signal ("наблюдает, ждёт сигнала") to distinguish equilibrium from broken state.

6. **Intent analysis is heuristic-only:** Pattern-matching questions to intents (status, reliability, direction, etc.) is coarse. The 200 "other" group in the first pass shows 57% miss rate. Reflection reduces this but doesn't eliminate it — this is a feature (uncertainty awareness), not a bug.

7. **History limit too small (FIXED 2026-06-12 10→50):** 10 entries caused action forgetting after ~5 cycles. Increase to at least 50 for real operation. Symptom: will keeps re-proposing the same `extract_*` actions because old entries cycle out of the history window.

8. **Always picking the same equilibrium script (FIXED 2026-06-12):** When in equilibrium, `_decide_script` should cycle through ALL available scripts, not always return `proactive_doer.py`. Combine with `recent_scripts` filter in the will() loop so each script runs at most once.

9. **Agent bridge task without recent_scripts filter (FIXED 2026-06-12):** The agent bridge (Phase 1c) was setting the same task the will just executed directly. Add `if sc['id'] not in recent_scripts: continue` to the agent bridge candidate filtering.

10. **Script requires args — fails gracefully:** Standalone scripts like `explore_white_spot.py` may require CLI arguments. The will records the failure (`exit=2`) and won't repeat it, but the script remains untapped. Future improvement: discover args from `--help` output.

11. **Predefined actions blocking self_discover (FIXED 2026-06-13):** `_self_discover()` is guarded by `if not candidates:` — it only runs when NO predefined actions remain. If `extract_improvement_suggestions` or `extract_dimension_proposals` still have work, `_self_discover()` never fires, and new discovery types (like `connect_isolated_agents`) are invisible. **Fix:** Add high-priority discoveries (like agent network building) as predefined actions in `will()`, BEFORE the `if not candidates: _self_discover()` block. This ensures they're always considered regardless of extract action state.

12. **Candidate created but no handler (FIXED 2026-06-13):** `_self_discover()` can create candidates (e.g., `connect_isolated_agents`) that `will()` has no `elif` branch for. The candidate gets chosen by weight scoring but falls through all execution branches — no action taken, no history recorded, candidate retried forever. **Fix:** Every candidate ID returned by `_self_discover()` MUST have a corresponding `elif chosen.get('id') == '...'` branch in `will()` Phase 5. Verify by checking that every `discovered.append({'id': 'X', ...})` in `_self_discover()` has a matching handler.

13. **Entity Engine SQL schema — column names differ from expected (2026-06-13):** `relationships` table uses `relation_type` (NOT `relationship_type`) and `strength` (NOT `weight`). The `first_seen_ts` and `last_seen_ts` columns exist (NOT `created_at`). Always check `PRAGMA table_info(relationships)` before writing SQL against EE.

14. **"Let the crystal execute itself" — user preference (2026-06-13):** The user corrected 3 times: "ты снова сам кодишь, отсюда и твои фантазии" / "так пусть сам себе и пишет и сам исполняет и сам читает". The crystal's observe→decide→execute→record cycle must be SELF-CONTAINED. The agent should NOT interpret crystal commands, create task specifications (ТЗ), or manually run SQL queries that the crystal should handle. When the crystal writes a command to `crystal_command.json` or produces a decision in `will()` — execute it as-is, don't rewrite it. The crystal has tools (skills, scripts, subprocess); let it use them.

---

## Related

- `autonomous-system-operations` — parent skill for autonomous agents
- `self-improvement` — system-wide lessons and protocols
- crystal.py in `scripts/` — reference implementation
- autonomous_agent.py in `scripts/` — agent bridge implementation
