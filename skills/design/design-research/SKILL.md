---
name: design-research
description: "Searches and extracts design trends, patterns, and references from external sources (Awwwards, Behance, Dribbble, YouTube, blogs, GitHub). Uses external_import for semantic search and pattern extraction."
version: "1.0.0"
author: "Hermes Agent"
tags:
  - design
  - research
  - trends
  - patterns
  - awwwards
  - behance
  - youtube
  - github
category: design
triggers:
  - design trends
  - find design references
  - search design patterns
  - analyze competitor designs
related_skills:
  - design-adaptation
  - design-code-generator
  - external-import
  - video-learner
---

# design-research

Searches and extracts design trends, patterns, and references from external sources for continuous learning.

## Pipeline

1. **Source Scanning** — Awwwards, SiteInspire, Behance, Dribbble, YouTube, Blogs, GitHub
2. **Pattern Extraction** — Semantic search via external_import, tag extraction
3. **Trend Analysis** — Frequency analysis, confidence scoring
3. **Storage** — Tactical Buffer (TTL 14 days, confidence 0.4-0.6)

## Usage

```python
from scripts.design_reference_collector import DesignReferenceCollector

collector = DesignReferenceCollector()
results = collector.run_full_collection(max_per_source=10)
# Returns: {"awwwards": [...], "youtube": [...], "github": [...], "blogs": [...]}

# Access trends
for trend in collector.trends.values():
    print(f"{trend.name}: freq={trend.frequency}, conf={trend.confidence:.2f}")
```

## Commands

```bash
python scripts/design_reference_collector.py collect  # Full collection
python scripts/design_reference_collector.py trends   # List trends
python scripts/design_reference_collector.py stats    # Statistics
```

## Integration

- Feeds: `design-adaptation` for pattern adaptation
- Feeds: `design-code-generator` for code templates
- Feeds: `design-critic` for trend comparison
- Stores in: Tactical Buffer → Strategic DB (promotion after 3+ uses, 80% success)

---

## DOX Compliance

This skill follows the DOX framework. See AGENTS.md for contracts.