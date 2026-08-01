# Pipeline Reality Check — 2026-07-25

## What Was Tested

Ran cron job with pipeline:
1. `python scripts/skill_indexer.py` — **SCRIPT NOT FOUND**
2. `python scripts/latent_domain_detector.py --seed` — **SCRIPT NOT FOUND**
3. `python scripts/skill_evolution_v2.py` — **SCRIPT NOT FOUND**

Also checked for `dimension_discovery.py` — **SCRIPT NOT FOUND**
Also checked `scripts/_deprecated/` — **DIRECTORY EMPTY**

## What Works

The only existing script that performs the self-improvement pipeline:

```bash
cd /d/Portable_Soft/hermes
python scripts/proactive_executor.py
```

Single run output (91s):
- Phase 1: KC Analysis — 12,970 experiences, 44 domains, 2,447 uncategorized
- Phase 2: Cron Error Scan — 12 failing jobs detected
- Phase 2.5: LLM Analysis — 45s timeout, issues saved to pending_analysis.json
- Phase 3: Fix application — PRAGMA optimize, no auto-fixes possible
- Phase 4: Gap detection — 27 white spots, 3 tasks generated
- Phase 4c: Skill Evolution — 16 patterns found, all duplicates (skipped)

## Action Needed

The cron job at `cron/jobs.json` (job ID: e4905470f419) specifies a pipeline that doesn't exist: `skill_indexer → latent_domain_detector --seed → skill_evolution_v2`. This job will always fail. Update it to run `python scripts/proactive_executor.py` instead.

## Knowledge Cube State at Check

| Metric | Value |
|---|---|
| Experiences | 12,970 |
| DB size | 25.4 MB |
| Uncategorized | 2,447 (18.9%) |
| White spot clusters | 57 |
| Dimensions | 5 |
| Skill entries | 1,542 |
| Physical SKILL.md files | 496 |
