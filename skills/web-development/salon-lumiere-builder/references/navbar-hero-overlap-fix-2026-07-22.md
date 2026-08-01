# Navbar-Photo Overlap Fix — Fargo trend (2026-07-22)

## Problem

Fixed nav with `mix-blend-mode:difference` and `padding:20px 0` at page top:
- CTA button in the nav visibly "floats" on the hero background photo
- Nav appears too short because the padding area is invisible
- When scrolled (background appears with `.scrolled` class), nav looks fine

## Root Cause

`mix-blend-mode:difference` makes the entire nav background transparent. Only the text content has visual presence. The 20px top/bottom padding is invisible, so the button appears to sit directly on the hero photo with no bar to contain it.

## Fix

### 1. Remove mix-blend-mode, add visible background

```css
/* BEFORE */
.header{position:fixed;top:0;padding:20px 0;mix-blend-mode:difference}
.header.scrolled{background:rgba(14,14,14,0.88);backdrop-filter:blur(20px);padding:12px 0;mix-blend-mode:normal}

/* AFTER */
.header{position:fixed;top:0;padding:16px 0;background:rgba(14,14,14,0.75);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}
.header.scrolled{background:rgba(14,14,14,0.92);backdrop-filter:blur(20px);padding:12px 0}
```

### 2. Give hero padding-top to clear nav

```css
.hero { min-height:100dvh; padding-top: 80px; }
```

## CSS Pattern: Dark Glass Nav

Safe alternative to mix-blend-mode that works on hero photos:

```css
.header {
  position: fixed;
  top: 0;
  z-index: 100;
  padding: 16px 0;
  background: rgba(14,14,14,0.75);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
.header.scrolled {
  background: rgba(14,14,14,0.92);
  backdrop-filter: blur(20px);
  padding: 12px 0;
}
```

Nav text colors should be light (white/cream) to contrast with the dark glass.

## Workflow Lesson

When user reports a bug on a local page, multiple variants may exist in the same directory (index.html, index.trend.html, index-v2.html). **Ask which file they're viewing before editing.** Fixing the wrong variant wastes time.

## Related

- Salons with hero photos + fixed nav
- Any landing page with transparent/glass nav over imagery
