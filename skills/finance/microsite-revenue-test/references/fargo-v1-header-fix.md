# Fargo v1 Header Fix (2026-07-14)

## Problem
On `/fargo/` (v1 light/terracotta theme):
- Hero has dark background (linear-gradient #1a1814 → #3d322c)
- Nav links used `color: var(--slate-light)` (#6b6560) — dark gray, invisible on dark hero
- Header CTA button was `.btn-primary` (terracotta bg), but hero has two buttons: `.btn-primary` + `.btn-outline` (transparent white border)
- User wanted header CTA to match hero's secondary button style

## Solution Applied

### CSS Changes in `docs/fargo/index.html`

```css
/* Nav links: white on dark hero, slate on scrolled */
.header-nav a { 
  color: var(--white); 
}
.header.scrolled .header-nav a { 
  color: var(--slate-light); 
}
.header-nav a:hover { 
  color: var(--terracotta); 
}

/* Header CTA: btn-outline on dark, btn-outline-dark on scrolled */
.header .btn-outline { 
  color: var(--white); 
  border-color: rgba(255,255,255,0.4); 
}
.header.scrolled .btn-outline { 
  color: var(--terracotta); 
  border-color: var(--terracotta); 
}
.header .btn-outline:hover { 
  background: rgba(255,255,255,0.08); 
  border-color: var(--white); 
  color: var(--white); 
}
.header.scrolled .btn-outline:hover { 
  background: var(--terracotta); 
  border-color: var(--terracotta); 
  color: var(--white); 
}
```

### HTML Change
```html
<a href="#booking" class="btn btn-primary">Записатись</a>

<a href="#booking" class="btn btn-outline">Записатись</a>
```

## Result
- Nav links: visible on dark hero, switch to slate when header becomes light
- Header CTA: matches hero's "Переглянути ціни" button (outline style) on dark; matches terracotta outline on light
- Consistent visual language across hero and header

## Files
- `docs/fargo/index.html` — main file with fix
- `docs/fargo-v2/index.html` — v2 dark luxury (separate deploy)