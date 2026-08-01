# CSS Theme Safety — Dark Mode Pitfalls

## Root Cause Pattern

CSS custom properties in `:root` cascade by specificity, not by block position. A `@media (prefers-color-scheme: dark)` block is NOT a separate scope — it overrides `:root` variables only when the media condition matches.

## Common Breakage: the Two-`:root` Trap

```css
/* ❌ BROKEN — dark mode tokens outside media query */
:root { --dark: #1a1a1a; }
:root { --dark: #f7fafc; }           /* OVERRIDES the first unconditionally */
@media (prefers-color-scheme: dark) {
  :root { --dark: #f7fafc; }         /* too late, already overridden */
}
```

```css
/* ✅ CORRECT — one :root, one @media */
:root { --dark: #1a1a1a; }
@media (prefers-color-scheme: dark) {
  :root { --dark: #f7fafc; }
}
```

## Exposed by Design Critics

Heuristic design critics (like `design_critic.py`) check for *presence* of CSS patterns (`backdrop-filter`, `@media (prefers-color-scheme: dark)`, `clamp()`) — NOT for correctness. A page scoring 76/100 can be visually broken.

**Always verify visually after CSS theme changes, not just with automated tools.**

## Hardcoded Colors Need Explicit Dark Overrides

When a CSS property uses a hardcoded color (not a variable), it won't change in dark mode:

```css
/* ❌ Stays light in dark mode */
.hero { background: linear-gradient(135deg, #f0f5f3 0%, #f0f0ec 100%); }

/* ✅ Add dark mode override */
@media (prefers-color-scheme: dark) {
  .hero { background: linear-gradient(135deg, #1a2a2a 0%, #121212 100%); }
}
```

## Never Use Themed Variables for Fixed-Style Elements

Variables that swap meaning between themes (`--dark` → light in dark mode, `--white` → dark in dark mode) should NOT be used for elements that must keep a consistent appearance.

```css
/* ❌ Footer becomes light in dark mode when --dark = #f7fafc */
.footer { background: var(--dark); color: rgba(255,255,255,.5); }

/* ✅ Hardcode footer background */
.footer { background: #1a1a1a; color: rgba(255,255,255,.6); }
@media (prefers-color-scheme: dark) { .footer { background: #0d0d0d; } }
```

## Safe Variable Swap Pattern

When variables swap meaning (`--white`/`--dark`), verify every usage:

| Component | Light mode | Dark mode | Risk |
|-----------|-----------|-----------|------|
| Button bg `var(--teal)` | `#2d6a6a` OK | `#4fd1c5` OK | Low |
| Button text `var(--white)` | `#ffffff` OK | `#1e1e1e` bad | **High** — dark text on colored bg |
| Paragraph `var(--text-muted)` | `#6b6b6b` OK | `#71717a` OK | Medium — check background contrast |

## Verification Checklist

- [ ] Header background visible in both themes
- [ ] Hero/text visible in both themes
- [ ] Buttons visible in both themes (text color ≠ background color)
- [ ] Footer readable in both themes
- [ ] Cards/surfaces distinct from background in both themes
- [ ] No hardcoded light colors left invisible in dark mode
