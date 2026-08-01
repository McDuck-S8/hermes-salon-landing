# Cache Cleanup and Dead Scripts Pattern (2026-06-25)

## Cache Cleanup
Before deleting, SCAN for value:
1. List all .py files in cache/
2. Quick scan: check for API calls, DB access, LLM usage, Telegram, crypto
3. Extract insights from valuable files BEFORE deleting
4. Move to trash, verify nothing broke, then delete

## What I Found (2026-06-25)
- 42 stale files: tmp_*, fetch_yt*, test_ddg*, yt_hack*
- 3 valuable insights extracted:
  - Crimea family budget data (budget_calc.py) — useful for arbitrage
  - Direct event logging pattern (direct_log.py) — lightweight logging
  - KC classification pattern (boot_actions.py) — keyword-based domain assignment
- All 3 recorded to KC before deletion

## Dead Scripts Cleanup
- 220 scripts in scripts/, 122 known dead in _dead_scripts.json
- Move to _deprecated/ (NOT delete) — preserves history
- After cleanup: 53 active scripts (was 220)
- Verify: no broken imports after moving

## Decision Matrix
| Situation | Action |
|-----------|--------|
| File in _dead_scripts.json | Move to _deprecated/ |
| File not imported by anything | Move to _deprecated/ |
| File in cache/tmp_* | Delete (after scanning for value) |
| File in cache/*.py | Scan first, extract insights, then delete |
| File in _deprecated/ | Keep — dont touch |
