# Crystal Iterative Run — 2026-07-13 (Session 2)

## Task
Run `python scripts/crystal.py --iterative 3` and verify:
1. Each cycle produces unique output (output ≠ input)
2. self_model.json updated with `studied` and `znu`

## Issues Found & Fixed

### 1. INSERT Schema Bug (FIXED)
**File:** `scripts/crystal.py` line 3030-3033
**Error:** `sqlite3.IntegrityError: NOT NULL constraint failed: experiences.content`
**Root Cause:** `record()` function INSERT missing required `content` column (schema: `content TEXT NOT NULL`, `raw_text TEXT NOT NULL`)
**Fix:** Updated INSERT to include both `content` and `raw_text`:
```sql
INSERT INTO experiences (ts, content, raw_text, hash, axis_time_hour, axis_time_dow, axis_domain, axis_outcome, source)
VALUES (?, ?, ?, ?, ?, ?, 'crystal', 'snapshot', 'crystal')
```

### 2. Exhausted Source Tracking (NOT FIXED - Root Cause)
**Problem:** All 3 cycles chose identical action:
```
→ Воля: fabric не содержал новых сущностей (200 записей, 0 кандидатов) — нужен другой подход
```

**Root Cause:** 
- `_self_discover()` found `fabric` source with 2156 files → added `extract_fabric` candidate
- `will()` selected it → `_execute_extract('fabric')` returned 0 candidates
- But `done_sources` tracking in `will()` uses `historical_ids` (action IDs like `extract_fabric`), NOT the source name
- Next cycle: `fabric` NOT in `done_sources` → `_self_discover()` adds `extract_fabric` AGAIN
- Cycle repeats infinitely

**Required Fix in `will()` function:**
```python
# After action execution, add SOURCE to done_sources, not just action_id
if chosen.get('source'):
    done_sources.add(chosen['source'])  # This exists but...
```
Actually the code HAS this at line 1989-1990:
```python
if chosen.get('source'):
    done_sources.add(chosen['source'])
```
But it's inside the `will()` function's local scope — `done_sources` is recreated every `will()` call!

**The Fix:** `done_sources` must be persisted across cycles. Options:
1. Save to `self_model.json` (already has `sovest.studied`)
2. Save to KC as `crystal_will` entry with source tracking
3. Use global/module-level cache

### 3. Undefined Constant (SELF_MODEL_PATH)
**File:** `scripts/crystal.py` line 1575
**Error:** `NameError: name 'SELF_MODEL_PATH' is not defined` (silently caught by bare `except`)
**Fix:** Define constant at module top:
```python
SELF_MODEL_PATH = os.path.join(ROOT, "cache", "self_model.json")
```

## Execution Results (After INSERT Fix)

### Cycle 1/3 (15:09:56)
- KC: 2605 entries
- EE: 3290 entities, 0 relations
- **Action**: `extract_fabric` → 0 new entities (exhausted)

### Cycle 2/3 (15:10:18) — IDENTICAL
- KC: 2605 entries  
- EE: 3290 entities, 0 relations
- **Action**: `extract_fabric` → 0 new entities (exhausted)

### Cycle 3/3 (15:10:41) — IDENTICAL
- KC: 2605 entries
- EE: 3290 entities, 0 relations
- **Action**: `extract_fabric` → 0 new entities (exhausted)

❌ **FAILED: Output = Input** — all 3 cycles identical

## self_model.json Verification (After Runs)
```json
{
  "last_cycle": "2026-07-13T15:14:31",
  "cycle_count": 130,
  "sovest": {
    "studied": 5 entries,  // after clean_studied.py trim
    "assessments": 20 entries
  },
  "znu": 25 keys
}
```

### studied (5 - last 5 after trim)
- music-audio, learning, bugfix, communication, dimension_proposals

### znu (25 keys)
- bugfix, music-audio, crystal, dimension_proposals, lavra_decision, design, architecture, crystal_discovery, file_ops, data, cube_analysis, uncategorized, skill, social-media, video-content, crystal_will, coding, research, debugging, creative, latent-domain-detector, improvement_suggestions, learning, communication, social-media, communication

## Observations
- ✅ Database INSERT bug fixed — cycles now complete without error
- ✅ self_model.json persists and updates correctly across cycles
- ✅ `studied` correctly trimmed to 5 entries
- ✅ `znu` contains 25 learned summaries
- ❌ **Unique action per cycle FAILED** — crystal repeats exhausted action
- ❌ Entity Engine growth stalled at 3290 (no new entities extracted)

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
print('studied:', d['sovest']['studied'])
print('znu:', len(d['znu']), list(d['znu'].keys()))
"
```

## Summary
| Requirement | Status |
|-------------|--------|
| INSERT bug fixed | ✅ |
| 3 unique cycles | ❌ (all identical) |
| self_model has studied | ✅ (5 entries) |
| self_model has znu | ✅ (25 entries) |
| SELF_MODEL_PATH defined | ❌ (still missing) |

## Next Steps
1. Define `SELF_MODEL_PATH` constant at module level
2. Fix exhausted source tracking — persist `done_sources` across `will()` calls
3. Re-run and verify unique outputs per cycle