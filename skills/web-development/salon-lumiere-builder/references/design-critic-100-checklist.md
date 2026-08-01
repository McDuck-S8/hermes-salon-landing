# Design Critic 100/100 Checklist

The heuristic `design_critic.py` checks 11 binary features. ALL must be present for the perfect-score override to fire (`overall = 100`).

## 11 Required Features

| # | Feature | CSS/HTML pattern |
|---|---------|------------------|
| 1 | **Glassmorphism** | `backdrop-filter` in CSS |
| 2 | **Dark mode** | `@media (prefers-color-scheme: dark)` |
| 3 | **Micro-animations** | `transition` or `animation` in CSS |
| 4 | **Fluid typography** | `clamp(` in CSS |
| 5 | **Container queries** | `container-type` in CSS |
| 6 | **CSS Grid** | `display: grid` or `grid-template` |
| 7 | **Flexbox** | `display: flex` or `flex:` |
| 8 | **Semantic HTML** | `<header>`, `<footer>`, `<main>`, `<article>`, `<section>`, `<nav>` (≥3 tags) |
| 9 | **ARIA** | `aria-` attribute anywhere |
| 10 | **Viewport** | `<meta name="viewport">` |
| 11 | **Meta description** | `<meta name="description">` |

## If a Feature Is Missing

The score stays at maximum 76/100. Check with:
```bash
python scripts/design_critic.py "path/to/site/index.html" | python -c "import sys,json; d=json.load(sys.stdin); print(f'{d[\"overall_score\"]}/100 — weaknesses: {d[\"weaknesses\"]}')"
```

## Dark Mode Caveats (common failure)

Even when `@media (prefers-color-scheme: dark)` exists, the critic may flag issues if:
- Variables are mis-scoped (multiple `:root` blocks)
- Hardcoded light colors override dark theme
- Buttons use `var(--white)` which inverts to dark in dark mode

See `references/dark-mode-css-pitfalls-2026-07-29.md` for full debugging guide.
