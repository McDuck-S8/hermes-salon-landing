# Kinetic Typography — Hero Text Animation

Splitting hero headings into individual character `<span>` elements with staggered CSS animations. Creates a dramatic entrance effect (2026 trend).

## HTML Structure

```html
<section class="hero">
  <div class="hero-content">
    <h1 class="hero-title" id="heroTitle">
      <!-- JS fills this with individual char spans -->
      Fargo
    </h1>
  </div>
</section>
```

## CSS

```css
@keyframes charReveal {
  0% { opacity: 0; transform: translateY(60px) rotateX(-40deg); }
  100% { opacity: 1; transform: translateY(0) rotateX(0); }
}

.hero-title .char {
  display: inline-block;
  opacity: 0;
  transform: translateY(60px) rotateX(-40deg);
}

.hero-title .char.revealed {
  animation: charReveal 0.6s ease forwards;
}
```

## JavaScript Implementation

```javascript
document.addEventListener('DOMContentLoaded', () => {
  const titleEl = document.getElementById('heroTitle');
  const titleText = titleEl.textContent;

  // Split into individual char spans
  const chars = titleText.split('').map((char, i) => {
    if (char === ' ') {
      // Spaces need explicit width in inline-block
      return `<span class="char" style="display:inline-block;width:0.3em">&nbsp;</span>`;
    }
    return `<span class="char" style="animation-delay:${0.8 + i * 0.05}s">${char}</span>`;
  }).join('');

  titleEl.innerHTML = chars;

  // Trigger reveal with stagger
  const charEls = titleEl.querySelectorAll('.char');
  charEls.forEach((el, i) => {
    setTimeout(() => {
      el.classList.add('revealed');
    }, 600 + i * 35); // 600ms delay for preloader, then 35ms stagger
  });
});
```

## Alternative: Pure CSS Stagger (no JS class toggle)

Set `animation-delay` directly on each span via inline style (as in the inline-style approach above with `style="animation-delay:0.8s"`), then use a single CSS rule:

```css
.hero-title .char {
  display: inline-block;
  animation: charReveal 0.6s ease forwards;
  /* delay is inline */
}
```

This skips the JS `setTimeout` loop entirely. Fewer lines, no jank from timer drift.

## Tuning Parameters

| Parameter | Typical Range | Effect |
|-----------|--------------|--------|
| Stagger interval | 30-50ms per char | Faster = subtle wave, slower = dramatic crawl |
| Start delay | 500-1000ms | Sync with preloader fade-out |
| `translateY` start | 40-80px | Larger = more dramatic pop |
| `rotateX` | -20deg to -50deg | More tilt = more 3D depth |
| Animation duration | 0.4-0.8s | Shorter = snappier, longer = smoother |
| Easing | `ease` or `cubic-bezier(0.2, 0.9, 0.3, 1.2)` | Custom = more polished |

## Companion Hero Elements

Pair kinetic typography with these elements for a complete 2026 hero:

```text
[pre-headline tag]   → 0.3s fade-up
[kinetic headline]   → 0.8s staggered char reveal
[subtitle paragraph] → 0.8s fade-up after headline
[CTA buttons]        → 0.8s fade-up after subtitle
[scroll indicator]   → 1.5s fade-up last
```

Sample timing:
```css
.hero-suptitle { animation: fadeUp 0.8s ease forwards 0.3s; }
.hero-title .char { /* delayed per char, starts at ~0.8s */ }
.hero-subtitle { animation: fadeUp 0.8s ease forwards 0.8s; }
.hero-actions { animation: fadeUp 0.8s ease forwards 1.1s; }
.hero-scroll { animation: fadeUp 0.8s ease forwards 1.5s; }
```

## Browser Support

- `@keyframes` + CSS transforms: All modern browsers
- `inline-block` on spans: Universal
- `setTimeout` stagger: Falls back to no animation (characters render as plain text)
- Degrade gracefully: Start text in DOM as plain text, JS upgrades to kinetic

## When to Use / Skip

**Use when**: Luxury/premium brands, beauty salons, creative agencies, fashion, any site wanting a "wow" first impression. Pairs best with dark themes and serif display fonts (Playfair Display, Cormorant Garamond).

**Skip when**: Content-heavy utility sites, government/medical, high-traffic landing pages (animations delay content visibility), SEO-critical pages (search engines see headings inside JS-spanned markup).

## Common Pitfalls

- **Space characters become zero-width in inline-block** — use `&nbsp;` with `width:0.3em`
- **Animation delay longer than preloader** — ensure preloader dismisses before char reveal starts
- **Multiple kinetic headings on one page** — only use for the primary H1; repeating the effect dilutes impact
- **Long headlines (10+ chars) feel slow** — use shorter stagger (25ms) or group into words instead of chars
- **Scroll-based re-trigger** — kinetic typography fires once on page load, not on scroll. Use IntersectionObserver only for section headers, not the main hero
