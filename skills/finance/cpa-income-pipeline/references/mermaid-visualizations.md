# Mermaid Visualizations for CPA Income Pipeline

The `income_status_report.py` script generates 4 native GitHub-rendered Mermaid diagrams in `reports/income_pipeline_status.md`.

## Quick Reference

```bash
# Regenerate visual report
python scripts/income_status_report.py
# Open reports/income_pipeline_status.md in GitHub
```

## Diagram Summary

| Diagram | Type | Key Insight |
|---------|------|-------------|
| **Status Distribution** | `pie` | 47 UNVERIFIED, 2 TESTING, 1 VERIFIED, 34 code-unblockable |
| **Blocker Distribution** | `bar` | AD_BUDGET (47) dominates; LANDING_PAGE (25), BOT (15), VIDEO_SCRIPT (10) are code-fixable |
| **Pipeline Flow** | `flowchart TD` | Generators → Deploy → Code-unblockable → TESTING → VERIFIED |
| **Priority Matrix** | `quadrantChart` | Quick Wins (🟢) = code-unblockable + TESTING/VERIFIED; Avoid (🔴) = manual-only |

## Integration with Components

The pipeline flowchart explicitly maps scripts to blockers they unblock:
- `landing_generator.py` → LANDING_PAGE (25 schemes)
- `video_scripts.py` → VIDEO_SCRIPT (10 schemes)  
- `cpa_bot_generator.py` → BOT (15 schemes)

## Next Actions from Visuals

1. **Quick Wins** (Quadrant 1): Deploy landing_generator + cpa_bot_generator for schemes #1, #2, #4
2. **Major Projects** (Quadrant 2): Build video pipeline for schemes #5, #6
3. **Fill-ins** (Quadrant 3): Pinterest, Craigslist, OLX, Gumtree, Locanto landings
4. **Avoid** (Quadrant 4): Avito, Reddit, Kijiji — require manual accounts + ad budget

## Embedding in Other Docs

Copy any diagram block (```mermaid ... ```) into any GitHub `.md` file — renders natively.