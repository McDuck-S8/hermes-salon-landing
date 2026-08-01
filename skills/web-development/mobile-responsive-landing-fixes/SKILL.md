---
name: mobile-responsive-landing-fixes
description: "Pattern for fixing common mobile responsiveness issues on landing pages: hamburger menu, carousel slides per view, touch targets, inline grid overrides, text overflow, and WCAG accessibility."
version: 1.0.0
author: hermes
tags:
- web-development
- mobile-first
- responsive-design
- landing-page
- wcag
- carousel
- hamburger-menu
category: web-development
---

# Mobile Responsive Landing Page Fixes

## Context
Fixed `https://mcduck-s8.github.io/hermes-salon-landing/cosmetologist/` — 5 major mobile issues found and fixed.

## Issues & Solutions

### 1. Hamburger Menu Invisible (Merged with Background)
**Problem:** `.mobile-toggle` had no background/border — white on white on mobile.
**Fix:**
```css
.mobile-toggle {
  display: none;
  flex-direction: column;
  gap: 5px;
  cursor: pointer;
  padding: 8px;
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  z-index: 101;  /* above nav */
}
@media(max-width:768px){ .mobile-toggle{display:flex} }
```

### 2. Mobile Menu Not Functional
**Problem:** `.header-nav` hidden on mobile but no toggle logic, no ARIA.
**Fix:**
```html
<button class="mobile-toggle" aria-expanded="false" aria-controls="header-nav" aria-label="Открыть меню">
  <span></span><span></span><span></span>
</button>
```
```javascript
const mobileToggle = document.querySelector('.mobile-toggle');
const headerNav = document.querySelector('.header-nav');
mobileToggle.addEventListener('click', () => {
  const isOpen = headerNav.classList.toggle('open');
  mobileToggle.setAttribute('aria-expanded', isOpen);
});
headerNav.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    headerNav.classList.remove('open');
    mobileToggle.setAttribute('aria-expanded', 'false');
  });
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && headerNav.classList.contains('open')) {
    headerNav.classList.remove('open');
    mobileToggle.setAttribute('aria-expanded', 'false');
    mobileToggle.focus();
  }
});
```
```css
@media(max-width:768px){
  .header-nav{
    position:fixed;top:70px;left:0;right:0;
    background:var(--white);flex-direction:column;padding:20px;gap:16px;
    border-bottom:1px solid var(--border);
    transform:translateY(-100%);opacity:0;visibility:hidden;
    transition:transform .3s ease, opacity .3s ease, visibility .3s ease;
    box-shadow:var(--shadow-md);z-index:100
  }
  .header-nav.open{transform:translateY(0);opacity:1;visibility:visible}
}
```

### 3. Carousel — 2 Slides on Mobile (Reviews/Before-After)
**Problem:** `#reviewTrack .carousel-slide` had `min-width:50%` — 2 slides visible, text overflow.
**Fix:**
```css
#reviewTrack .carousel-slide{min-width:50%;aspect-ratio:auto;display:flex;align-items:center;padding:16px 8px}
@media(max-width:768px){
  #reviewTrack .carousel-slide{min-width:100%}
}
```
Also: `initCarousel('reviewTrack', 'reviewDots', 1)` — visibleCount=1.

### 4. Inline Grid Styles Override Media Queries (About Section)
**Problem:** `<div style="display:grid;grid-template-columns:1fr 1fr 1fr">` — inline style beats CSS media queries.
**Fix:** Add `!important` to media queries:
```css
@media(max-width:768px){
  .about-single div[style*="grid-template-columns"]{grid-template-columns:1fr 1fr !important}
}
@media(max-width:480px){
  .about-single div[style*="grid-template-columns"]{grid-template-columns:1fr !important}
}
```

### 5. Touch Targets Too Small (Time Slots)
**Problem:** `<span class="slot-time">10:00</span>` — 32px height, hard to tap.
**Fix:** Convert to `<a>` with minimum 44×44px:
```css
.slot-time{
  display:inline-flex;align-items:center;justify-content:center;
  min-width:44px;min-height:44px;
  padding:8px 16px;border-radius:50px;
  border:1px solid var(--border);font-size:0.82rem;
  color:var(--text);cursor:pointer;transition:.3s;text-decoration:none
}
.slot-time:hover,.slot-time:focus{border-color:var(--teal);background:var(--teal);color:var(--white);outline:none}
```
```html
<a href="https://t.me/alliccenn" class="slot-time" target="_blank" rel="noopener">10:00</a>
```

### 6. Text Overflow / Horizontal Scroll (Page Width > 100vw)
**Problem:** Carousel `margin:0 -8px` + hero image + grids caused overflow.
**Fix:**
```css
body{overflow-x:hidden;max-width:100vw}
@media(max-width:768px){
  .carousel{margin:0 -20px;max-width:calc(100vw + 40px)}
  .carousel-track{width:100%}
  .hero-right img{max-width:100%;height:auto;display:block}
}
```

### 7. Carousel Images Distort (Aspect Ratio)
**Fix:** Use `aspect-ratio` + `object-fit:cover`:
```css
.carousel-slide img{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:var(--radius-sm);max-height:420px}
```

### 8. WCAG 2.1 AA (Claimed in Footer)
**Added:**
- Skip link: `<a href="#main" class="skip-link">Перейти к содержанию</a>`
- `focus-visible` outlines: `*:focus-visible{outline:2px solid var(--teal);outline-offset:3px;border-radius:4px}`
- ARIA on carousels: `aria-label`, `aria-controls`, `role="navigation"`
- Semantic buttons: `<button>` for carousel nav, not `<div>`
- Alt texts: descriptive (`alt="Коррекция асимметрии губ — до и после"`)

### 9. JS Cascade Failure — One Error Kills All Scripts
**Problem:** When multiple JS features share one `<script>`, a TypeError in the carousel blocks ALL subsequent code. Hamburger, scroll-reveal, and scroll-top all stop working silently.

**Fix — Isolated IIFE per feature with try/catch:**
```html
<script>
// ===== ISOLATED: Header scroll + scroll-top =====
(function(){try{
  var h=document.querySelector('.header'),st=document.getElementById('scrollTop');
  if(!h)return;
  window.addEventListener('scroll',function(){
    var y=window.scrollY>40;h.classList.toggle('scrolled',y);
    if(st)st.classList.toggle('visible',window.scrollY>300)
  },{passive:true});
}catch(e){console.warn('scroll:',e)}})();

// ===== ISOLATED: Scroll reveal =====
(function(){try{
  var els=document.querySelectorAll('.reveal');
  if(!els.length)return;
  // ... IntersectionObserver logic
}catch(e){console.warn('reveal:',e)}})();

// ===== ISOLATED: Hamburger menu =====
(function(){try{
  // ... toggle, overlay, Escape, resize, link click
}catch(e){console.warn('hamburger:',e)}})();

// ===== ISOLATED: Carousel =====
(function(){try{
  // ... slide logic, clone, transitionend
}catch(e){console.warn('carousel:',e)}})();
</script>
```

**Key rules:**
1. Every JS feature = its own `(function(){try{...}catch(e){console.warn('name:',e)}})()`
2. Guard clause at top: `if(!el)return;` — missing elements don't crash
3. `console.warn` so errors don't pollute but can be found
4. No shared mutable state between blocks
5. CSS controls visible count via `@media` queries — no JS `getCount()` function
6. ⚠️ **DO NOT stub `|}catch`** — the `|` is a line-number artifact. Write `}catch(e){` directly.

**Without isolation:** error in carousel → hamburger won't close, scroll-reveal won't trigger, scroll-to-top won't appear

### 9a. ⚠️ CRITICAL PITFALL: Stray `|` before `}catch(e){` kills ALL JS
**Problem:** A single stray pipe character `|` before `}catch(e){` causes a **SyntaxError at parse time**. Unlike runtime errors caught by `try/catch`, SyntaxErrors prevent the ENTIRE `<script>` block from being parsed/executed — every JS feature dies, including scroll reveal, hamburger, carousel, and scroll-to-top. No `console.warn` is emitted because nothing runs.

**Root cause:** Copy-paste artifact or diff artifact where `|` from a line-number prefix (e.g. `437|---content---`) leaks into the actual code. Common when copying code that has `|` as readability separator.

**Detection:**
```bash
# Extract JS and validate syntax
python -c "import re; f=open('index.html','r',encoding='utf-8'); m=list(re.finditer(r'<script>(.*?)</script>',f.read(),re.DOTALL)); open('/tmp/check.js','w').write(m[-1].group(1))"
node --check /tmp/check.js
```
If `node --check` reports a `SyntaxError`, grep for `|}catch`.

**Fix:** Remove the stray `|`:
```
-|}catch(e){console.warn('block:',e)}})();
+}catch(e){console.warn('block:',e)}})();
```

**Verification:** After fix, `typeof window.moveSlide` should return `"function"` (any exported function from the script block works as a canary).

### 9b. Scroll Reveal: ALWAYS default to visible (Progressive Enhancement)
**Problem:** Pattern `.reveal{opacity:0;...}.reveal.visible{opacity:1}` combined with IntersectionObserver means if the observer fails (SyntaxError kills JS, browser quirk, headless test environment, Browserbase), ALL sections below hero are invisible. User sees only hero section — everything below is `opacity:0` despite being in the DOM.

**Fix — sections visible by default, animation as enhancement only:**
```css
/* Sections always visible by default */
.reveal{opacity:1;transform:none;transition:opacity .6s ease,transform .6s ease}
/* Animation as enhancement — opt-in via JS-added class */
@media(prefers-reduced-motion:no-preference){
  .reveal-hidden{opacity:0;transform:translateY(20px)}
  .reveal-hidden.visible{opacity:1;transform:translateY(0)}
}
```
```js
// JS adds .reveal-hidden (which starts suppressed), IntersectionObserver removes it
document.querySelectorAll('.reveal').forEach(function(el){
  el.classList.add('reveal-hidden');
  obs.observe(el);
});
```

**Key principle:** If JS fails, content is fully visible. Animation is enhancement, not a requirement.

### 9c. Hero Layout: avoid `grid` + `dvh` + `overflow:hidden` on mobile
**Problem:** `.hero{min-height:90dvh;display:grid;grid-template-columns:1fr;overflow:hidden}` with child `order:-1` for mobile image-first layout caused sections below hero to be clipped or not render on mobile WebKit.

**Root cause:** `dvh` unit + `overflow:hidden` on a grid parent creates an unpredictable block formatting context. `min-height:90dvh` on a single-column grid with `order:-1` children can produce unexpected content height calculations on mobile.

**Fix — Simple `flex` with `column-reverse` on mobile:**
```css
.hero{display:block;padding-top:70px}
.hero-inner{display:flex;flex-wrap:wrap}
.hero-left,.hero-right{flex:1 1 50%;min-width:300px}
@media(max-width:768px){
  .hero-inner{flex-direction:column-reverse} /* image on top, text below */
}
```

**Benefits:** No `dvh` unit, no `overflow:hidden`, no `order` trick. `column-reverse` is universally supported and renders predictably.

### 10. Jekyll Strips &lt;title&gt; on GitHub Pages
**Problem:** GitHub Pages runs Jekyll on all HTML files. Without explicit layout directive, `<title>` is stripped.

**Fix — `_config.yml` defaults:**
```yaml
defaults:
  - scope:
      path: "cosmetologist"
    values:
      layout: none
      sitemap: false
```

NOT front matter in the HTML file (CRLF line endings on Windows break Jekyll front matter parsing).

### 11. GitHub Pages Build Delay
**Problem:** After push, Pages takes ~60-90 seconds to rebuild. During this time it may serve empty content (0 bytes) or a broken page. User opens site during build → thinks it's broken.

**Fix:** Wait 90s after push before verifying. Check with `curl -s -o /dev/null -w "%{http_code}" URL` — expect 200.

## Checklist for Future Landing Pages
- [ ] **JS isolation**: every feature in own IIFE + try/catch, guard clauses, `console.warn` on error
- [ ] **JS syntax validation**: `node --check` on extracted script — grep for `|}catch`
- [ ] Scroll reveal: `.reveal{opacity:1}` by default, animation via `.reveal-hidden` only
- [ ] Hero: avoid `grid`+`dvh`+`overflow:hidden` — use `flex` with `column-reverse` on mobile
- [ ] Hamburger: visible (bg+border), ARIA, toggle logic, Escape close, focus trap
- [ ] Carousel: 1 slide on ≤480px, 3 on ≥580px. CSS controls visible count, not JS
- [ ] Inline grids: media queries with `!important` OR move to CSS classes
- [ ] Touch targets: ≥44×44px, `<a>`/`<button>`, `:focus-visible`
- [ ] No horizontal scroll: `body{max-width:100vw;overflow-x:hidden}`, carousel negative margins compensated
- [ ] Images: `aspect-ratio` + `object-fit:cover`, descriptive alt
- [ ] Skip link, focus-visible, ARIA labels on all interactive components
- [ ] **Jekyll title**: `_config.yml` defaults with `layout: none` for page path
- [ ] **Build delay**: wait 90s after push, verify with curl, not browser

## Files
- `cosmetologist/index.html` — full fixed landing page
- `references/session-2026-07-23-cosmetologist-mobile-fixes.md` — first session (hamburger, WCAG, touch targets)
- `references/session-2026-07-29-js-cascade-fix.md` — second session (JS isolation, carousel infinite, Jekyll title)
- `references/session-2026-07-29-stray-pipe-syntaxerror.md` — third session (stray `|` SyntaxError, scroll reveal progressive enhancement, hero flex)
- This skill — pattern for reuse

## Related Skills
- `web-development/anti-slop-design` — Three Dials system
- `web-development/salon-lumiere-builder` — salon landing generator
- `web-development/small-business-landing-generator` — generic landing generator