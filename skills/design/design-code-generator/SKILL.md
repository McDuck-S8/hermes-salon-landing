---
name: design-code-generator
description: "Generates production-ready HTML/CSS/JS from design patterns and adapted components. Uses templates from design-research and design-adaptation."
version: "1.0.0"
author: "Hermes Agent"
tags:
  - design
  - code-generation
  - html
  - css
  - javascript
  - tailwind
  - components
category: design
triggers:
  - generate html
  - generate css
  - generate component
  - create landing page
  - build design system
related_skills:
  - design-research
  - design-adaptation
  - design-quality-check
  - skill-composer
---

# design-code-generator

Generates production-ready HTML/CSS/JS from design patterns and adapted components. Uses templates from design-research and design-adaptation.

## Pipeline

1. **Template Selection** — Chooses appropriate templates based on task
2. **Pattern Injection** — Injects adapted patterns (colors, typography, spacing)
4. **Code Assembly** — Assembles HTML/CSS/JS with proper structure
4. **Optimization** — Minifies, adds critical CSS, defers JS

## Usage

```python
from scripts.design_analyzer import DesignAnalyzer

analyzer = DesignAnalyzer()

# Generate a landing page
code = analyzer.generate_landing_page(
    brand_colors={"primary": "#2563eb", "secondary": "#0ea5e9"},
    typography={"heading": "Inter", "body": "Inter"},
    components=["hero", "features", "testimonials", "cta", "footer"]
)

# Generate a component
button_code = analyzer.generate_component("button", {
    "variants": ["primary", "secondary", "outline", "ghost"],
    "sizes": ["sm", "md", "lg"],
    "states": ["default", "hover", "focus", "disabled", "loading"]
})
```

## Output Formats

- **HTML** — Semantic, accessible, SEO-ready
- **CSS** — Custom properties, modern layout (Grid/Flex), container queries
- **Tailwind** — Utility classes, custom config, dark mode
- **JS** — Vanilla ES modules, progressive enhancement, no framework lock-in

## Templates Directory

Each generated skill includes a `templates/` directory:
```
templates/
├── landing_page.html
├── landing_page.css
├── landing_page.tailwind.js
├── components/
│   ├── button.html
│   ├── button.css
│   ├── card.html
│   ├── card.css
│   └── ...
└── design_tokens.json
```

## Quality Standards

- Semantic HTML5
- WCAG 2.1 AA compliant
- Mobile-first responsive
- Container queries where applicable
- Critical CSS inlined
- JS deferred/async

---

## DOX Compliance

This skill follows the DOX framework. See AGENTS.md for contracts.