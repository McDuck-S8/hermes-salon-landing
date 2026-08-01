---
name: data-toolkit
description: "Unified data science toolkit for Hermes: data-analyst + jupyter-live-kernel + ripple-engine. One skill to load, 3 engines at hand."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [data, analysis, jupyter, ripple, visualization, reporting]
    related_skills: [data-analyst, jupyter-live-kernel, ripple-engine, web-analytics, stocks, excel-author]
  skill_updated: "2026-07-24"
  created_by: "auto_patch_g007"
  component_skills:
    - data-analyst
    - jupyter-live-kernel
    - ripple-engine
---

# Data Toolkit — Unified Interface

**One skill to load. 3 data engines. Zero context switching.**

This meta-skill wraps all core data science skills into a single loadable unit.

## Quick Start

```python
# Load once, get all 3 tools
from hermes_tools import skill_view
skill_view("data-science/data-toolkit")

# Now you have:
# - data-analyst (end-to-end analysis with viz + reporting)
# - jupyter-live-kernel (iterative Python via live Jupyter kernel)
# - ripple-engine (structured analytical methodology for Knowledge Cube)
```

## Component Skills Map

| Skill | Purpose | Best For |
|-------|---------|----------|
| **data-analyst** | End-to-end analysis: load → explore → viz → report | CSV/Excel/DB → charts → HTML report |
| **jupyter-live-kernel** | Iterative Python via live Jupyter kernel (hamelnb) | Exploration, prototyping, stepwise analysis |
| **ripple-engine** | Structured analytical methodology for Knowledge Cube | Deep research, synthesis, pattern extraction |

## Unified Data Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. INGEST (data-analyst)                                        │
│    • Load: CSV, Excel, JSON, SQL, Parquet                       │
│    • Schema detection, missing value profiling                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. EXPLORE (jupyter-live-kernel)                                │
│    • Live kernel: hamelnb                                        │
│    • Stepwise: load → clean → feature engineering → model       │
│    • State persists across cells                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. ANALYZE (ripple-engine)                                      │
│    • Structured methodology: Observe → Orient → Decide → Act    │
│    • Knowledge Cube integration: extract patterns → KC entries  │
│    • Synthesis: cross-source correlation, hypothesis testing    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. REPORT (data-analyst)                                        │
│    • Visualizations: matplotlib, seaborn, plotly                │
│    • HTML report: self-contained, interactive                   │
│    • Export: JSON/CSV for downstream                            │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Commands Reference

### Data Analyst (data-analyst)
```python
# Full pipeline
from skills.data_science.data_analyst import DataAnalyst

analyst = DataAnalyst()
analyst.load("data.csv")
analyst.explore()           # profile, missing, correlations
analyst.visualize()         # auto-charts
analyst.report("report.html")  # self-contained HTML
```

### Jupyter Live Kernel (jupyter-live-kernel)
```bash
# Start kernel
jupyter console --kernel=python3

# Or via hamelnb (iterative)
python -m hamelnb kernel --port 8888

# Notebook operations
jupyter nbconvert --to html notebook.ipynb
jupyter nbconvert --execute notebook.ipynb
```

### Ripple Engine (ripple-engine)
```python
# Structured analysis for Knowledge Cube
from skills.data_science.ripple_engine import RippleEngine

engine = RippleEngine()
engine.observe(query="CPA offer performance by geo")
engine.orient(sources=["kc", "web", "logs"])
engine.decide(hypothesis="Geo X has 3x CR of Geo Y")
engine.act()  # writes to KC with tags
```

## Integration with Knowledge Cube

```python
from scripts.event_evolution import on_task_complete

on_task_complete(
    content="Data analysis complete: loaded 50k rows, found 3 key segments, exported report.html + KC entries",
    tags=["data", "analysis", "cpa", "segments", "success"],
    source="agent"
)
```

## Anti-Patterns (from 96 data entries, 21 failures = 22% failure rate)

| Anti-Pattern | Guard |
|--------------|-------|
| Analysis without persistence | **data-analyst**: mandatory report.html export |
| Kernel state lost | **jupyter-live-kernel**: hamelnb state persistence |
| Insights not in KC | **ripple-engine**: structured KC entry per finding |
| Manual chart creation | **data-analyst**: auto-viz from profile |
| One-off notebooks | **jupyter-live-kernel**: save as .ipynb, version |

## Verification Checklist

After using this toolkit:
- [ ] Data loaded and profiled (data-analyst)
- [ ] Exploration done in live kernel (jupyter-live-kernel)
- [ ] Patterns synthesized via structured methodology (ripple-engine)
- [ ] Report generated (HTML/JSON/CSV)
- [ ] KC entries created for each finding
- [ ] All tags applied

---

**Origin:** g-007 Unlock: data (96 entries, 21 failures, 3 successes)
**Created:** 2026-07-24 via auto_patch_g007
**Source:** Knowledge Cube domain `data` + all 3 component skills