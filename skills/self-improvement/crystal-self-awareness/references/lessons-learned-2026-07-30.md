# Lessons Learned — Crystal Self-Awareness Session 2026-07-30

## Session Summary
Ran crystal self-awareness loop 3 iterations as scheduled cron job. Verified output uniqueness and self_model.json update.

## Execution Trace

### First Run (without clearing studied)
```
ЦИКЛ 1/3: Action → "fabric не содержал новых сущностей (200 записей, 0 кандидатов) — ну"
ЦИКЛ 2/3: Action → "fabric не содержал новых сущностей..." + "Углубление 'debugging': 13026 записей..."
ЦИКЛ 3/3: Action → "fabric не содержал..." + "Аномалия 'data': [failure=40, success=5, unknown=115]..."
```
**Problem**: Cycles 1-2 nearly identical (only counter increments). Cycle 3 adds anomaly but still "all done" pattern.

### Studied Cache Cleared
Removed `log_agent` from `sovest.studied` (kept last 5: `terminal`, `finance`, `debugging`, `dimension_proposals`, `data`)

### Second Run (after clearing studied)
```
ЦИКЛ 1/3: Action → "Аудит источника 'log_agent': 79 записей, домены: coding(36), bugfix(16), devops(7)"
ЦИКЛ 2/3: Action → "Аудит источника 'agent_decisions': 122 записи, домены: devops(77), bugfix(22), creative(10)"
ЦИКЛ 3/3: Action → "Аномалия 'uncategorized': [success=5, unknown=70]..."
```
**Result**: ✅ Each cycle produced UNIQUE action — different source audited each iteration.

## Verification Results

### self_model.json Updated ✅
- **studied**: 8 entries (terminal, finance, debugging, dimension_proposals, data, log_agent, agent_decisions, uncategorized)
- **znu**: 8 entries matching all conscience actions executed:
  - log_agent → audit summary
  - terminal → blindspot summary
  - finance → blindspot summary
  - debugging → deepen summary
  - dimension_proposals → audit summary
  - data → anomaly summary
  - agent_decisions → audit summary
  - uncategorized → anomaly summary

### System State (Cycle 3)
- KC: 23,957 entries (+15,213 in 7d, 63% growth)
- Dominant domain: failure (13,719)
- EE: 3,672 entities, 201 connections (0.05 connectivity)
- Phase: 🔄 Synthesis → next ⚡ Autonomy (26% progress)
- Orphans: 42 (0%) — healthy

## Key Confirmation
**The workflow in `run_crystal_self_awareness.py` is correct and complete:**
1. Run crystal → check unique outputs
2. If "all done" pattern (same action repeated) → clear studied to last 5
3. Re-run crystal → verify unique actions
4. Verify self_model.json has studied + znu populated

No code changes needed. The pattern is documented and working.

## Next Session Checklist
- [ ] Data acquisition first (sensor_array, web_surfer, fabric import)
- [ ] Clear studied before iterative run
- [ ] Run `python scripts/crystal.py --iterative 3`
- [ ] Verify unique actions per cycle
- [ ] Verify znu growth matches executed actions