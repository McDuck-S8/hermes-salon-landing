---
name: modern-css
description: "Modern CSS 2026 — container queries, View Transitions API, :has(), @scope, CSS nesting, subgrid, light-dark(), start-style, CSS layers. Load BEFORE any page build to use platform features instead of JS workarounds."
version: 1.0.0
tags: [css, modern-css, container-queries, view-transitions, frontend, web-development]
---

# Modern CSS 2026

> Every new page should use these platform features. They eliminate JS boilerplate and ship faster.

## Container Queries

Key tool for responsive components. Queries PARENT size, not viewport.

```css
/* 1. Define container */
.card-grid {
  container-type: inline-size;
  container-name: card;
}

/* Shorthand */
.card-grid {
  container: card / inline-size;
}

/* 2. Query it */
@container card (min-width: 400px) {
  .card { display: grid; grid-template-columns: 1fr auto; }
}

@container card (max-width: 299px) {
  .card { flex-direction: column; }
}
```

### Common patterns

```css
/* Component adapts to its slot */
.widget {
  container-type: inline-size;
}
@container (min-width: 350px) {
  .widget-header { flex-direction: row; }
}
@container (max-width: 349px) {
  .widget-header { flex-direction: column; }
}

/* Card grid that works in sidebar and main */
.card-container { container: card / inline-size; }
@container card (min-width: 500px) {
  .card { display: flex; gap: var(--space-md); }
}
@container card (min-width: 700px) {
  .card { grid-template-columns: 2fr 1fr; }
}
```

### Pitfalls
- `container-type: inline-size` affects layout — parent needs `overflow: clip` or `overflow: hidden` (no scrollbars)
- Can't animate `display` changes across breakpoints (yet)
- Browser support: Baseline 2023 (>= Chrome 105, Safari 16, FF 110)

---

## :has() — The Parent Selector

Replaces JS for state-dependent styling.

```css
/* Form group error — no JS needed */
.form-group:has(input:invalid) .error-msg { display: block; }
.form-group:has(input:invalid) input { border-color: var(--color-error); }

/* Flyout open state */
nav:has(.flyout:hover) .trigger { color: var(--color-accent); }

/* Count children */
.card-grid:has(> :last-child:nth-child(3)) { grid-template-columns: repeat(3, 1fr); }
.card-grid:has(> :last-child:nth-child(2)) { grid-template-columns: repeat(2, 1fr); }

/* Dark mode aware — image filters */
figure:has(img) { background: transparent; }

/* Empty state */
.list:has(> :only-child:empty)::after { content: "No items"; }
```

### Performance note
`:has()` is relatively slow — don't use on 1000+ elements or inside `*` selectors. OK for forms, menus, cards (< 200 elements).

---

## View Transitions API

SPA-like page transitions with zero JS (cross-document) or minimal JS (same-document).

### Cross-document (MPA — Multi-Page App)
Drop in `<head>` — works between navigations on same origin:

```html
<meta name="view-transition" content="same-origin" />
```

```css
/* Default crossfade — customize with pseudo-elements */
::view-transition-old(root) { animation: fade-out 0.3s ease-out; }
::view-transition-new(root) { animation: fade-in 0.3s ease-out; }

@keyframes fade-out { to { opacity: 0; } }
@keyframes fade-in { from { opacity: 0; } }
```

### Same-document (SPA — needs JS)
```javascript
document.startViewTransition(() => {
  // DOM change inside callback
  document.querySelector('#content').innerHTML = newContent;
});
```

### Shared elements (morph animation)
```css
/* Both old and new pages have class .card-image */
.card-image {
  view-transition-name: card-img;
}
/* Morphs between states automatically */
```

### Pitfalls
- Cross-document: Chrome 126+, Safari 18.2+ (Baseline 2025)
- Same-document: Chrome 111+, Safari 18+ (Baseline 2024)
- Don't animate everything — pick 2-3 key elements per page
- Disable if `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion) {
  ::view-transition-group(*),
  ::view-transition-old(*),
  ::view-transition-new(*) {
    animation: none !important;
  }
}
```

---

## CSS Nesting

Native nesting in all modern browsers.

```css
.card {
  background: var(--color-paper);
  
  /* Nest by & */
  & .title { font-weight: 700; }
  & .body { color: var(--color-text-secondary); }
  
  /* Pseudo-classes */
  &:hover { transform: translateY(-2px); }
  &:focus-within { outline: 2px solid var(--color-focus); }
  
  /* No & — implicit & (most browsers) */
  .meta { font-size: 0.875rem; }
  
  /* Media query nesting */
  @media (max-width: 768px) { flex-direction: column; }
}
```

### Pitfalls
- Always use `&` for concatenation: `&:hover` ✓, not ` :hover` (space matters)
- Deep nesting (> 3 levels) hurts specifity management — prefer flat

---

## @scope — Scoped Styles

Limit rules to a subtree without Shadow DOM.

```css
@scope (.card) {
  /* Only .card's descendants */
  p { margin-block: 0.5em; }
  img { border-radius: var(--radius); }
  
  /* Limit scope further */
  @scope (.card-header) {
    h2 { font-size: 1.25rem; }
  }
}
```

### Use cases
- Component isolation without Shadow DOM overhead
- Third-party widgets
- CMS-generated content within specific container

---

## Subgrid

Align children to parent grid tracks.

```css
.page-grid {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: var(--space-lg);
}

.content {
  display: grid;
  grid-template-columns: subgrid;   /* ← inherits parent columns */
  grid-column: 1;
}

.sidebar {
  display: grid;
  grid-template-columns: subgrid;
  grid-column: 2;
}
```

Useful for aligning cards, form fields, or section headers across columns.

---

## light-dark() — Built-in Theme Function

No JS theme toggle needed for basic dark mode (respects `prefers-color-scheme`).

```css
:root {
  color-scheme: light dark;
  --color-bg: light-dark(#fff, #1a1a2e);
  --color-text: light-dark(#1a1a2e, #e4e4e7);
  --color-accent: light-dark(#2563eb, #60a5fa);
}

body {
  background: var(--color-bg);
  color: var(--color-text);
}
```

### When to use
- Simple dark mode (no toggle, follow OS)
- Works in all modern browsers (Baseline 2024)
- For toggle + transition: use CSS custom properties + `class="dark"`

---

## start-style — Entry Animations

Animate elements on first render (no JS needed).

```css
@starting-style {
  .toast {
    opacity: 0;
    translate: 0 -10px;
  }
}

.toast {
  opacity: 1;
  translate: 0 0;
  transition: opacity 0.3s, translate 0.3s;
}
```

### Use cases
- Toast notifications appearing
- Menu opening from off-screen
- Dropdowns on first open
- List items appearing on page load

---

## CSS Layers (@layer)

Manage specifity by controlling cascade order.

```css
/* Declare layers (in order: lowest to highest priority) */
@layer reset, base, components, utilities;

/* Assign rules to layers */
@layer reset {
  *, *::before, *::after { box-sizing: border-box; margin: 0; }
}

@layer base {
  body { font-family: var(--font-body); line-height: 1.6; }
}

@layer components {
  .btn { /* component styles */ }
}

@layer utilities {
  .flex { display: flex; }
}

/* Layer with more specifity wins even with lower specificity selector */
@layer components {
  /* This beats identical specificity in base */
  .card { background: var(--color-paper); }
}
```

### Template for any project
```css
@layer reset, base, tokens, layout, components, utilities, overrides;
```

### Pitfalls
- Order of `@layer` statements matters — first declaration sets order
- Unlayered styles beat layered (they go to last implicit layer)
- `!important` in lower layer beats `!important` in higher — avoid

---

## Scroll-Driven Animations

Animate based on scroll position — no IntersectionObserver.

```css
.progress-bar {
  animation: scale-progress linear;
  animation-timeline: scroll();        /* default root scrollbar */
  animation-range: entry 0% exit 100%;
}

@keyframes scale-progress {
  from { scale: 0 1; }
  to   { scale: 1 1; }
}

/* View-based (element enters/exits viewport) */
.fade-in {
  animation: fade-in linear;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;
}
```

### Status
- Chrome 115+, Safari 18.2+ (not Firefox yet — Baseline 2025 partial)
- Use as progressive enhancement

---

## Quick reference

| Feature | Baseline | Replaces |
|---------|----------|----------|
| CSS Nesting | 2024 | SCSS/Less nesting |
| :has() | 2024 | JS classList logic |
| Container Queries | 2023 | Most media queries |
| Subgrid | 2023 | Nested grid hacks |
| @scope | 2025 | Shadow DOM for scoping |
| View Transitions (X-doc) | 2025 | Full-page JS routers |
| View Transitions (S-doc) | 2024 | SPA transition libs |
| light-dark() | 2024 | JS dark mode toggle |
| start-style | 2025 | JS entry animations |
| CSS Layers | 2023 | Import order hacks |
| scroll() / view() | 2025 (partial) | IntersectionObserver |
