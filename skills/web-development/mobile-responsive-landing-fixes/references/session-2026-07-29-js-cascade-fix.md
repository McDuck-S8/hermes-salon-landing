# Session 2026-07-29: Cosmetologist Landing — JS Cascade Fix + Carousel Reorder

## URL
https://mcduck-s8.github.io/hermes-salon-landing/cosmetologist/

## Root Problem
All JS ran in one flat `<script>` block. Any error in carousel (e.g. `null.querySelector()`) killed ALL subsequent code: hamburger wouldn't close, scroll-reveal wouldn't trigger, scroll-to-top wouldn't appear.

## Fix Applied
Wrapped every JS feature in its own IIFE + try/catch:

```js
// ===== ISOLATED: Header scroll + scroll-top =====
(function(){try{
  var h=document.querySelector('.header'),st=document.getElementById('scrollTop');
  if(!h)return;
  window.addEventListener('scroll',function(){
    var y=window.scrollY>40;h.classList.toggle('scrolled',y);
    if(st)st.classList.toggle('visible',window.scrollY>300)
  },{passive:true});
|}catch(e){console.warn('scroll:',e)}})();
```

4 isolated blocks: scroll, reveal, hamburger, carousel.

## Carousel Change
- Reordered slides: more1, more2, more3, lips1, botox1, lips2 (4-5-6 first)
- Infinite scroll: clones at init, `current=step`, `transitionend` for edge reset
- Dots: `Math.ceil(totalReal / visible)` with active dot highlighting
- Visible count controlled by CSS, not JS: `@media(max-width:580px)` = 1 slide, default = 3

## Jekyll Title Issue
`<title>` was stripped by Jekyll. Fix via `_config.yml`:
```yaml
defaults:
  - scope:
      path: "cosmetologist"
    values:
      layout: none
      sitemap: false
```

Not front matter in HTML — CRLF line endings break Jekyll.

## Added
- Favicon: inline SVG data URI (💉 on teal bg)
- Scroll-to-top button: appears after 300px scroll
- Both in isolated JS blocks, survive carousel failure

## Build Issue
After push, GitHub Pages returns empty content for ~60-90s. User opened site during build. Verify with curl after delay:
```bash
curl -s -o /dev/null -w "%{http_code}" "https://mcduck-s8.github.io/hermes-salon-landing/cosmetologist/"
```
Expect 200 and non-zero byte count.

## Files
- `cosmetologist/index.html` — complete page with isolated JS
- `_config.yml` — Jekyll defaults for title preservation
