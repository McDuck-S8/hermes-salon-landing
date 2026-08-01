---
name: omh-deep-research
description: |
  Multi-phase web research: decompose topic → parallel search → synthesize findings → verify citations.
  Outputs structured research report with sources. Part of OMH pipeline.
version: 1.0.0
category: autonomous-ai-agents
tags:
  - research
  - web-search
  - synthesis
  - citations
  - omh
---

# OMH Deep Research

## Purpose
Conducts thorough multi-phase research on any topic using Agent Reach web access capabilities.
Decomposes complex topics into searchable sub-questions, executes parallel searches, synthesizes findings,
and produces a verified research report with citations.

## Usage
```python
from scripts.crystal.omh_integration import OMHIntegration
omh = OMHIntegration()
result = omh.run_deep_research("topic to research", depth="normal")
```

## Phases
1. **Decompose** — Break topic into 5-10 searchable sub-questions
2. **Parallel Search** — Execute searches via Agent Reach (YouTube, Web, GitHub, RSS)
3. **Synthesize** — Combine findings, identify patterns, contradictions, gaps
4. **Verify Citations** — Cross-reference sources, flag unverified claims

## Outputs
- Structured research report (markdown)
- Source list with URLs and relevance scores
- Key findings summary
- Identified knowledge gaps

## Dependencies
- Agent Reach (web access layer)
- Crystal Knowledge Cube (for caching results)

## References
- `references/adr-template.md` — Architecture Decision Record template
- `references/state-schema.md` — Research state schema