# WCAG 2.1 Level AA — Landing Page Requirements

## Must-Have (check before deploy)

### 1. Skip Link
First focusable element on the page. Hidden until focused via Tab.
```html
<a href="#main" class="skip-link">Перейти до змісту</a>
```
```css
.skip-link{position:fixed;top:-100px;left:0;z-index:9999;padding:12px 24px;background:var(--gold);color:#000;border-radius:0 0 8px 0;transition:top 0.3s}
.skip-link:focus{top:0;outline:3px solid #fff}
```

### 2. Focus Indicators
Every interactive element must have visible focus style.
```css
*:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:4px}
.btn:focus-visible,.form-submit:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
```

### 3. ARIA Landmarks
Wrap content in `<main id="main" role="main">`, header `role="banner"`, nav `role="navigation" aria-label="Головне меню"`, footer `role="contentinfo"`.

### 4. Form Labels
Every `<input>`, `<select>`, `<textarea>` needs a `<label for="id">` with matching `id` on the input. Never use bare `<label>` without `for`.
```html
<label for="bname">Ім'я *</label>
<input type="text" id="bname" required>
```

### 5. Alt Text on Images
Descriptive Ukrainian/Russian text. Not "Salon interior" but "Інтер'єр салону краси Fargo — світлий простір з дзеркалами". Not "Nails" but "Процедура манікюру з УФ-лампою в салоні".

### 6. aria-hidden on Emoji
All decorative emoji must be hidden from screen readers:
```html
<span aria-hidden="true">✏️</span> Записатись
```
Not just emoji, but ANY decorative icon (SVG without text).

### 7. Color Contrast (WCAG AA)
- Normal text (<18px or <14px bold): 4.5:1 minimum
- Large text (≥18px or ≥14px bold): 3:1 minimum
- Gold (#c4954a) on dark bg (#0e0e0e): ~6.5:1 ✅
- White text on gold bg: ~2.2:1 ❌ — use dark text on gold buttons

Best practice: test with https://webaim.org/resources/contrastchecker/

### 8. Touch Targets
Interactive elements (links, buttons) should be minimum 44×44px on mobile.

## Schema Fix — Pexels Gallery Photos

Do NOT guess Pexels photo IDs. Search or verify first.

### Safe Salon/Nail IDs (verified working)
| Category | Pexels ID | alt text |
|---|---|---|
| Salon interior | 3993320 | Інтер'єр салону краси |
| Haircut/styling | 3992875 | Майстер-стиліст робить стрижку |
| Nails/manicure | 3997386 | Процедура манікюру з УФ-лампою |
| Hair color | 5069603 | Стиліст фарбує волосся |
| Makeup | 5069604 | Візажист наносить макіяж |

### Pitfalls
- `pexels-photo-5069601` is NOT a makeup photo — it's a bird/image error. Always verify Pexels content.
- `pexels-photo-18426792` (hair color) doesn't load reliably → use 5069603 or 3993383 instead.
- If Pexels returns 403 on HEAD requests, the image still loads in browsers — test with browser, not curl.
