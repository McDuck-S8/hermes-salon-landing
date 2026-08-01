---
name: design-adaptation
description: "Adapts external design patterns to local project context — colors, typography, spacing, brand guidelines. Uses PatternAdapter for semantic translation."
version: "1.0.0"
author: "Hermes Agent"
tags:
  - design
  - adaptation
  - pattern-adapter
  - branding
  - tailwind
  - css
category: design
triggers:
  - adapt design pattern
  - apply brand colors
  - customize design system
  - translate pattern to project
related_skills:
  - design-research
  - design-code-generator
  - pattern-adapter
  - external-import
---

# design-adaptation

Adapts external design patterns to local project context — brand colors, typography, spacing, component library.

## Pipeline

1. **Context Loading** — Reads brand guidelines, design tokens, existing components
2. **Pattern Matching** — Identifies adaptable elements in source pattern
3. **Semantic Translation** — Maps generic entities to local equivalents
4. **Code Generation** — Outputs adapted CSS/Tailwind/HTML

## Usage

```python
from scripts.design_analyzer import DesignAnalyzer
from scripts.design_reference_collector import DesignReferenceCollector

collector = DesignReferenceCollector()
analyzer = DesignAnalyzer()

# Collect references
collector.run_full_collection()

# Analyze patterns
for ref in collector.references.values():
    analyzer.analyze_reference(ref)

# Adapt patterns to project context
# The analyzer automatically maps tags to CSS/Tailwind
# and infers usage contexts
```

## Adaptation Rules

| External Entity | Local Mapping |
|----------------|---------------|
| `primary-color` | Project's primary brand color |
| `secondary-color` | Project's accent color |
| `font-heading` | Project's heading font |
| `font-body` | Project's body font |
| `spacing-unit` | Project's base spacing (e.g., 4px) |
| `border-radius` | Project's default radius |
| `shadow-level` | Project's shadow system |

## Output

- Adapted CSS custom properties
- Tailwind config extensions
- Component variants with brand colors
- Design token JSON

---

## DOX Compliance

This skill follows the DOX framework. See AGENTS.md for contracts.