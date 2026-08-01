# Lessons Learned — Crystal Self-Awareness Session 2026-07-14

## Key Findings

### 1. Identical Output Across Iterations is Normal
- Crystal.py reads state (KC, EE, FL, Fabric) — it's an **observer**, not a writer
- If no new data was added to sources between cycles, output will be identical
- This is NOT a bug — it's correct behavior: same state → same observation

### 2. `studied` Cache Must Be Cleared Before Re-run
- `studied` tracks which domains/sources the conscience has already explored
- If not cleared, crystal prioritizes **unstudied** domains (via `learning_direction` generation)
- Clearing `studied = []` (or keeping last 5) forces fresh exploration
- **Action**: Always clear `cache/self_model.json` → `sovest.studied` before iterative runs

### 3. `znu` Population Happens Post-Conscience, Not During Observation
- `znu` (знаю/не знаю) is updated in `_evaluate_conscience_learning()`
- Called AFTER conscience actions execute (`conscience_blindspot_*`, `conscience_deepen_*`, `conscience_audit_*`)
- Observation phase (`observe()`) only fills `znayu`/`umeyu`/`ne_znayu`
- **Expectation**: znu grows only when crystal actually **acts**, not when it watches

### 4. To Get New Actions, Feed New Data First
- Crystal generates actions from: orphan sources, improvement_suggestions clusters, agency agents, fabric, state_db intents
- If KC is static → crystal repeats same assessment
- **Real workflow**: run sensors/scrapers → import Fabric → spawn agent tasks → THEN run crystal

## Practical Checklist for Next Run

- [ ] Clear `sovest.studied` in self_model.json
- [ ] Run data acquisition first (sensor_array, web_surfer, fabric import)
- [ ] Run `python scripts/crystal.py --iterative 3`
- [ ] Verify: cycle outputs differ OR new conscience actions appear
- [ ] Verify: `znu` has new entries matching executed actions
- [ ] Verify: `studied` appended with new domains