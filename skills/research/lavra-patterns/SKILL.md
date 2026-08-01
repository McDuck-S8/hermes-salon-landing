---
name: lavra-patterns
description: "Lavra/OpenClaude patterns for skill creation, knowledge capture, and multi-agent orchestration. Use when creating new skills, building knowledge bases, or orchestrating parallel tasks."
---

# Lavra Patterns Reference

Patterns extracted from Lavra (OpenClaude's AI coding agent).
Source: D:/Portable_Soft/OpenClaude-Portable-main/engine/lavra/
Hermes Installation: See `references/lavra-hermes-installation.md`

## 1. Skill Creation (from create-agent-skills)

### Core Principles
- Skills ARE prompts — all prompting best practices apply
- YAML frontmatter + markdown body (NO XML tags)
- Keep SKILL.md under 500 lines, split into reference files
- Description must include WHAT + WHEN (discovery field)

### Standard Structure
```
my-skill/
├── SKILL.md              # Entry point (required)
├── reference.md          # Detailed docs (loaded when needed)
├── examples.md           # Usage examples
└── scripts/              # Utility scripts (executed, not loaded)
```

### Frontmatter Fields
| Field | Required | Max | Description |
|-------|----------|-----|-------------|
| name | Yes | 64 chars | lowercase, hyphens only |
| description | Yes | 1024 chars | what + when |
| allowed-tools | No | - | tools allowed without asking |
| model | No | - | specific model |

## 2. Knowledge Capture (from lavra-knowledge)

### 7-Step Process
1. Detect Confirmation ("that worked", "it's fixed")
2. Gather Context (area, symptom, attempts, root cause, solution, prevention)
3. Classify (LEARNED/DECISION/FACT/PATTERN/INVESTIGATION)
4. Write Entry (JSONL format)
5. Log as Bead Comment (traceability)
6. Verify Entry (read back, confirm searchability)
7. Update Codebase Profile (if new area discovered)

### Knowledge Prefixes
- LEARNED: something learned through investigation
- DECISION: architectural/design decision with rationale
- FACT: verifiable technical fact
- PATTERN: recurring solution to common problem
- INVESTIGATION: dead end or negative result (also valuable)

### Integration with Our Systems
- Knowledge Cube: import JSONL entries as experiences
- Fler Engine: analyze tone of knowledge entries
- Memory: extract durable facts for MEMORY.md

## 3. Multi-Agent Orchestration (from lavra-work-multi)

### Wave-Based Parallel Execution
1. Gather beads (tasks) from queue
2. Detect file-scope conflicts (prevent parallel writes)
3. Order into waves (conflict-free batches)
4. Dispatch subagents per wave (implement → self-review → learn)
5. Orchestrator reviews after each wave
6. Repeat until all beads complete

### Integration with Our delegate_task
- delegate_task already implements wave pattern
- Add file-scope conflict detection before dispatching
- Add post-wave review step
- Add learn step (capture knowledge after each task)

### File-Scope Conflict Detection
Script: D:/Portable_Soft/hermes/scripts/file_conflict_detector.py
Usage:
  from file_conflict_detector import detect_conflicts, FileScope
  scopes = [FileScope(task_id="a", files=["config.py"]), FileScope(task_id="b", files=["config.py"])]
  conflicts = detect_conflicts(scopes)  # Returns conflict for config.py

## 4. Auto-Recall Pattern

### How It Works
- Hook searches knowledge.jsonl by keyword at session start
- Injects relevant entries into context
- Builds on existing knowledge, prevents repetition

### Implementation (our scripts)
- `scripts/auto_recall.py` — FTS5 search over Knowledge Cube + Lavra knowledge.jsonl
- `scripts/session_recall.py` — runs at session start, extracts keywords from first user message
- `scripts/import_lavra_knowledge.py` — imports external JSONL into Knowledge Cube
- `data/lavra_knowledge.jsonl` — 217 Lavra entries from OMP-Portable

### Usage
```python
from auto_recall import auto_recall_with_lavra
result = auto_recall_with_lavra("python debugging", top_n=5)
# Returns merged results from Knowledge Cube + Lavra knowledge
```

### Usage (recall_for_session — added 2026-06-04)
```python
from auto_recall import recall_for_session
result = recall_for_session("salon bot deployment", top_n=5)
# Returns: {results, keywords, domain, total, cube_found, lavra_found}
# Merges Knowledge Cube (FTS5 + LIKE) + Lavra (jsonl), sorts by score
```
Use `recall_for_session()` when you need a single-call keyword search across
both data sources. Use `auto_recall_with_lavra()` for the full pipeline with
domain detection.

### Integration with Our Systems
- Knowledge Cube: auto-recall query on session start
- Memory: inject relevant memories at session start
- branches.yaml: auto-load relevant branches

## 5. Benchmark Suite (Community 16)

### Metrics (integrated into self-evolution fitness.py)
- Cost score: token efficiency (0-1, lower tokens = higher score)
- Wall time score: speed relative to baseline (0-1)
- Tests passing: fraction of tests passing (0-1)
- Functional score: does it work on real tasks? (0-1)

### Composite Score Weights
- correctness: 35%
- procedure_following: 25%
- conciseness: 15%
- functional_score: 10%
- tests_passing: 8%
- cost_score: 4%
- wall_time_score: 3%

### Integration with Our Systems
- Self-evolution: `score_with_benchmarks()` method in LLMJudge
- Knowledge Cube: track benchmark results as experiences
- Fler Engine: correlate benchmarks with tone/engagement

## 6. Knowledge Integration from External Sources

### Pattern (learned 2026-06-04)
When user points to an external directory (OpenClaude-Portable, OMP-Portable, etc.):

1. **Scan** — list directory structure, find key files (knowledge.jsonl, graphs, configs)
2. **Extract** — read reports, knowledge bases, analysis outputs
3. **Copy** — bring data files into Hermes (data/, cache/, scripts/)
4. **Integrate** — wire into existing systems (Knowledge Cube, auto-recall, memory)
5. **Update** — add to branches.yaml, update MEMORY.md
6. **Verify** — test that integrated systems work with new data

### Key Files to Look For
- `knowledge.jsonl` — Lavra knowledge base (JSONL entries)
- `graphify-out/GRAPH_REPORT.md` — graph analysis reports
- `*.db` — SQLite databases with experiences/sessions
- `plugins/` — reusable patterns and skills
- `commands/` — slash command definitions

### Anti-pattern
Don't ask "what should I do with this?" — the user expects autonomous integration.
Scan → Extract → Copy → Integrate → Report.

## 7. Event-Driven Self-Evolution (not schedule-based)

### Core Principle
User explicitly rejected cron/schedule-based learning: "только не фиксированно по тайм, а по событиям!!!!"
Self-improvement must react to WHAT HAPPENS, not what time it is.

### Note on Overlap with self-improvement
This section provides DETAILED architecture (event types, triggers, implementation).
The self-improvement skill has a CONDENSED version (quick reference).
If updating Event-Driven Self-Evolution, update BOTH skills.

### Event Types and Triggers

| Event | Trigger | Action | Cooldown |
|-------|---------|--------|----------|
| `task_complete` | Successful task finish | capture_knowledge (LEARNED) | 4h |
| `error_occurred` | Error + fix applied | capture_investigation | 2h |
| `skill_used` | Skill execution | evaluate_skill (size check) | 24h |
| `session_end` | Session closes | session_summary | 4h |
| `knowledge_threshold` | Knowledge cube grows N% | optimize_knowledge | 48h |
| `user_correction` | User corrects agent | capture_pattern | 12h |

### Architecture
```
emit_event() → EventMonitor.record() → EvolutionTrigger.should_trigger() → _execute_action()
                                    ↓
                              capture_knowledge() → knowledge.jsonl → auto_recall()
```

### Implementation Files
- `scripts/event_evolution.py` — EventMonitor, EvolutionTrigger, EvolutionEngine
- `scripts/hermes_hooks.py` — HermesEventHooks for agent integration
- `scripts/event_quickstart.py` — CLI: init, task, error, skill, correction, status, recent, demo
- `cache/events.db` — SQLite: events + triggers tables

### Usage
```python
from scripts.event_evolution import on_task_complete, on_error, on_user_correction

# After successful task
on_task_complete("Deployed salon bot", tags=["salon-bot", "deployment"])

# After error fix
on_error(error="FTS5 corrupted", fix="Recreated database")

# After user correction
on_user_correction(correction="Use OpenCode Zen", context="self-evolution")
```

### Anti-pattern
Don't build schedule-based learning systems. Events > cron. The user's work
doesn't follow a timetable — neither should the learning system.

### Integration Chain
1. Event fires → capture_knowledge writes to knowledge.jsonl
2. Next session → auto_recall_with_lavra searches knowledge.jsonl
3. Context injection → agent has relevant past experience
4. Better decisions → fewer repeated mistakes → faster progress

### Pitfall: Cooldowns Are Critical
Without cooldowns, high-frequency events (skill_used on every tool call) would
flood knowledge.jsonl with noise. Cooldowns ensure only meaningful captures.
Default cooldowns: error=2h, task=4h, skill=24h, knowledge=48h.

### Pitfall: Parameter Mismatch in Knowledge Capture (learned 2026-06-04)
The event system's internal `_capture_*` functions were calling `capture_knowledge()` with parameters `entry_type` and `tags`, but the actual knowledge capture function expects `prefix` and `area`. This caused silent failures where events were recorded but no knowledge was captured.

**How to detect:** 
- Events show as processed in events.db but no new entries appear in knowledge.jsonl
- Check logs for "Unexpected keyword argument" errors when capture_knowledge is called

**Fix:** 
Update the event system's `_capture_knowledge`, `_capture_investigation`, and `_capture_pattern` functions to use:
```python
capture_knowledge(
    prefix="LEARNED",  # not entry_type
    content=content,
    area=tags + [...],  # not tags parameter
    source=source
)

**Integration Chain Test:**
After fixing, verify the full chain: 
1. Emit event → 
2. Process events → 
3. Check knowledge.jsonl for new entry with correct prefix and area

### Pitfall: Dead Code — Scripts Exist But Nobody Calls Them ( learned 2026-06-04)
The #1 failure mode: all scripts are written, all DBs exist, but the system
does nothing. Audit result (2026-06-04): 12 events written, 0 processed.
Hooks defined in hermes_hooks.py but no AGENTS.md to invoke them.

**How to detect:**
```python
import sqlite3
conn = sqlite3.connect('cache/events.db')
unprocessed = conn.execute('SELECT COUNT(*) FROM events WHERE processed=0').fetchone()[0]
total = conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]
print(f'{unprocessed}/{total} events unprocessed')  # If > 0 → dead code
```

**Root cause checklist:**
1. No AGENTS.md or session hooks → agent doesn't know about the system
2. No caller → functions exist but nothing invokes them
3. No integration test → nobody verified end-to-end flow
4. Cron broken (API credits, wrong provider) → background processing stopped

**Fix order:** AGENTS.md first (tells agent what to do), then verify callers,
then test end-to-end. Don't add more features to dead systems.

### Audit Methodology (learned 2026-06-04)
When checking if a system actually works, don't just list files. Test the PIPELINE:

1. **Data exists?** → `SELECT COUNT(*) FROM table` (not "file exists")
2. **Data processed?** → `SELECT COUNT(*) WHERE processed=0` (the real test)
3. **Callers exist?** → grep for function imports across codebase
4. **End-to-end?** → call the function, check output, verify side effects
5. **Automated?** → is there a hook/cron/event that triggers this without being asked?

If steps 1-2 pass but 3-5 fail → DEAD CODE. The system is a sophisticated logger.

### Plan A vs Plan C Decision Framework (learned 2026-06-04)
When a system is broken, choose repair scope:

**Plan A — Patch (30-60 min):**
- Add missing "glue" (AGENTS.md, callers, integration hooks)
- Keep existing scripts/DBs, just connect them
- Test end-to-end with existing data
- When: system has working parts that just aren't connected

**Plan C — Rebuild (2-4 hours):**
- Merge duplicate systems (e.g. unified.db + core_engine.db → one DB)
- Rewrite with clean architecture
- When: Plan A reveals deep structural problems, or duplicates cause confusion

**Rule:** Start with A. Only escalate to C when A shows the system is
fundamentally wrong (not just missing glue, but bad design).

## 8. Universal Information Events

### Core Principle
Every piece of information IS an event. Not just task_complete/error_occurred — 
ANY information entering the system is an event that changes it.

### Information → Event → Impact → Adaptation
- Novelty (0-1): how new is this?
- Importance (0-1): how important?
- Relevance (0-1): how relevant to current goals?
- Impact = novelty*0.4 + importance*0.4 + relevance*0.2

### Adaptation Types
- High novelty → capture_knowledge
- High importance → update_strategies
- High relevance → adjust_goals
- error category → investigate_error
- decision category → validate_decision
- pattern category → generalize_pattern

### Implementation
- `scripts/unified.py` — UnifiedSystem (all-in-one: search, gaps, learning, chains)
- `scripts/core_engine.py` — CoreEngine (connects to real data)
- `scripts/event_patterns.py` — EventPatterns (impact, actions, patterns, chains)
- `cache/unified.db` — gaps + searches + learnings + patterns
- `cache/core_engine.db` — gaps + searches + benefits + impacts + patterns + chains

### Deep Dive
See `references/universal-events.md` for detailed architecture and schema.

## 9. Autopoietic Loop (Self-Creating Through Information)

### The Ultimate Loop
1. Gap discovered → knows what it doesn't know
2. Information seeking → searches to learn
3. Information fed → feeds the system
4. Learning complete → extracts knowledge
5. System grows → knows what else it doesn't know
6. Infinite loop → self-creation through information

### Integration with Lavra Knowledge Capture
- Knowledge gaps from analysis → discover_gap()
- Search queries → seek_information()
- Found information → feed_information() → capture_knowledge()
- Learning from meals → learn_from_meal()

### Implementation
- `scripts/core_engine.py` → `find_real_gaps()` and `run_chain("gap_analysis")`
- `scripts/unified.py` → `find_gaps()` and `chain()`
- `cache/core_engine.db` — gaps + searches + benefits

### Deep Dive
See `references/autopoietic-system.md` for detailed architecture and schema.

### Pitfall: Unified Gap Filling Bug (learned 2026-06-04)
`chain('fill_gap')` in unified.py finds gaps, searches, and logs learnings,
but NEVER updates `filled=1` in knowledge_gaps table. All gaps stay at
filled=0 forever, making the system think it has more gaps than it does.

**Fix:** Add UPDATE query after learn():
```python
conn_g = sqlite3.connect(str(UNIFIED_DB))
conn_g.execute("UPDATE knowledge_gaps SET filled=1 WHERE topic=? AND filled=0", (g['topic'],))
conn_g.commit()
conn_g.close()
```

**How to detect:** `SELECT filled, COUNT(*) FROM knowledge_gaps GROUP BY filled`
If all rows show filled=0 → bug present.

### Anti-pattern
Don't wait for schedule-based triggers. The system should be hungry — 
constantly seeking information to fill its knowledge gaps.

## 10. OpenCode→Hermes Skill Conversion (learned 2026-06-04)

When importing external agent systems (Lavra, OpenCode, Claude Code) into Hermes:

### Conversion Pipeline
1. **Scan** source for SKILL.md files, agents/, commands/, memory/
2. **Read** each source SKILL.md (OpenCode uses XML tags: <objective>, <process>, <execution_context>)
3. **Convert** to Hermes format:
   - Strip XML tags → plain markdown sections
   - Simplify frontmatter: keep name, description, category only
   - Remove OpenCode-specific fields: argument-hint, metadata, overwrite-warning
   - Replace `Skill("name")` → `skill_view(name="name")`
   - Remove HTML comments (generation markers)
4. **Write** to `D:\Portable_Soft\hermes\skills\<name>\SKILL.md`
5. **Test** by loading via skill_view() and running on real task

### Batch Conversion (execute_code)
For 10+ skills, use execute_code with a loop — faster than delegate_task:
```python
import os, re
for skill_name in skills_list:
    content = open(source_path).read()
    # Convert XML→markdown, fix frontmatter
    write_file(target_path, converted)
```

### Agent Files → Skills
Agent .md files (from agents/ directory) become Hermes skills with:
- name: lavra-agent-<original-name>
- category: lavra-agents
- Body: preserved review criteria, checklists, specialized knowledge

### Pitfall: JSONL Double-Parsing
Lavra knowledge.jsonl stores each entry as a JSON-encoded STRING containing JSON:
```python
outer = json.loads(line)       # outer is a string
e = json.loads(outer) if isinstance(outer, str) else outer
```
Not raw JSON objects. Failing to double-parse gives 0 imported entries.

### Pitfall: List Tags in JSONL
The `tags` field is often a list, not a string. SQLite FTS5 needs strings:
```python
tags = e.get('tags','')
if isinstance(tags, list):
    tags = ','.join(tags)
```

### Pitfall: recall.sh Needs jq
The bash recall.sh script requires `jq` for JSON parsing. Verify with:
```bash
which jq && jq --version
```

## 11. Provider Migration Pattern (learned 2026-06-04)

When a provider dies (402/404/timeout), migrate systematically:

### Steps
1. **Test** — curl/httpx the provider endpoint to confirm it's dead
2. **Find alternative** — check .env for other API keys, test free models
3. **Update config.yaml** — change api_key, base_url, default model
4. **Update cron jobs** — LLM-based jobs need `model` override:
   ```python
   cronjob(action='update', job_id='xxx', model={'model': 'meta-llama/llama-3.1-8b-instruct', 'provider': 'openrouter'})
   ```
5. **Verify** — test inference with the new provider
6. **Update memory** — record which provider is active

### Known Dead Providers (as of 2026-06-04)
- OpenGateway (openclaude.gitlawb.com) — 404 on all endpoints
- OpenRouter with `:free` suffix — models renamed, use base names

### Working Free Models on OpenRouter
- `meta-llama/llama-3.1-8b-instruct` — tested, works
- Others may work but untested

### Cron Job Model Override
Jobs with `model=null` inherit from config.yaml default. To override per-job:
```python
cronjob(action='update', job_id='xxx', model={'model': 'model-name', 'provider': 'openrouter'})
```
This is needed when the default provider changes but specific jobs should stay on a known-good model.


## 13. NEVER Manual Work Outside /lavra-work (learned 2026-06-09)

### Critical User Correction
The user was FURIOUS about manual code changes outside the /lavra-work protocol.
Direct quote: "ты блять снова свои ручки запустил???!!!! всё через лавр!!!!!"

**ABSOLUTE RULE:** ALL code changes MUST go through /lavra-work beads.
No manual patches. No "quick fixes". No exceptions.

### Why This Rule Exists
1. Manual changes bypass review, testing, and knowledge capture
2. Changes get lost or forgotten without bead tracking
3. User explicitly demands protocol compliance — violating it destroys trust
4. Beads provide audit trail and dependency tracking

### Correct Workflow
```
1. bd ready → see available beads
2. /lavra-work {bead_id} → follow lavra-work-single protocol
3. Implement changes → commit → close bead
4. Repeat for next bead
```

### Wrong Workflow (NEVER DO THIS)
```
# WRONG: Manual patch outside protocol
patch(file, old, new)  # ← FORBIDDEN without active bead
terminal("git add ... && git commit ...")  # ← FORBIDDEN without bead
```

### Pitfall: "It's Just One Line" Trap
The most dangerous moment is when you think "this is trivial, I'll just fix it."
That's exactly when you MUST create a bead and use /lavra-work.
Trivial fixes without tracking accumulate into untracked technical debt.

### Integration with Other Skills
- `lavra-work` — the protocol for all code changes
- `lavra-work-single` — single bead implementation
- `lavra-review` — review after implementation
- `requesting-code-review` — pre-commit review (compatible with lavra)

## 14. Common Python Pitfalls in Hermes Codebase (learned 2026-06-09)

### Hardcoded Absolute Paths
**Problem:** Scripts use `D:/Portable_Soft/hermes/` which breaks on other machines.
**Fix:** Use relative paths from script location:
```python
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent  # if scripts/ is one level down
```

### Bare except: pass
**Problem:** `except: pass` silently swallows ALL errors including KeyboardInterrupt.
**Fix:** Always catch specific exceptions and log them:
```python
try:
    # code
except Exception as e:
    print(f"[{component}] Error: {e}", file=sys.stderr)
```

### Temp File Deletion Before Fallback
**Problem:** Deleting temp file BEFORE trying fallback commands means fallback has nothing to work with.
**Fix:** Delete temp file ONLY after all attempts succeed or fail:
```python
try:
    with tempfile.NamedTemporaryFile(...) as tmp:
        # try method 1
        # try method 2
finally:
    # cleanup AFTER all attempts
```

### Observational Action Executors
**Problem:** Action executors that only `print()` don't actually fix anything.
**Fix:** Each executor should have at least one real side effect:
- `_action_fix_cron_errors` → actually disable broken cron jobs
- `_action_explore_white_spots` → actually add entries to Knowledge Cube
- `_action_apply_suggestions` → actually apply patches
