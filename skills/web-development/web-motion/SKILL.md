---
name: web-motion
description: "Web animations and motion design — GSAP + ScrollTrigger + Lenis smooth scroll, CSS view transitions, Framer Motion (React), micro-interactions, parallax, stagger reveals. Load when ANY animation or motion is needed."
version: 1.0.0
tags: [gsap, scrolltrigger, lenis, motion, animation, framer-motion, parallax]
---

# Web Motion & Animation

## Core Stack: Lenis + GSAP + ScrollTrigger

Lenis (3kB) handles smooth scroll. GSAP handles everything else. ScrollTrigger links animations to scroll position.

### Install

```html
<!-- CDN -->
<script src="https://cdn.jsdelivr.net/npm/@studio-freight/lenis@1.1.18/dist/lenis.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.7/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.7/dist/ScrollTrigger.min.js"></script>
```

```bash
# npm
npm install @studio-freight/lenis gsap
```

---

## Lenis — Smooth Scroll

```javascript
const lenis = new Lenis({
  duration: 1.2,         // scroll duration (lower = snappier)
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), // easeOutExpo
  orientation: 'vertical',
  smoothWheel: true,
});

// GSAP integration — MUST have
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add((time) => lenis.raf(time * 1000));
gsap.ticker.lagSmoothing(0);

// Anchor links (smooth scroll to section)
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', (e) => {
    e.preventDefault();
    const target = document.querySelector(anchor.getAttribute('href'));
    if (target) lenis.scrollTo(target, { offset: -80 });
  });
});
```

### Pitfalls
- `gsap.ticker.add()` is REQUIRED for ScrollTrigger sync — without it, ScrollTrigger lags behind Lenis
- `lagSmoothing(0)` prevents jitter on scroll
- Never use native `scroll-behavior: smooth` with Lenis — they conflict
- Test with `prefers-reduced-motion` — disable Lenis if active

---

## GSAP ScrollTrigger — Scroll-Linked Animations

```javascript
gsap.registerPlugin(ScrollTrigger);

// === Basic reveal (fade up) ===
gsap.from('.card', {
  opacity: 0,
  y: 60,
  duration: 0.8,
  stagger: 0.15,         // delay between cards
  ease: 'power2.out',
  scrollTrigger: {
    trigger: '.card-grid',
    start: 'top 80%',     // when grid enters viewport
    end: 'top 30%',
  }
});

// === Pin section ===
gsap.to('.parallax-section', {
  scrollTrigger: {
    trigger: '.parallax-section',
    start: 'top top',
    end: 'bottom top',
    pin: true,
    scrub: true,          // links to scroll (0 = start, 1 = end)
  }
});

// === Horizontal scroll ===
gsap.to('.horizontal-container', {
  x: () => -(document.body.scrollWidth - innerWidth),
  ease: 'none',
  scrollTrigger: {
    trigger: '.horizontal-wrapper',
    pin: true,
    scrub: 1,
    end: () => '+=' + document.body.scrollWidth,
  }
});

// === Text reveal (word by word) ===
const words = document.querySelector('.hero-title').textContent.split(' ');
document.querySelector('.hero-title').innerHTML =
  words.map(w => `<span class="word">${w}</span>`).join(' ');

gsap.from('.word', {
  opacity: 0,
  y: 20,
  stagger: 0.1,
  duration: 0.6,
  ease: 'power2.out',
  scrollTrigger: {
    trigger: '.hero-title',
    start: 'top 80%',
  }
});
```

### ScrollTrigger options

| Option | Effect |
|--------|--------|
| `start: 'top center'` | Animation starts when element top hits center |
| `end: 'bottom top'` | Animation ends when element bottom exits top |
| `scrub: true` | Linked to scroll position |
| `scrub: 1` | Smooth 1s delay (less jerky) |
| `pin: true` | Pin element in viewport while scrolling |
| `pinSpacing: false` | Don't add space for pinned element |
| `toggleActions: 'play none none reverse'` | Play on enter, reverse on leave |
| `markers: true` | Debug only — show trigger points |

---

## Framer Motion (React)

```bash
npm install framer-motion
```

```jsx
import { motion, AnimatePresence } from 'framer-motion';

// Fade in on mount
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5, ease: 'easeOut' }}
>
  Content
</motion.div>

// Stagger children
<motion.ul
  variants={{
    show: { transition: { staggerChildren: 0.1 } },
  }}
  initial="hide"
  whileInView="show"
>
  {items.map(item => (
    <motion.li
      key={item.id}
      variants={{ hide: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }}
    >
      {item.name}
    </motion.li>
  ))}
</motion.ul>

// Page transitions (with AnimatePresence)
<AnimatePresence mode="wait">
  <motion.div
    key={page}
    initial={{ opacity: 0, x: 50 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: -50 }}
    transition={{ duration: 0.3 }}
  >
    {pageContent}
  </motion.div>
</AnimatePresence>

// Hover / tap micro-interactions
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  transition={{ type: 'spring', stiffness: 400, damping: 17 }}
>
  Click me
</motion.button>

// Viewport reveal (no GSAP needed)
<motion.div
  initial={{ opacity: 0, y: 50 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, margin: '-100px' }}
  transition={{ duration: 0.6 }}
>
  Reveals on scroll
</motion.div>
```

### Framer Motion vs GSAP
- **Framer Motion** — React-native, declarative, great for UI micro-interactions
- **GSAP + ScrollTrigger** — Complex timeline sequences, pin, horizontal scroll, large page animations
- **Combine both** — Framer Motion for component interactions, GSAP for page-level choreography

---

## CSS Animations (zero-JS)

```css
/* Keyframe definition */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Apply */
.animate-on-load {
  animation: fadeInUp 0.6s ease-out both;
}

/* Scroll-triggered with @starting-style (no JS) */
@starting-style {
  .reveal { opacity: 0; translate: 0 40px; }
}
.reveal {
  opacity: 1;
  translate: 0 0;
  transition: opacity 0.5s, translate 0.5s;
}
```

---

## Micro-Interactions

### Button hover states
```css
.btn {
  transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
}
.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.btn:active {
  transform: translateY(0);
  box-shadow: none;
}
```

### Focus ring (accessibility)
```css
:focus-visible {
  outline: 3px solid var(--color-focus);
  outline-offset: 2px;
}
```

### Reduced motion
```css
@media (prefers-reduced-motion) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

---

## Parallax

```javascript
// GSAP parallax
gsap.to('.bg-image', {
  yPercent: 30,           // moves background up/down
  ease: 'none',
  scrollTrigger: {
    trigger: '.parallax-section',
    start: 'top bottom',
    end: 'bottom top',
    scrub: true,
  }
});
```

### CSS-only parallax (simpler, but limited)
```css
.parallax {
  background-image: url('/bg.jpg');
  background-attachment: fixed;     /* ← the parallax */
  background-size: cover;
  background-position: center;
}
```

---

## Loading & Transition Patterns

### Page load animation
```javascript
// Hero text stagger on load
gsap.timeline()
  .from('.hero-title', { opacity: 0, y: 40, duration: 0.8, ease: 'power3.out' })
  .from('.hero-subtitle', { opacity: 0, y: 30, duration: 0.6 }, '-=0.4')
  .from('.hero-cta', { opacity: 0, y: 20, duration: 0.5 }, '-=0.3');
```

### Section reveal
```javascript
// Reveal on scroll (most common pattern)
document.querySelectorAll('.reveal').forEach(el => {
  gsap.from(el, {
    opacity: 0,
    y: 40,
    duration: 0.8,
    ease: 'power2.out',
    scrollTrigger: {
      trigger: el,
      start: 'top 85%',
      once: true,         // animate only once
    }
  });
});
```

---

## Pitfalls & Performance

- **Don't animate layout properties** (width, height, top, left) — use transform + opacity only
- **Use `will-change: transform`** sparingly on animated elements (triggers GPU layer)
- **`gsap.context()`** for cleanup — wrap animations in `let ctx = gsap.context(() => {...})` in React
- **Test with `prefers-reduced-motion: reduce`** — disable all motion or provide minimal alternative
- **Don't animate on load AND on scroll** — pick one to avoid double-trigger
- **Horizontal scroll + keyboard** — test arrow keys, Tab, Enter
- **Lenis + fixed elements** — ensure `position: fixed` doesn't break scroll
- **Mobile performance** — reduce `duration` and `stagger` on mobile (check `matchMedia`)
