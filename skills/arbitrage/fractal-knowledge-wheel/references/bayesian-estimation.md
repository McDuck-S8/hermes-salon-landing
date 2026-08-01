# Bayesian Estimation for Euler Circle Intersections

## Overview
Added in v3.0.0 (2026-07-16). Every intersection of Euler circles now carries a Bayesian probability estimate `P(success | evidence)` instead of just a color/category.

## Architecture

### Core Classes
- **`BayesianEstimator`** (dataclass) — encapsulates priors, likelihood factors, and estimation logic
- **`Intersection`** (dataclass) — extended with fields: `p_success`, `p_success_given_green`, `p_success_given_red`, `prior`, `evidence`

### Flow
```
EulerCirclesEngine.find_all_intersections()
    → finds all pair/triple/4+ intersections
    → _apply_bayesian_estimation()
        → BayesianEstimator.estimate() for each intersection
            → computes prior from intersection type
            → builds evidence from sector attributes
            → calculates posterior P(success)
    → returns intersections with Bayesian fields populated
```

## Priors (Base Rates)
| Intersection Type | Prior | Rationale |
|-------------------|-------|-----------|
| `system_core` (4+ green) | 0.95 | Platform ready, any offer/geo launches in days |
| `golden_core` (3 green) | 0.92 | Strong core, minimal friction |
| `golden` (2 green) | 0.85 | Ready pair, scalable |
| `growth` (2 yellow) | 0.55 | Potential, needs work |
| `mixed` (yellow+red) | 0.35 | Uncertain |
| `conflict` (green+red/yellow) | 0.40 | Depends on red/yellow severity |
| `isolated_strength` (1 green + 2 red) | 0.35 | Isolated resource |
| `core_conflict` (2 green + 1 red) | 0.25 | Blocker on strong core |
| `red` (2+ red) | 0.15 | Critical gaps |

## Likelihood Factors (Evidence)
| Factor | LR | Trigger |
|--------|-----|---------|
| `all_critical_green` | 2.5 | All critical sectors in intersection are green |
| `has_critical_red` | 0.3 | Any critical sector is red |
| `high_weight_green` | 1.8 | Green sector weight ≥ 1.2 |
| `low_fill_green` | 0.7 | Green sector fill < 70% |
| `intersection_strength` | 1.0 | Embedded in `strength` (0-1) |

## Posterior Calculation
Uses log-odds for numerical stability:
```
prior_odds = prior / (1 - prior)
log_post_odds = log(prior_odds) + Σ log(LR_i)
post_odds = exp(log_post_odds)
posterior = post_odds / (1 + post_odds)
```
Clamped to [0.05, 0.99].

## Specialized Estimates
- **`p_success_given_green`**: `0.5 + (avg_green_fill / 100) * 0.45` — linear 0.5→0.95
- **`p_success_given_red`**: `max(0.05, 0.3 + (avg_red_fill/100)*0.3 - 0.15*critical_count)`

## CLI Output
```bash
python fractal_wheel.py "topic" arbitrage euler
```
JSON output includes for each intersection:
```json
{
  "type": "golden",
  "circles": ["Трафик", "Платежи"],
  "strength": 0.88,
  "p_success": 0.9725,
  "p_success_given_green": 0.8938,
  "p_success_given_red": 0.9725,
  "prior": 0.85,
  "evidence": {"all_critical_green": 2, "intersection_strength": 0.875}
}
```

## Calibration Notes
- Priors can be calibrated from historical launch success rates
- Likelihood factors are heuristic; can be adjusted per domain
- Evidence factors currently don't query Knowledge Cube — future: integrate OKF white spots as uncertainty signals