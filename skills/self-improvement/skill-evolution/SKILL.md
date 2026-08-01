---
name: skill-evolution
description: "Auto-evolve skills from Knowledge Cube — index, detect gaps, create/update skills automatically"
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [skills, evolution, auto-update, knowledge-cube, self-improvement]
related_skills: [self-improvement-runtime]
---

# Skill Auto-Evolution

Orchestrator that keeps skills fresh and relevant. Runs a pipeline: index skills → detect knowledge gaps → evolve skills from Knowledge Cube patterns.

## When to Use

- At system startup (daily) to ensure skills reflect current knowledge
- After any significant Knowledge Cube growth (100+ new entries)
- When you notice skills are stale or missing common patterns
- After installing new skills to index them properly
- The cron job `skill-evolution` (daily at 4:00 AM) runs this automatically

## Pipeline

```bash
┌──────────────────────────────────────────┐
│ 1. Run proactive_executor.py (single     │
│    script does all 3 phases)             │
│    ┌─────────────────────────┐           │
│    │ Phase 1: KC Analysis     │           │
│    │ Phase 2: Cron Error Scan│           │
│    │ Phase 3: Apply Fixes    │           │
│    │ Phase 4: Gap Detection  │           │
│    │ Phase 4c: Skill Evolution│          │
│    └─────────────────────────┘           │
└──────────────────────────────────────────┘
```

> **✅ Reality check (2026-08-01)**: The standalone 3-script pipeline **DOES exist and runs** — verified live this session: `python scripts/skill_indexer.py` (549 SKILL files, 237 newly indexed), `python scripts/latent_domain_detector.py --seed` (gap analysis + seed insertion), `python scripts/skill_evolution_v2.py` (read-only audit of installed skills/usage/KC). A 2026-07-25 note claimed these scripts never existed and that all phases live in `proactive_executor.py` — that note was wrong/stale. Both paths work: `proactive_executor.py` (single combined run) AND the explicit 3-script pipeline. When in doubt, check `ls scripts/` first instead of trusting either doc.

### The Only Working Command

```bash
cd /d/Portable_Soft/hermes
python scripts/proactive_executor.py
```

This single script completes the full cycle: Knowledge Cube analysis → cron error scan + LLM analysis → fix application → gap detection → skill auto-evolution.

### Alternative: explicit 3-script pipeline (verified working 2026-08-01)

```bash
cd /d/Portable_Soft/hermes
python scripts/skill_indexer.py              # indexes SKILL.md files into cube (source='skill-indexer')
python scripts/latent_domain_detector.py --seed   # gap analysis + inserts knowledge-gap seeds (source='latent-domain-detector')
python scripts/skill_evolution_v2.py         # READ-ONLY audit: lists skills, usage events, KC state — creates/updates NOTHING
```

Notes on the 3-script path:
- `skill_evolution_v2.py` never writes skills — it is a pure reporter (122 skills, skill_used events, KC last entries). "Evolve skills" in the old cron description was always aspirational for this script.
- `skill_indexer.py` prints `SUMMARY: Total SKILL.md files found / Newly indexed / Total unique skills` — grep for those lines.
- `latent_domain_detector.py --seed` inserts seeds for missing domains (marketing/analytics/seo/cicd/monitoring/backup were flagged 2026-08-01); verify with `SELECT COUNT(*) FROM experiences WHERE source='latent-domain-detector'`.

## Step-by-Step Procedure

### Run the Full Pipeline

All phases execute in one command:

```bash
cd /d/Portable_Soft/hermes
python scripts/proactive_executor.py
```

**Expected output:** Knowledge Cube analysis (44+ domains listed) → cron error scan → LLM analysis (capped at 45s) → fix application → gap detection → skill auto-evolution (finds patterns, skips duplicates). Duration: ~90s.

### Partial: Run Detection Only (if Full Is Too Heavy)

If you only want gap analysis without the full evolution cycle:

```bash
cd /d/Portable_Soft/hermes
python scripts/proactive_executor.py
```
Then read the output sections `[Phase 4] Knowledge-Driven Task Generation` and `[Phase 4c] Skill Auto-Evolution` — these contain the gap/detection/evolution results inline.

## How Evolution Works

### Domain → Skill Mapping

When a Knowledge Cube domain has 20+ entries:

| Domain | Skill Created/Updated | Threshold |
|--------|----------------------|-----------|
| `coding` | `coding-patterns` | 20 entries |
| `research` | `research` | 20 entries |
| `browser` | `agent-browser` | 20 entries |
| `data` | `data-science` | 20 entries |
| `devops` | `devops` | 20 entries |
| `creative` | `creative` | 20 entries |
| Any new domain | `{domain}-patterns` | 20 entries |

### Pattern Extraction

The evolution engine scans entries for keywords marking reusable knowledge:
- `always`, `never`, `must`, `should`, `best practice`
- `важно`, `нужно`, `всегда`, `никогда`
- `remember`, `pattern`, `tip`, `checklist`
- `NOTE:`, `WARNING:`, `IMPORTANT:`

Each matched keyword produces a snippet that gets added to the skill.

### Update Logic

- If skill exists and has no `## Auto-evolved patterns` section → patterns appended
- If skill exists and already has the section → skip (avoids duplication)
- If skill doesn't exist and domain has 20+ entries → new SKILL.md created

## Automation

This pipeline runs automatically via cron:

```bash
# Current cron job (daily at 4:00 AM):
#   Name: self-evolution-cycle
#   Job ID: e4905470f419
#   Command: python scripts/proactive_executor.py
#   Schedule: "0 4 * * *"
#   NOTE: The cron job originally specified a 3-script pipeline
#   (skill_indexer → latent_domain_detector → skill_evolution_v2).
#   Those scripts EXIST and run (verified 2026-08-01); the combined
#   proactive_executor.py path also works. If the cron job fails,
#   check jobs.json to confirm which command it actually runs.
```

See [references/session-20260610-execution.md](./references/session-20260610-execution.md) for the inaugural cycle trace (197 skills indexed, 32 seeds, 6 created, 7 updated).  
See [references/session-20260611-execution.md](./references/session-20260611-execution.md) for the second cycle trace (205 skills indexed, 33 seeds, 5 updated, monitoring gap detected).  
See [references/session-20260801-pipeline-bugfix.md](./references/session-20260801-pipeline-bugfix.md) for the 2026-08-01 trace — 3-script pipeline verified live, seed-insertion bug (INSERT OR IGNORE + NOT NULL content) found & fixed, verification pattern for untested scripts, `kc_rag.upsert()` signature.

## State

Evolution state is tracked in:
- `cron/skill_evolution_state.json` — **minimal**: only `last_run` (ISO timestamp) and `total` (entries analysed that run). No per-skill change log. To audit what changed, compare `git diff --stat` before and after, or check SKILL.md timestamps with `find skills/ -name SKILL.md -newer <state_file>`.
- `cache/knowledge_cube.db` — all indexed skill metadata

## Requirements

- Python 3.8+
- Knowledge Cube database initialized
- All scripts in `scripts/` directory
- Write access to `skills/` directory

## Pitfalls

- **Pipeline scripts DO exist (corrected 2026-08-01)**: `skill_indexer.py`, `latent_domain_detector.py`, `skill_evolution_v2.py` all exist in `scripts/` and run successfully. An earlier note claiming they never existed was stale — a previous `ls`/doc check missed them. `proactive_executor.py` remains the combined single-run path, but the explicit 3-script pipeline is a valid alternative (and is what the original cron job referenced).

- **`latent_domain_detector.py --seed` silently inserted 0 rows (fixed 2026-08-01)**: `insert_seeds()` used `INSERT OR IGNORE INTO experiences (ts, raw_text, hash, ...)` — but `experiences.content` is **NOT NULL** and wasn't provided, so every insert was silently swallowed (OR IGNORE suppresses constraint failures without raising), while the counter still printed "✅ Вставлено: 48". The script's own verification line "Всего семян в Cube: 0" exposed the lie. Fix: include `content` (set = raw_text) in the INSERT and count `cur.rowcount > 0` instead of unconditional `inserted += 1`. ALWAYS cross-check a script's reported insert count against `SELECT COUNT(*) FROM experiences WHERE source='<that-source>'` after any bulk-write script. Full pitfall: see `database-reliability` skill, section "INSERT OR IGNORE silently swallows constraint failures".

- **Cube DB lives at `cache/knowledge_cube.db`, NOT repo root**: a root-level `knowledge_cube.db` exists but is an empty stub (no tables). All three pipeline scripts and `kc_rag.py`/`knowledge_cube.py` connect to `HERMES_HOME/cache/knowledge_cube.db`. Query that path when verifying counts.

- **`kc_rag.upsert()` signature**: `upsert(content, tags="", source="", category="", importance=5, confidence=0.5, verification_method="manual", expiration_date=None)` — there is NO `domain=` or `outcome=` kwarg; passing them raises `TypeError`. Record pipeline outcomes with `category=` (e.g. 'devops') instead.

- **Autonomous Maintenance & Skill-Usage Pipeline (2026-07-31)**: New event-driven + cron fallback loop for detecting and fixing unused skills:
  - `scripts/skill_usage_analyzer.py` — scans all skills, checks feedback_store for 14-day usage, routes root causes:
    - No triggers → Suggestion Applier (add triggers)
    - Not in CLAUDE.md/AGENTS.md → Suggestion Applier (register skill)
    - Broken deps → Proactive Doer (fix deps)
    - Duplicates → Crystal (merge/delete)
    - No examples → Suggestion Applier (add examples)
    - Context shift → Knowledge Cube (reassess relevance)
  - `scripts/suggestion_applier.py` — consumes queue, applies fixes:
    - Registers skills in CLAUDE.md + .claude/rules/always.md
    - Adds Revisit frontmatter
    - Fixes verifier findings
  - Trigger: event `new_suggestions_ready` + cron fallback `*/30 * * * *` (every 30 min)
  - Threshold: 14 days unused (`days_unused = 0` if used <14d, `999` if no feedback record)
  - **Fixed nested payload bug** in suggestion_applier (lines 58-59): now extracts `inner = payload.get("payload", {})` before checking action
  - **Fixed applied_suggestions corruption**: `load_applied()` now handles dict-with-"failed" format
  - **KC hash constraint fix**: experiences.hash has UNIQUE constraint; compute content hash before INSERT

- **Skill Usage Analyzer + Suggestion Applier integration (2026-07-31)**: New autonomous maintenance loop:
  - `scripts/skill_usage_analyzer.py` — scans all skills, checks feedback_store for last 14-day usage, routes root causes:
    - No triggers → Suggestion Applier (add triggers)
    - Not in CLAUDE.md/AGENTS.md → Suggestion Applier (register skill)
    - Broken deps → Proactive Doer (fix deps)
    - Duplicates → Crystal (merge/delete)
    - No examples → Suggestion Applier (add examples)
    - Context shift → Knowledge Cube (reassess relevance)
  - `scripts/suggestion_applier.py` — consumes queue, applies fixes:
    - Registers skills in CLAUDE.md + .claude/rules/always.md
    - Adds Revisit frontmatter
    - Fixes verifier findings
  - Cron fallback: `suggestion-applier` every 30 min + event-driven on `new_suggestions_ready`
  - Threshold: 14 days unused (not 999) — `days_unused = 0` if used <14d, `999` if no feedback record
  - Fixed nested payload bug in suggestion_applier (lines 58-59): now extracts `inner = payload.get("payload", {})` before checking action
  - Fixed applied_suggestions corruption: `load_applied()` now handles dict-with-"failed" format

- **Skill audit was missing as background process**: The `skill` key in morning report (2304 entries, 100% maturity) is actually `skill_indexer.py` bulk indexing, NOT skill usage telemetry. The real audit (checking 523 SKILL.md files for validity, AGENTS.md presence, duplicates, stale skills, broken chains) was a manual trigger (g-009). Fixed in 2026-07-28:
  - Created `scripts/skill_audit.py` — full audit + chain validation + domain coverage
  - Added `skill_audit_complete` event to Chain Heartbeat (6h interval)
  - Cron job `skill-audit` runs every 360m (6h), fires event, updates `cache/skill_audit.json`
  - Morning report now sees fresh audit cache automatically

- **OMH / AgentReach modules registered but silent**: 16 modules in `MODULES` list (`omh_deep_research`, `omh_ralplan*`, `omh_ralph*`, `omh_autopilot`, `omh_triage*`, `agent_reach_youtube`, `agent_reach_web`, `agent_reach_github`, `agent_reach_rss`, `agent_reach_twitter`, `agent_reach_bilibili`) never call `beat()`. They appear SILENT in Chain Heartbeat, dragging module health to 7/23. Fix: add `from chain_heartbeat import beat` and `beat("module_name")` at startup of each component, or prune unused modules from `MODULES` list.

- **skill_indexer.py is not auto-triggered**: It only runs when manually invoked. New skills added to `skills/` directory are not indexed until someone runs it. Consider adding a file watcher or post-commit hook, or running it from `proactive_executor.py` on schedule.
- **Parallel execution is mandatory**: The 2026-07-26 remediation session proved that subagent batch deployment (8 parallel agents for 11 skill categories) completes in ~20min what took 2+ hours linearly. Always use `delegate_task` with multiple tasks for skill remediation across categories.
- **Heartbeat restoration before remediation**: System health (Chain Heartbeat) must be restored (events firing, modules beating, pipelines HEALTHY) BEFORE running skill security remediation — otherwise findings are polluted by silent modules and the system reports UNHEALTHY during the work.
- **proactive_executor.py is the single entry point**: All KC analysis, cron error scanning, fix application, gap detection, and skill evolution run in one script. Do not look for separate scripts.
- **LLM analysis timeout**: `proactive_executor.py` has a 45s LLM call deadline. When it expires, issues are written to `pending_analysis.json` for offline processing. The gap detection still runs but without LLM-generated fix suggestions.
- **Cron job fails silently**: The `self-evolution-cycle` cron job (ID: e4905470f419) tries to run the nonexistent 3-script pipeline and fails. If evolution isn't running, check and update the cron job in `cron/jobs.json` to point to `proactive_executor.py`.
- **DB locking**: `proactive_executor.py` fails with "database is locked" when `event_daemon`/`agent_daemon` hold WAL locks. **Fix**: Wait 5-10s or run outside peak hours.
- **Auto-evolution creates "Created skill" log for BOTH new skills AND existing skills receiving appended patterns**. Check `skills/<name>/` for new `.md` files vs. appended sections to existing `SKILL.md`.
- **Skill usage telemetry is sparse**: Only 4 skill_used events recorded (all June 2026). Consider adding instrumentation to `skill_view` and skill execution paths.
- The evolution engine only creates skills for domains with 20+ entries — small domains are skipped
- Skill names must not clash with existing skills (auto-prefixed with domain name)
- Manual skill edits may be overwritten if the auto-pattern section is present
- After evolution, run `/reload-skills` in-session to pick up new skills
- **"Created" in output is misleading** — the script logs "Created skill: X" for both brand-new SKILL.md files AND existing skills that got patterns appended. Most runs produce zero new files. Check timestamps or git diff to tell them apart.
- **Noisy auto-evolved patterns** — the extracted patterns often contain raw serialized JSON/metadata from the Knowledge Cube (skill frontmatter, serialized dicts, full tag lists). The quality is useful for discovery but not for direct consumption as clean documentation. Review and clean up manually if the patterns will be shown to a human.
- **State file is sparse** — `cron/skill_evolution_state.json` only stores `last_run` + `total`. If you need to know what changed in a specific run, capture the script's stdout at execution time or use git pre/post diff.
