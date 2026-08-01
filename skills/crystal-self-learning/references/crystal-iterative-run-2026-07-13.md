# Crystal Iterative Run — 2026-07-13

## Task
Run `python scripts/crystal.py --iterative 3` and verify:
1. Each cycle produces unique output (output ≠ input)
2. self_model.json updated with `studied` and `znu`

## Pre-conditions
- `cache/entity_engine.db` was empty (0 bytes, no tables)
- `scripts/crystal.py` had schema bug in `_self_discover()` query (wrong column names)

## Fixes Applied
1. **Fixed SQL query in crystal.py** — changed `r.source_entity_id` / `r.target_entity_id` → `r.source_id` / `r.target_id` (see `self-improvement/references/crystal-schema-fix-2026-07-13.md`)
2. **Initialized entity_engine.db** — ran `python scripts/init_entity_engine.py` → created tables, seeded 101 entities / 11 types

## Execution Results
Ran `python scripts/crystal.py --iterative 3`:

### Cycle 1/3 (02:43:37)
- KC: 2605 entries, 6% orphans (150)
- EE: 101 entities, 0 relations
- **Action**: Extracted 2397 new entities from white-spot-explorer (168 records)
- EE grew to 2498 entities

### Cycle 2/3 (02:44:03)
- KC: 2605 entries, 0% orphans (3)
- EE: 2498 entities, 0 relations
- **Action**: Extracted 649 new entities from fabric (200 records)
- EE grew to 3147 entities

### Cycle 3/3 (02:44:25)
- KC: 2605 entries, 0% orphans (2)
- EE: 3147 entities, 0 relations
- **Action**: Fabric exhausted (0 new candidates) — "нужен другой подход"

✅ **Each cycle produced unique output** — different actions, different entity counts, different decisions

## self_model.json Verification (after runs)
```json
{
  "last_cycle": "2026-07-13T02:49:45",
  "cycle_count": 130,
  "sovest": {
    "studied": 20 entries,  // trimmed to last 5 per instructions
    "assessments": 20 entries
  },
  "znu": 23 keys
}
```

### studied (20, now 5)
- Before trim: crystal_discovery, file_ops, data, cube_analysis, uncategorized, skill, social-media, video-content, crystal_will, coding, research, debugging, creative, latent-domain-detector, improvement_suggestions, music-audio, learning, bugfix, communication, dimension_proposals
- After trim (last 5): improvement_suggestions, music-audio, learning, bugfix, communication

### znu (23 keys)
- bugfix, music-audio, crystal, dimension_proposals, lavra_decision, design, architecture, crystal_discovery, file_ops, data, cube_analysis, uncategorized, skill, social-media, video-content, crystal_will, coding, research, debugging, creative, latent-domain-detector, improvement_suggestions, learning, communication

## Observations
- Crystal now correctly processes iterative cycles
- EE growth: 101 → 2498 → 3147 entities across 3 cycles
- Orphans reduced from 6% → 0%
- self_model persists and updates correctly across cycles
- The `studied` list tracks what domains/sources were analyzed, `znu` captures "what I now know" summaries

## Commands for Verification
```bash
# Check crystal runs
python scripts/crystal.py --iterative 3

# Check self_model
python -c "
import json
with open('cache/self_model.json') as f: d=json.load(f)
print('last_cycle:', d['last_cycle'])
print('cycle_count:', d['cycle_count'])
print('studied:', len(d['sovest']['studied']), d['sovest']['studied'])
print('znu:', len(d['znu']), list(d['znu'].keys()))
"
```