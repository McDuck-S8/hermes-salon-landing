# Nav mix-blend-mode Pitfall — 2026-07-22

## Symptom
Header with `mix-blend-mode:difference` makes nav content (buttons, logo) visually float on the hero background photo. Button appears to "ride on" or overlap the photo. Scrolled state with background looks fine.

## Root Cause
`mix-blend-mode:difference` inverts the color of every pixel behind the element. Without a background, the entire header is transparent — it just inverts the photo behind it. Buttons inside the nav have no visual container, creating the illusion they're positioned directly on the hero photo.

```css
/* ❌ WRONG — button floats on photo */
.header {
  position: fixed; top: 0;
  padding: 20px 0;
  mix-blend-mode: difference;  /* transparent + invert */
  background: transparent;
}
.header.scrolled { background: rgba(14,14,14,0.88); mix-blend-mode: normal; }
```

## Fix: Glass-morphism nav from page load

```css
/* ✅ RIGHT — nav visible as a distinct bar from the start */
.header {
  position: fixed; top: 0;
  padding: 16px 0;
  background: rgba(14,14,14,0.75);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
.header.scrolled { background: rgba(14,14,14,0.92); backdrop-filter: blur(20px); padding: 12px 0; }
```

The header must be **immediately visible as a distinct UI element**. A semi-transparent dark background with blur creates a premium glass effect while keeping buttons visually contained within the nav bar.

## Additional Considerations

### Hero Padding
Even with a solid nav, the fixed header overlaps the hero section. Account for nav height:

```css
.hero-left { padding-top: 80px; }    /* enough for nav height + breathing room */
.hero { padding-top: 80px; }         /* for vertical-center hero sections */
```

### Scroll Threshold
Match the scroll threshold to when the nav should visually tighten:

```js
window.addEventListener('scroll', () =>
  header.classList.toggle('scrolled', window.scrollY > 60)
);
```

### Footer Social Buttons
Demo landing pages often have placeholder `href="#"` for social icons. Before deploying, verify every `<a>` in footer has a real URL. Common fixes:

```html
<!-- Before: placeholder -->
<a href="#..." target="_blank" aria-label="Telegram">...</a>

<!-- After: real link from existing business contacts -->
<a href="https://t.me/fargosalon" target="_blank" aria-label="Telegram">...</a>
```

If a social platform has no associated account, **remove the icon entirely** rather than leaving a dead link.

## Rule
> Never use `mix-blend-mode:difference` on a fixed nav without an accompanying background. The nav must always be a visually distinct container — buttons, text, and CTAs need a defined bar to sit in.
