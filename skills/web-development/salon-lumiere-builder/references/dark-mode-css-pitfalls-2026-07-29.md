# CSS Dark Mode Pitfalls — Salon Landing Fix

## Date: 2026-07-29
## Context: Cosmetologist site turned black-and-white, buttons invisible

## Symptom
- Site renders in black-and-white (forced dark mode)
- Buttons appear invisible (text same color as background)
- Hero heading "Ваша красота" barely visible

## Root Cause 1: Duplicate :root blocks

Multiple `:root {}` blocks at different specificity levels cause CSS custom property conflicts. The browser overrides variable values from the LAST matching block, not the one inside the expected `@media` query.

### ANTI-PATTERN (what broke the site):
```css
:root {
  --white: #ffffff;
  --dark: #1a1a1a;
  --teal: #2d6a6a;
}

/* ❌ BAD: dark mode tokens OUTSIDE @media — always override :root */
:root {
  --white: #1e1e1e;
  --dark: #f7fafc;
  --teal: #4fd1c5;
}

@media (prefers-color-scheme: dark) {
  :root {
    /* ❌ BAD: too late, already overridden by second :root above */
    --teal: #4fd1c5;
  }
}
```

### FIX — ONE :root + ONE @media:
```css
:root {
  /* Light mode defaults — everything here */
  --white: #ffffff;
  --dark: #1a1a1a;
  --teal: #2d6a6a;
  --glass-bg: rgba(255,255,255,0.15);
}

/* ONE dark mode override — nothing outside this */
@media (prefers-color-scheme: dark) {
  :root {
    --white: #1e1e1e;
    --dark: #f7fafc;
    --teal: #4fd1c5;
    --glass-bg: rgba(255,255,255,0.05);
  }
}
```

**Rule:** ONE `:root` block with light defaults, ONE `@media (prefers-color-scheme: dark)` block. Count them. If you have > 1 `:root`, you broke it.

## Root Cause 2: Hardcoded light colors need explicit dark overrides

CSS custom properties only affect elements that REFERENCE them via `var(--name)`. Elements with hardcoded color values (gradients, `background-color`, `border-color`) are unaffected by variable changes.

### Problematic pattern:
```css
.hero { background: linear-gradient(135deg, #f0f5f3 0%, #f8f7f4 100%); }
.header { background: rgba(248, 247, 244, 0.9); }
```
These stay LIGHT in dark mode while text becomes light → invisible.

### Fix — add @media overrides:
```css
@media (prefers-color-scheme: dark) {
  .hero { background: linear-gradient(135deg, #1a2a2a 0%, #121212 50%, #1a1a2e 100%); }
  .header { background: rgba(18, 18, 18, 0.85); backdrop-filter: blur(12px); }
  .hero p { color: #c0c0c0; } /* override var(--text-muted) for dark bg */
}
```

## Root Cause 3: Buttons use var(--white) for text, var(--white) becomes dark in dark mode

```css
.btn-primary { background: var(--teal); color: var(--white); }
```
In dark mode `--white = #1e1e1e` (dark gray), `--teal = #4fd1c5` (cyan) — text is dark gray on cyan, low contrast.

**Fix for header buttons** (always visible): hardcode `color: #fff` in the header-specific selector:
```css
.header .btn-primary { background: var(--teal); color: #fff; }
```

## Detective Work

When user says "site became black and white and buttons disappeared":

1. Count `:root` blocks in CSS — if > 1, that's the primary bug
2. Count `@media (prefers-color-scheme: dark)` blocks — should be exactly 1
3. Check if dark mode variables are referenced OUTSIDE any @media block (always-on override)
4. Check hardcoded colors (gradients, rgba literals) on `.hero`, `.header`, `.promo`, etc.

## Verification

After fixing:
1. Open in browser — toggle system dark/light mode
2. Check: hero h1 visible ✅, buttons visible ✅, cards visible ✅
3. Run design_critic to confirm no regression
