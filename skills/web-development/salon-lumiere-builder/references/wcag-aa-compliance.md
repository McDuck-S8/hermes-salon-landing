# WCAG 2.1 AA Compliance for Beauty Salon / Business Landing Pages

European Accessibility Act requires websites to meet WCAG 2.1 Level AA.
Apply ALL of these patterns to every landing page deployed for the EU market.

## Required Elements

### 1. Skip Link (WCAG 2.4.1)

First element after `<body>`:
```html
<a href="#main" class="skip-link">Перейти до змісту</a>
```

CSS:
```css
.skip-link{position:fixed;top:-100px;left:0;z-index:9999;padding:12px 24px;background:var(--gold);color:#0e0e0e;font-size:0.9rem;font-weight:500;border-radius:0 0 8px 0;transition:top 0.3s;text-decoration:none}
.skip-link:focus{top:0;outline:3px solid #fff}
```

### 2. ARIA Landmarks (WCAG 4.1.2)

| Element | Role | Attribute |
|---|---|---|
| `<header>` | `role="banner"` | — |
| `<nav>` | `role="navigation"` | `aria-label="Головне меню"` |
| `<main>` | `role="main"` | `id="main"` (matched by skip link) |
| `<footer>` | `role="contentinfo"` | — |

### 3. Focus Indicators (WCAG 2.4.7)

```css
*:focus-visible{outline:2px solid var(--gold);outline-offset:3px;border-radius:4px}
.btn:focus-visible,.form-submit:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
```

### 4. Form Labels (WCAG 1.3.1, 4.1.2)

EVERY form field MUST have `<label for="id">` matching `<input id="id">`:
```html
<label for="bname">Ім'я *</label>
<input type="text" id="bname" required>
```

### 5. Alt Texts (WCAG 1.1.1)

Descriptive Ukrainian-language alt text — NOT English labels:
- ✅ `alt="Майстер-стиліст робить стрижку жінці в салоні"`
- ✅ `alt="Процедура манікюру з УФ-лампою в салоні"`  
- ✅ `alt="Салон краси Fargo — світлий інтер'єр з дзеркалами"`
- ❌ `alt="Salon interior"` — English, too generic
- ❌ `alt="Nails"` — not descriptive for screen reader

### 6. aria-hidden on Decorative Icons (WCAG 4.1.2)

Wrap emoji that are purely decorative (not essential for understanding) in `<span aria-hidden="true">`:

```html
<button><span aria-hidden="true">✉️</span> Надіслати заявку</button>
<span class="h-icon" aria-hidden="true">💅</span>
```

### 7. WCAG Compliance Badge in Footer

Add to `.footer-bottom`:
```html
<span class="footer-acc-badge" aria-label="Сайт відповідає WCAG 2.1 рівень AA">
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
    <circle cx="12" cy="12" r="10"/><path d="M12 8v8M8 12h8"/><circle cx="12" cy="7" r="1.5" fill="currentColor" stroke="none"/>
  </svg>
  WCAG 2.1 AA
</span>
```

CSS:
```css
.footer-acc-badge{display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:4px;border:1px solid rgba(255,255,255,0.1);font-size:0.7rem;color:var(--text-muted)}
```

### 8. Touch Targets (WCAG 2.5.8 Level AA)

Social icons and buttons should be at least 24×24px touch target. Use 18px+ SVG icons in 36px+ containers:
```css
.footer-social a{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center}
.footer-social svg{width:18px;height:18px}
```

### 9. Color Contrast (WCAG 1.4.3)

Minimum contrast ratio 4.5:1 for normal text, 3:1 for large text.

Common dark-theme values that pass AA:
- Text #d4cfc8 on bg #0e0e0e → ~10.5:1 ✅
- Gold #c4954a on dark #0e0e0e → ~6.5:1 ✅
- Muted #8a857e on #0e0e0e → ~5.8:1 ✅
- **Avoid:** `rgba(255,255,255,0.4)` on dark backgrounds — drops below 4.5:1

### 10. Phone Links (must work)

No placeholder numbers — use real phone hrefs:
```html
<a href="tel:+380996140054">099 614 00 54</a>
```
❌ `tel:+380****0054` — does not work, fails WCAG

### 11. Accordion Behavior

All price/service accordion sections MUST start COLLAPSED on page load:
```html
<div class="price-block collapsed" id="price-haircut">
```

CSS to prevent content flash before JS wraps items:
```css
.price-block.collapsed > :not(h3){display:none}
.price-block.collapsed > .price-content{display:block;max-height:0}
.price-block:not(.collapsed) > .price-content{display:block}
```

### 12. Language Attribute

Always set `lang="uk"` or `lang="ru"` on `<html>` — never omit.

## Checklist Before Deploy

- [ ] Skip link present and functional
- [ ] All ARIA landmarks in place
- [ ] `:focus-visible` styles defined
- [ ] All form inputs have matching `<label for="id">`
- [ ] All images have descriptive Ukrainian alt text (not English)
- [ ] All decorative emoji wrapped in `<span aria-hidden="true">`
- [ ] WCAG badge in footer
- [ ] Social icons ≥ 18px SVG in 36px+ containers
- [ ] Color contrast passes 4.5:1
- [ ] Phone hrefs have real numbers (no ****)
- [ ] Accordions start collapsed
- [ ] `lang` attribute set on `<html>`
- [ ] No `mix-blend-mode:difference` on nav — use dark glass instead

## Common pitfalls

- **mix-blend-mode on nav:** Makes nav invisible at top — button appears to float on hero photo. Fix: use `background:rgba(14,14,14,0.75); backdrop-filter:blur(12px)` instead.
- **Emoji without aria-hidden:** Screen reader reads "pencil" for ✏️, "nail polish" for 💅. Always hide decorative emoji.
- **English alt text on Ukrainian site:** Screen reader pronounces "haircut" in English on a Ukrainian site. Always use the site's language.
- **Form labels without `for`:** Keyboard navigation breaks. Every `<label>` needs `for` matching `<input id>`.
- **Accordion first block open by default:** Users expect all collapsed on load. Set `collapsed` class on all blocks in HTML.
