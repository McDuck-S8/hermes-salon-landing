# Cosmetologist Site Deployment — 2026-07-29

## Context
- Repo: `McDuck-S8/hermes-salon-landing`
- Default branch: `user/hermes-session-2026-06-09`
- Pages: enabled, source = root of default branch
- Site: `https://mcduck-s8.github.io/hermes-salon-landing/cosmetologist/`

## Critical Mistake

**Pushed to `gh-pages` branch via the `D:/gh-pages-deploy` worktree** — had NO effect because Pages serves from the **root of the default branch**, not from `gh-pages`.

```bash
# Wrong (pushed to irrelevant branch):
cd /d/gh-pages-deploy && git add cosmetologist/index.html && git commit -m "..." && ALL_PROXY=socks5h://127.0.0.1:10806 git push origin gh-pages

# Correct (push to Pages source branch):
cd /d/Portable_Soft/hermes && cp /d/gh-pages-deploy/cosmetologist/index.html cosmetologist/index.html && git add cosmetologist/index.html && git commit -m "..." && ALL_PROXY=socks5h://127.0.0.1:10806 git push origin user/hermes-session-2026-06-09
```

## How to Detect Pages Source Without gh CLI

```bash
# Compare raw file vs live URL content:
curl -s https://raw.githubusercontent.com/OWNER/REPO/DEFAULT_BRANCH/PATH/ | grep "UNIQUE_MARKER"
curl -s https://LIVE_URL | grep "UNIQUE_MARKER"
# If markers match → Pages serves from default branch
```

## Frontend Issues Found Post-Deploy

### 1. Missing `<title>` tag
Rewriting the HTML accidentally removed the `<title>`. GitHub Pages generates a title from filename when missing, but result is unpredictable.

### 2. Hamburger CSS without HTML
`.mobile-toggle{display:flex}` existed in CSS but `<button class="mobile-toggle">` was never added to `<header>`. Fix: add the button with `<span>` children in the header.

### 3. Carousel JS hardcoded to 3 slides
`initCarousel('carouselTrack', 'carouselDots', 3)` — on mobile (<481px), CSS made slides 100% wide but JS still scrolled by 33.3%. Fix:

```js
var count = window.innerWidth < 481 ? 1 : 3;
initCarousel('carouselTrack', 'carouselDots', count);
// Re-init on resize (debounced, no location.reload)
window.addEventListener('resize', function(){
  clearTimeout(rt);
  rt = setTimeout(reinit, 400);
});
```

### 4. Inline grid columns break on mobile
`<div style="grid-template-columns:1fr 1fr 1fr">` on about grid — no media query override possible without `!important`. Fixed by adding `.about-grid` class and `!important` in media query.

### 5. Reviews grid used wrong selector
`#reviewTrack` used inline 2-column grid. Media query overrode `.reviews-grid{grid-template-columns:1fr}` but that class wasn't used. Fixed by adding `#reviewTrack` to the media query selector.

## Deployment Setup
- Source file: `D:\Portable_Soft\hermes\cosmetologist\index.html`
- Edit file: `D:\gh-pages-deploy\cosmetologist\index.html`
- Deploy command: `cp /d/gh-pages-deploy/cosmetologist/index.html /d/Portable_Soft/hermes/cosmetologist/ && git add cosmetologist/ && git commit && git push`
- Required: Proxy `ALL_PROXY=socks5h://127.0.0.1:10806` for git push
