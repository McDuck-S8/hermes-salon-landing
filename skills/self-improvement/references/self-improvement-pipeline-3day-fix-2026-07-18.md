# Self-Improvement Pipeline — 3-Day Conversion Fix (2026-07-18)

## Problem Statement
**Self-improvement conversion: 0.27%** (17,704 suggestions → 19 skills over 32 runs)

### Root Causes Identified (Autopsy)
1. **Verified Fixes pipeline dead** — `verified_fixes.db` empty, `knowledge_cube.db` empty, `events.db` cross-connection broken
2. **Log noise dominates** — `log_artifact` (141), `telegram_timeout` (150) counted as "critical" errors
3. **Auto-skills are templates, not code** — 19 skills are TODO checklists, no executable fixes
4. **No consumer for suggestions** — `improvement_suggestions.json` written, never read/acted on
5. **Cross-run dedup missing** — same suggestions regenerated daily

## 3-Day Fix Plan

### Day 1 (2026-07-18) — **COMPLETE** ✅
- [x] Initialize Knowledge Cube schema (`get_db()` call)
- [x] Create `verified_fixes.db` with proper schema + indexes
- [x] Fix `events.db` cross-connection visibility (`isolation_level=None` + WAL)
- [x] Wire `event_evolution.py:on_error()` and `on_task_complete(verified=True)` to write directly to `verified_fixes.db`
- [x] Verify `self_improvement_loop.py` reads populated DBs → generates suggestions from REAL fixes

**Result:** `verified_fixes` now has 7 entries, `command` cluster detected at count=30, suggestions generated from real data.

### Day 2 (2026-07-19) — Noise Filtering + Executable Skills
- [ ] Filter log noise in `analyze_error_patterns()`:
  - Exclude `log_artifact` (successful logging, not errors)
  - Exclude `telegram_timeout` (infrastructure, not code bugs)
  - Exclude `terminal_timeout` (resource limit, not pattern)
  - Minimum cluster count: 3 (already implemented)
- [ ] Convert auto-skill generation from template → executable:
  - Generate `.patch` file with actual fix
  - Generate test case (`test_<skill>.py`)
  - Store in `skills/auto-generated/<name>/fix.patch` + `test_<name>.py`
- [ ] Add skill validation: `python -m py_compile` on generated skill code

### Day 3 (2026-07-20) — Close the Loop
- [ ] Create `scripts/apply_top_suggestion.py` cron job:
  - Read `improvement_suggestions.json`
  - Pick top critical suggestion with executable fix
  - Apply patch, run test, verify
  - Emit `knowledge_added` event on success
- [ ] Wire suggestion → skill → verification → KC entry full cycle
- [ ] Target: **1% conversion** (177 skills from 17,704 suggestions)

## Key Technical Lessons (Embed in Skills)

### 1. Write Path > Read Path
The self-improvement loop's `load_verified_fixes()` was correct. The bug was **nothing wrote to it**. Always verify write path exists before optimizing read path.

### 2. Cross-Connection SQLite Visibility
Default SQLite connection (`isolation_level=""`) uses DEFERRED transactions. Commits from Connection A are **not visible** to Connection B until B's transaction ends. Fix: `isolation_level=None` (AUTOCOMMIT) + WAL mode.

### 3. Hook Wiring Pattern
```python
def on_error(...):
    emit_event(...)        # async event bus for other consumers
    write_verified_fix(...) # sync write for self-improvement loop
```
Dual-write ensures both real-time event consumers AND batch analysis have data.

### 4. Noise Classification Before Clustering
Classify errors by root-cause library (`httpx`, `httpcore`, `telegram`, `api`) BEFORE clustering. Single-occurrence "unknown" clusters = noise.

### 5. Verified Fix Definition
A "verified fix" requires: `issue_type`, `fix_description`, `evidence`, `tags`, `source`, `verified_at`. Not just an error message.

## Metrics to Track
| Metric | Day 1 | Day 2 Target | Day 3 Target |
|--------|-------|--------------|--------------|
| Verified fixes in DB | 7 | 50+ | 200+ |
| Recurring fix clusters | 1 | 10+ | 30+ |
| Noise suggestions filtered | 0% | 80% | 90% |
| Executable auto-skills | 0 | 5 | 20 |
| Suggestion→skill conversion | 0.27% | 0.5% | **1%** |

## Files Created/Modified
- `scripts/knowledge_cube.py` — unified path via `hermes_config.CACHE_DIR`
- `scripts/event_evolution.py` — direct writes to `verified_fixes.db`, fixed events.db
- `scripts/self_improvement_loop.py` — already correct, now reads real data
- `skills/self-improvement/references/verified-fixes-hooks-day1-2026-07-18.md` — this session's detail
- `skills/self-improvement/references/self-improvement-pipeline-3day-fix-2026-07-18.md` — this summary

## Next Session Kickoff
```bash
# Verify pipeline health
python -c "
from scripts.self_improvement_loop import load_verified_fixes, load_cube_experiences
fixes = load_verified_fixes()
exp = load_cube_experiences()
print(f'Verified fixes: {len(fixes)}')
print(f'KC experiences: {len(exp)}')
from scripts.hermes_hooks import get_hooks
h = get_hooks()
h.on_error('Test error', 'Test fix', ['test'])
h.on_task_complete('Test', 'Fixed', ['test'], verified=True, evidence='Applied fix X')
"
# Should show growing counts
```