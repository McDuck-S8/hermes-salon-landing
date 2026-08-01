---
name: autonomous-ripple-engine
version: 1.0.0
category: self-improvement
description: "Autonomous daily knowledge processing engine - reads raw data stones, builds impact circles, detects mature keys, generates modern dark dashboards. Implements the user's autonomous protocol: run daily at 9:00, process stones, build circles, unlock mature keys, show visual map."
tags: [autonomous, knowledge-processing, dashboard, visualization, ripple-engine, event-driven, daily-cron]
---

# Autonomous Ripple Engine

**Autonomous daily knowledge processing system** that implements the user's protocol:
1. **Daily autonomous execution** (9:00 AM) - no user command needed
2. **Stone processing** - reads raw data, computes differentiated scores
3. **Circle building** - groups stones by shared aspects and keys
4. **Mature key detection** - finds converging keys across multiple stones
5. **Auto-unlock** - mature keys unlock without user intervention
6. **Visual map** - single HTML dashboard with gradient cards by importance
7. **User-only direction** - user observes and points; engine acts

## When to Use

- Daily autonomous knowledge processing runs
- Building impact maps from heterogeneous data sources
- Detecting convergent signals across multiple data points
- Generating executive dashboards for autonomous agents
- Any "throw stones, build circles, find mature keys" workflow

## Architecture

### Core Components

```
ripple_engine.py                    # Main engine (scripts/)
├── Stone class                     # Differentiated scoring (strength, confidence, tier)
├── RippleEngine class              # Orchestration
│   ├── gather_daily_stones()       # From ripple_keys/*.json + KC fallback
│   ├── build_circles()             # Aspect + key intersections
│   ├── calculate_mature_keys()     # Convergence detection
│   ├── unlock_mature_keys()        # Auto-unlock
│   └── generate_html_visualization() # Dark gradient dashboard
└── DESIGN_TOKENS                   # From ui-ux-pro-max
    ├── colors (dark theme + gradients)
    ├── spacing, radius, shadows
    └── typography (JetBrains Mono + Space Grotesk)
```

### Data Sources

| Source | Path | Format |
|--------|------|--------|
| Ripple keys | `cache/ripple_keys_*.json` | YouTube/Partnerkin processed |
| Knowledge Cube | `cache/knowledge_cube.db` | SQLite experiences table |
| Improvement suggestions | `cache/improvement_suggestions.json` | Self-improvement loop |

### Stone Scoring (Differentiated)

```python
# Not fake 80/80 everywhere - real computation:
key_strength  = base + aspects*3 + keys*5 - conflicts*5 - gaps*3  # 10-100
confidence    = base + actionable*10 - gaps*4 - conflicts*5 + specific_keys*3  # 15-100
priority_tier = critical(>=85/85) | high(>=75/75) | medium(>=60/60) | low
visual_weight = (strength + confidence) / 2  # for card sizing
actionable    = strength>=70 AND confidence>=75 AND no_conflicts
```

### Maturity Criteria (Convergence-Based)

```python
is_mature = (
    count >= 2 and                    # Multiple stones
    avg_strength >= 65 and            # Strong signal
    avg_confidence >= 55              # Reliable
)
# actionable_ratio used for display only, not gating
```

### Dashboard Design (ui-ux-pro-max tokens)

- **Dark theme**: `#0A0E17` background, radial glow orbs
- **Gradient cards by tier**: critical=red, high=purple, medium=cyan, low=gray
- **Visual hierarchy**: Card size = visual_weight, hover lift + glow
- **Typography**: JetBrains Mono (mono) + Space Grotesk (display)
- **Animations**: Staggered entrance, hover transitions
- **Responsive**: Auto-fit grids, stat pills, summary cards

## Usage

```bash
# Manual run
python scripts/ripple_engine.py

# Cron (9:00 AM daily)
# Add to cron/jobs.json:
# "ripple_engine": {"schedule": "0 9 * * *", "script": "scripts/ripple_engine.py"}
```

## Output

- **HTML Dashboard**: `cache/reports/daily_ripple_map.html` (single file, ~500KB)
- **Console Log**: Stone count, circles, mature keys unlocked
- **Unlocked Keys**: Printed to stdout, ready for downstream consumption

## Integration Points

| Component | Integration |
|-----------|-------------|
| `event_evolution.py` | Fires `architecture_scan_complete` after run |
| `chain_heartbeat.py` | Module heartbeat on completion |
| `ui-ux-pro-max` | Design tokens, color palettes, component patterns |
| Knowledge Cube | Reads experiences, could write mature keys back |

## Pitfalls & Fixes

| Issue | Fix |
|-------|-----|
| All stones same score (80/80) | Compute differentiated scores from aspects, keys, conflicts, gaps |
| Confidence 0-1 vs 0-100 | Normalize: `conf * 100 if float <= 1 else conf` |
| Actionable string "true" | Normalize: `str(val).lower() == "true"` |
| Deduplication loses data | Use URL first, then full title |
| Maturity too strict (0 keys) | Gate on convergence (count>=2, avg_str>=65, avg_conf>=55), not actionable_ratio |
| Dashboard empty | Check `_deduplicate()` not filtering all stones |
| Mature keys not persisted | Add `_persist_mature_keys()` writing to KC experiences table with axis_domain=mature_key |
| Duplicate mature key entries | Use `INSERT OR IGNORE` with hash on `mature_key:{key}:{unlocked_at}` |
| KC schema mismatch | Use kc_entries table (id, content, tags, source, category, importance, created_at, confidence) not experiences |
| **Morning report protocol** | Engine now auto-runs at 9:00 AM, generates visual map, prints mature keys to stdout for user direction |
| **Mature key rotation** | Mature keys now unlock sequentially (1 per day max), not all at once — prevents overload |

## References

- `references/design-tokens.md` - DESIGN_TOKENS dict extracted from ui-ux-pro-max
- `references/scoring-formula.md` - Full stone scoring math
- `references/maturity-criteria.md` - Convergence detection logic
- `templates/ripple_dashboard.html` - Base HTML template (for reference)
- `scripts/ripple_engine.py` - Main implementation

## Related Skills

- `event-driven-self-improvement-pipeline` - Parent pipeline pattern
- `ui-ux-pro-max` - Design system tokens
- `crystal-architecture-awareness` - Module health monitoring
- `closed-loop-autonomy` - Producer/consumer principle
- `kairos-lite` - Lightweight proactive scheduling
- `ripple-engine` (data-science) - KC entry analysis methodology (v1, complementary)