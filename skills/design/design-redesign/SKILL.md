---
name: design-redesign
description: "Complete website redesign pipeline — analysis, research, adaptation, generation, quality check, handoff."
version: "1.0.0"
author: "Hermes Agent"
tags:
  - design
  - redesign
  - pipeline
  - full-cycle
category: design
triggers:
  - redesign website
  - update design
  - modernize site
  - improve design
related_skills:
  - design-research
  - design-adaptation
  - design-code-generator
  - design-quality-check
  - design-critic
  - handoff-manager
  - cli-orchestrator
---

# design-redesign

Complete website redesign pipeline — analysis, research, adaptation, generation, quality check, handoff.

## Pipeline Stages

```
1. ANALYSIS
   Input: URL or HTML of existing site
   Output: Site structure, content inventory, current design tokens
   
2. RESEARCH
   Input: Business context, target audience, brand guidelines
   Output: Relevant design references, trend analysis, competitor analysis
   
3. ADAPTATION
   Input: Selected references + brand guidelines
   Output: Adapted design tokens (colors, typography, spacing, components)
   
4. GENERATION
   Input: Adapted tokens + site structure
   Output: New HTML/CSS/JS code with templates
   
5. QUALITY CHECK
   Input: Generated code
   Output: Lighthouse, axe, ESLint, W3C scores + recommendations
   
6. HANDOFF
   Input: Quality-approved code
   Output: Deployed site or handoff package with docs
```

## Usage

```python
# Full redesign pipeline
from scripts.cli_orchestrator import CLIOrchestrator

orchestrator = CLIOrchestrator()
orchestrator.add_task("analyze", "design_researcher", "Analyze current site structure and content")
orchestrator.add_task("research", "design_researcher", "Find modern B2B design references with blue brand", dependencies=["analyze"])
orchestrator.add_task("adapt", "design_adaptation", "Adapt patterns to blue brand guidelines", dependencies=["research"])
orchestrator.add_task("generate", "design_code_generator", "Generate new site code from adapted patterns", dependencies=["adapt"])
orchestrator.add_task("evaluate", "design_quality_check", "Run Lighthouse, axe, ESLint on generated code", dependencies=["generate"])
orchestrator.add_task("critique", "design_critic", "LLM-based design review of generated site", dependencies=["evaluate"])
orchestrator.add_task("handoff", "design_handoff", "Package final code with documentation", dependencies=["critique"])

results = orchestrator.execute()
```

## Configuration

```yaml
redesign:
  brand_colors:
    primary: "#2563eb"
    secondary: "#0ea5e9"
  brand_typography:
    heading: "Inter"
    body: "Inter"
  target_audience: "B2B decision makers"
  industry: "SaaS"
  competitors: ["competitor1.com", "competitor2.com"]
  preserve_content: true
  preserve_structure: false
```

## Outputs

| Stage | Output |
|-------|--------|
| Analysis | `analysis/site_structure.json`, `analysis/content_inventory.json` |
| Research | `research/references.json`, `research/trends.json`, `competitors/analysis.md` |
| Adaptation | `adaptation/design_tokens.json`, `adaptation/component_map.yaml` |
| Generation | `output/index.html`, `output/styles.css`, `output/app.js`, `output/templates/` |
| Quality Check | `quality/report.md`, `quality/scores.json`, `quality/recommendations.json` |
| Critique | `critique/design_review.md`, `critique/score.json` |
| Handoff | `handoff/final_code/`, `handoff/documentation.md`, `handoff/deployment_guide.md` |

---

## DOX Compliance

This skill follows the DOX framework. See AGENTS.md for contracts.