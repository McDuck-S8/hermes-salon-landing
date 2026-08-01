# Changelog — Fractal Knowledge Wheel

## v5.0.0 (2026-07-16) — Landscape + Transparency Layers

**Added:**
- **4-layer knowledge architecture** (military map metaphor): Landscape (permanent) + Situation/Plans/Logistics (replaceable transparent overlays)
- `layer_type` field for `kc_entries` and `experiences`: `landscape` | `situation` | `plans` | `logistics`
- `overlay_on` field — JSON array of parent layer keys this entry depends on
- `geometry` field for Plans layer — arrows with from→to, ROI, probability, blocking factors
- Migration path: backfill existing → Situation, extract Landscape from high-confidence entries, build Plans from Euler/Key Strength, build Logistics from critical red sectors
- SQL query patterns for composing full picture across layers

**Integration with Fractal Wheel:**
| Mode | Reads | Writes |
|------|-------|--------|
| Analysis | Landscape | Situation (current gaps) |
| Synthesis | Landscape + Situation | Plans (novel keys) |
| Euler | Plans + Situation | Key Strength |
| Key Strength | All 4 layers | Key Strength score |

**File:** `references/landscape-transparency-architecture.md`

---

## v4.0.0 (2026-07-16) — Key Strength Assessment

---

## v3.0.0 (2026-07-16) — Bayesian Estimation

**Added:**
- `BayesianEstimator` class — байесовская оценка P(success | evidence) для каждого пересечения
- `Intersection` dataclass extended: `p_success`, `p_success_given_green`, `p_success_given_red`, `prior`, `evidence`
- Prior base rates by intersection type: system_core=0.95, golden_core=0.92, golden=0.85, growth=0.55, conflict=0.40, core_conflict=0.25, isolated_strength=0.35, mixed=0.35, red=0.15
- Likelihood factors: all_critical_green=2.5, has_critical_red=0.3, high_weight_green=1.8, low_fill_green=0.7, previous_success=3.0, previous_failure=0.2
- Posterior via log-odds update
- `_apply_bayesian_estimation()` called automatically in `find_all_intersections()`

---

## v2.0.0 (2026-07-16) — Euler Circles (Mode 3)

**Added:**
- `EulerCircle` dataclass — radius = weight × fill_percent, area, color
- `EulerZone` dataclass — zone_type (green/red/conflict), sectors, fill_percent, min/max fill, action, reasoning, resource_waste
- `EulerCirclesEngine` — find_intersections(), classify zones, get_golden_sections(), get_critical_gaps(), get_conflicts(), get_growth_zones(), synthesize_from_green_intersections()
- Zone classification: green (all green), red (all red), conflict (mixed green+red), growth (all yellow)
- Conflict detection: green sector ∩ red sector = resource waste

---

## v1.1.0 (2026-07-16) — Synthesis (Mode 2)

**Added:**
- `SynthesisEngine` — Entity extraction from Knowledge Cube, compatible pair building, SynthesizedKey generation
- `Entity` dataclass — type (traffic/bridge/offer/geo/payment/withdrawal/tool), name, compatibility scores
- `SynthesizedKey` dataclass — name, compatibility_score, novelty_score, description, reasoning, entities
- Fixed: sorted keys for compatible_pairs (frozenset), frozenset for intersection matching

---

## v1.0.0 (2026-07-16) — Analysis (Mode 1)

**Added:**
- `Sector` dataclass — id, name, weight, critical, fill_percent, facts, gaps, status (🟢/🟡/🔴)
- `WheelAssessment` — overall_percent, green/yellow/red/critical_red sectors, priority_tasks
- `FractalWheel` class — build_wheel(), assess_gaps(), run_analysis_mode(), run_synthesis_mode(), run_euler_mode()
- Domain sectors: arbitrage (8), ai-ofm (8), craft (8), default (6)
- HTML report template

---

## 1.1.0 (2026-07-16) — Legacy
- **Verified** all core functionality via ad-hoc test suite
- **Added** `references/verification.md` with test results
- **Updated** SKILL.md to v1.1.0 with verified timestamp
- **Fixed** `create_tasks()` to handle dict/list goal_queue correctly
- **Added** `recurse_on_critical_red()` method for fractal recursion
- **Updated** `generate_html()` with fallback template support

## Planned (1.2.0 / 5.0.0)
- [ ] Integrate `assess_gaps()` with Knowledge Cube (`knowledge_cube.py`)
- [ ] Implement Jinja2 rendering for HTML template
- [ ] Auto-run sub-wheels in `recurse_on_critical_red()`
- [ ] Add CLI subcommands for individual operations
- [ ] Add sector weight configuration via YAML

## Known Issues
1. `assess_gaps()` uses mock data — needs Knowledge Cube integration
2. `generate_html()` falls back to string replacement without Jinja2
3. `recurse_on_critical_red()` creates sub-wheels but doesn't auto-run them
4. HTML template uses Jinja2 syntax not yet rendered by current implementation