---
name: design-quality-check
description: "Automated quality checking for design projects — Lighthouse, axe-core, ESLint, W3C Validator, custom design checks. Integrates with feedback_store for learning."
version: "1.0.0"
author: "Hermes Agent"
tags:
  - design
  - quality
  - lighthouse
  - axe-core
  - eslint
  - w3c
  - accessibility
  - seo
  - performance
category: design
triggers:
  - check design quality
  - run lighthouse
  - check accessibility
  - validate html
  - audit design
related_skills:
  - design-evaluator
  - design-critic
  - design-feedback
  - feedback-store
---

# design-quality-check

Automated quality checking for design projects — Lighthouse, axe-core, ESLint, W3C Validator, custom design checks.

## Pipeline

1. **Project Setup** — Locates HTML/CSS/JS files
2. **Lighthouse** — Performance, Accessibility, Best Practices, SEO, PWA
3. **axe-core** — Accessibility violations, passes, incomplete
3. **ESLint** — JavaScript/TypeScript errors and warnings
4. **W3C Validator** — HTML validation errors/warnings
5. **Custom Checks** — Viewport, charset, semantic HTML, ARIA, responsive images
6. **Scoring** — Weighted overall score with thresholds
6. **Report** — Detailed report with recommendations

## Quality Thresholds

| Metric | Threshold |
|--------|-----------|
| Lighthouse Performance | ≥ 80 |
| Lighthouse Accessibility | ≥ 90 |
| Lighthouse Best Practices | ≥ 85 |
| Lighthouse SEO | ≥ 80 |
| axe-core Score | ≥ 90 |
| W3C Errors | 0 |
| ESLint Errors | 0 |

## Usage

```bash
python scripts/design_evaluator.py <project_path> [project_name]
```

```python
from scripts.design_evaluator import DesignEvaluator

evaluator = DesignEvaluator()
result = evaluator.evaluate_project(Path("my-project"), "my-project")

print(f"Score: {result.overall_score}/100")
print(f"Passed: {result.passed}")

# Detailed report
report = evaluator.generate_report(result)
print(report)

# Access detailed results
print(f"Lighthouse: Perf={result.lighthouse_performance}, A11y={result.lighthouse_accessibility}")
print(f"Axe: score={result.axe_score}, violations={result.axe_violations}")
print(f"Custom checks: {result.custom_checks.get('_score', 0)}/100")
```

### Known Issues & Fixes

| Issue | Fix Applied |
|-------|-------------|
| Lighthouse server working directory | Fixed: Uses `project_path.resolve()` and custom HTTP handler with `directory=` parameter instead of `os.chdir` |
| Inline CSS detection | Fixed: Extracts `<style>` tags from HTML before concatenating with external CSS |
| Output file path resolution | Fixed: Uses `project_path.parent.resolve() / "evaluation_report.json"` for file-based projects |
| HTML parser false negatives | Fixed: Case-insensitive matching, extracts inline `<style>` content |
| File vs directory path handling | Fixed: Checks `project_path.is_file()` vs `project_path.is_dir()` before rglob |
| Container queries detection | Fixed: Detects `container-type` and `@container` in combined HTML+CSS |

## Output

- **Overall Score** (0-100)
- **Pass/Fail** status
- **Detailed breakdown** per tool
- **Recommendations** with code examples
- **JSON report** for programmatic use

## Integration

- Feeds: `design-feedback` for learning signals
- Feeds: `design-critic` for trend comparison
- Uses: `feedback-store` for pattern learning
- Triggers: `design-redesign` if quality < threshold

---

## DOX Compliance

This skill follows the DOX framework. See AGENTS.md for contracts.