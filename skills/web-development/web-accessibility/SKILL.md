---
name: web-accessibility
description: >
  WCAG 2.1 Level AA compliance for landing pages and business websites targeting the EU market.
  Covers skip links, ARIA landmarks, focus styles, alt texts, form labels, emoji, contrast, and
  accessibility badge in footer.
version: 1.0.0
platforms: [web]
---

# Web Accessibility (WCAG 2.1 AA) — Compliance Checklist

## Legal Context

EU **European Accessibility Act (EAA)** requires websites to meet WCAG 2.1 Level AA. Required for:
- Beauty salons, restaurants, hotels targeting EU tourists
- Any commercial site in Montenegro / EU-adjacent markets
- GitHub Pages sites are not exempt

## Mandatory Fixes (checklist)

### 1. Skip Link
```html
<a href="#main" class="skip-link">Перейти до змісту</a>
```
```css
.skip-link{position:fixed;top:-100px;left:0;z-index:9999;padding:12px 24px;background:var(--amber);color:#000;...}
.skip-link:focus{top:0}
```

### 2. ARIA Landmarks
- `<header role="banner">`
- `<nav role="navigation" aria-label="Головне меню">`
- `<main id="main" role="main">` — wraps all content between header and footer
- `<footer role="contentinfo">`

### 3. Focus Indicators
```css
*:focus-visible{outline:2px solid var(--gold);outline-offset:3px;border-radius:4px}
.btn:focus-visible,.form-submit:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
```

### 4. Descriptive Alt Texts (Ukrainian)
Bad: `alt="Salon interior"`  
Good: `alt="Інтер'єр салону краси Fargo"`

Bad: `alt="Nails"`  
Good: `alt="Процедура манікюру з УФ-лампою в салоні"`

### 5. Form Labels: `for` + `id`
```html
<label for="bname">Ім'я *</label>
<input type="text" id="bname" required>
```

### 6. Emoji Icons: `aria-hidden="true"`
Wrap every decorative emoji:
```html
<span aria-hidden="true">✏️</span> Записатись
<span aria-hidden="true">📅</span> Сьогодні
```

### 7. Touch Targets
Social icons: minimum 36×36px (44×44px preferred).
SVG icons: `width="18" height="18"` in 36px+ container.

### 8. WCAG Badge in Footer
```html
<span class="footer-acc-badge" aria-label="Сайт відповідає WCAG 2.1 рівень AA">
  <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 8v8M8 12h8"/><circle cx="12" cy="7" r="1.5" fill="currentColor" stroke="none"/></svg>
  WCAG 2.1 AA
</span>
```

### 9. Phone Numbers (no placeholders)
Bad: `href="tel:+380****0054"`  
Good: `href="tel:+380996140054"`

## Pexels Photo Selection for Beauty Salon

| Category | Good Pexels Photo IDs |
|---|---|
| Salon Interior | 3993320 |
| Haircut/Стрижки | 3992875 |
| Nails/Манікюр | 3997386 |
| Hair Color/Фарбування | 5069603 |
| Makeup/Макіяж | 5069604 |

## Pitfalls
- DO NOT delete existing content (social links, phone numbers) without asking — "if it was there, there was a reason"
- DO NOT use mix-blend-mode on headers — breaks accessibility (button invisible on photo)
- Verify the CORRECT file path before editing — the user may open a different variant (index.html vs index.trend.html)
- Always test with Ctrl+F5 (hard reload) — browser cache hides your fixes
- Gallery layout with 5+ items in a 3-column grid produces an implicit 3rd row — test all items are visible
