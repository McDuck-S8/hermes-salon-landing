# Skill Auto-Evolution v2

Engine that evolves Hermes skills from Knowledge Cube data, replacing the broken v1.

## Location
- Script: `scripts/skill_evolution_v2.py`
- State: `cron/skill_evolution_state.json`
- Cron: job `674a3eb0561e` (skill-evolution), schedule `0 4 * * *`, no_agent=True

## Flow
1. Read Knowledge Cube (`cache/knowledge_cube.db`) — count entries, group by domain
2. For each domain with 20+ entries:
   - If no skill exists → create one with extracted patterns
   - If skill exists → append Auto-evolved patterns section
3. Extract insight-worthy patterns (sentences containing: always, never, must, should, важно, remember, tip, etc.)
4. Report created/updated skills

## Domain → Skill Mapping (First Run 2026-06-07)
| Domain | Created/Updated Skill |
|--------|---------------------|
| coding | coding-patterns (NEW) |
| research | research-paper-writing (UPDATED) |
| browser | agent-browser (NEW) |
| file_ops | file_ops (NEW) |
| communication | communication (NEW) |
| uncategorized | uncategorized (NEW — placeholder) |
| systematic-debugging | systematic-debugging (UPDATED) |

## What v2 Fixed vs v1 (old skill_evolution_cron.py)
- v1 used `_HERMES_HOME.parent` → resolved to wrong directory
- v1 looked for `data/plugins/self-evolution/` which doesn't exist in current setup
- v1 referenced non-existent simple_evolve.py
- v2 directly reads Knowledge Cube SQLite DB
- v2 doesn't need hermes CLI (hermes skills install timed out)
- v2 with `LIMIT` typo fixed (was LIMIMT — crashed on domain queries)

## Uncategorized Problem (SOLVED 2026-06-07)

**Before:** 366/619 entries (59%) tagged `uncategorized`. Engine found themes via keyword frequency but couldn't create meaningful skills for raw session dumps.

**Solution:** `cube-categorizer` cron (every 6h, job `faaa775374fb`) now classifies uncategorized entries via keyword heuristics:
- 94 entries categorized in first run (366 → 272 uncategorized)
- Added: debugging, terminal domains
- Script: `scripts/cube_categorizer.py` — supports `--dry-run`

The remaining 272 are short conversational fragments that legitimately stay uncategorized. The categorizer runs every 6h, so new entries get labeled before the next skill-evolution run.

## Pitfall: Name Collisions
The engine creates skills under the first matching `DOMAIN_SKILL_MAP` name. If a skill already exists under a different name for the same domain (e.g. `research` mapped to `research-paper-writing` but a skill named `research` also exists), the engine may update the wrong one. Currently uses `find_skill_dir(name_fragment)` which does substring matching — first match wins.

## Pitfall: `hermes skills install` Times Out
Calling `hermes skills install <name>` from within a cron script hangs (15s timeout in v1). v2 writes SKILL.md files directly into the skills directory — no CLI needed.
