# Fargo v1 → v2 Header CTA Adaptation Case Study

## Problem
Landing page with:
- **Dark hero** (`#1a1814` gradient) with white nav links + terracotta CTA button
- **Light scrolled header** (`rgba(247,244,240,0.92)`) — nav links adapt to dark (`var(--slate-light)`), but CTA button stayed terracotta → **blended into background**

## Root Cause
CSS only handled nav link color change on scroll:
```css
.header-nav a{color:var(--white)}          /* dark hero */
.header.scrolled .header-nav a{color:var(--slate-light)}  /* light header */
```
But the CTA button (`.btn-primary` in header) had no `.header.scrolled` override.

## Fix Applied
```css
.header .btn-primary{background:var(--terracotta);color:var(--white)}
.header.scrolled .btn-primary{background:var(--dark);color:var(--white)}
.header .btn-primary:hover{background:var(--terracotta-dark)...}
.header.scrolled .btn-primary:hover{background:var(--terracotta)...}
```

## Result
| State | Button | Readability |
|-------|--------|-------------|
| Dark hero | Terracotta bg, white text | ✅ High contrast |
| Light scrolled header | Dark bg (`var(--dark)`), white text | ✅ High contrast |
| Hover dark | Terracotta-dark | ✅ |
| Hover light | Terracotta | ✅ |

## Anti-Slop-Design Pre-Flight Items Caught
- ✅ **Button Contrast Check**: all CTAs readable (no white-on-white)
- ✅ **CTA Button Wrap**: no wrapped labels at desktop
- ✅ **Page Theme Lock**: one theme per state, no accidental mixing

## Pattern for Future Landing Pages
When designing a landing with:
1. Dark hero + CTA button
2. Light scrolled header containing same CTA

**Always add** `.header.scrolled .btn-primary` override with inverted colors. Never assume one button style works on both backgrounds.