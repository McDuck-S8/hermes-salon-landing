---
name: web-performance
description: "Web performance optimization — Core Web Vitals (LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1), image optimization (WebP/AVIF, responsive, lazy loading), caching, HTTP/2-3, preconnect, font loading. Run BEFORE publishing ANY site."
version: 1.0.0
tags: [performance, core-web-vitals, seo, images, caching, optimization]
---

# Web Performance Optimization

## Core Web Vitals Targets

| Metric | Good | Needs Work | Poor |
|--------|------|-----------|------|
| LCP (Largest Contentful Paint) | ≤ 2.5s | 2.5-4.0s | > 4.0s |
| INP (Interaction to Next Paint) | ≤ 200ms | 200-500ms | > 500ms |
| CLS (Cumulative Layout Shift) | ≤ 0.1 | 0.1-0.25 | > 0.25 |
| TTFB (Time to First Byte) | ≤ 800ms | 800-1800ms | > 1.8s |
| FCP (First Contentful Paint) | ≤ 1.8s | 1.8-3.0s | > 3.0s |

## Image Optimization (highest impact — 85% of pages have LCP from images)

### Format choice
```html
<!-- AVIF: best compression, modern (Chrome/Safari/FF) -->
<picture>
  <source srcset="photo.avif" type="image/avif">
  <source srcset="photo.webp" type="image/webp">
  <img src="photo.jpg" alt="..." loading="lazy" width="800" height="600">
</picture>
```

### Required attributes for CLS prevention
```html
<!-- ALWAYS set width + height — prevents layout shift -->
<img src="hero.jpg" alt="..." width="1200" height="800"
     loading="eager" fetchpriority="high" decoding="async">
```

### Lazy loading rules
- **DO** lazy-load below-fold images: `loading="lazy"`
- **NEVER** lazy-load the LCP image (16% of pages still do this!)
- **LCP image**: `loading="eager"` + `fetchpriority="high"`
- **Decode**: `decoding="async"` on all images (offloads decode from main thread)

### Responsive images
```html
<!-- srcset + sizes — browser picks right size -->
<img src="hero-800.jpg"
     srcset="hero-400.jpg 400w, hero-800.jpg 800w, hero-1200.jpg 1200w"
     sizes="(max-width: 768px) 100vw, 50vw"
     alt="..." width="800" height="600">
```

### CDN image services
- Cloudflare Images — transform on the fly: `/cdn-cgi/image/width=400,format=avif`
- Cloudinary — `w_400,f_avif`
- imgix — `?w=400&fm=avif`

### Checklist
- [ ] AVIF or WebP for all images
- [ ] Explicit `width` + `height` on every `<img>`
- [ ] LCP image: `loading="eager" fetchpriority="high"`
- [ ] Below-fold: `loading="lazy"`
- [ ] `srcset` + `sizes` for responsive images
- [ ] `decoding="async"` on all images

---

## Font Loading

### The right way (no FOIT/FOUT)
```html
<!-- 1. Preconnect to Google Fonts early -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<!-- 2. Preload main font -->
<link rel="preload" href="/fonts/inter-var.woff2" as="font" crossorigin>

<!-- 3. Font-display: swap (text visible immediately) -->
<style>
@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter-var.woff2') format('woff2');
  font-display: swap;        /* ← critical — no invisible text */
  font-weight: 100 900;
}
</style>
```

### Self-hosting (better than CDN for Core Web Vitals)
```bash
# Download + subset (use only needed characters)
npx @capsizecss/metrics inter
```

### Variable fonts
```css
/* One file, all weights — reduces requests */
@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter-var.woff2') format('woff2');
  font-weight: 100 900;
  font-stretch: 50 200;
  font-display: swap;
}
```

---

## HTTP Caching & CDN

### Cache headers
```
# Static assets — long cache
Cache-Control: public, max-age=31536000, immutable

# HTML — short cache
Cache-Control: public, max-age=0, must-revalidate

# Fonts — immutable
Cache-Control: public, max-age=31536000, immutable
```

### Preconnect / Prefetch / Preload
```html
<!-- Third-party: preconnect (opens connection early) -->
<link rel="preconnect" href="https://api.example.com">

<!-- Likely navigation: prefetch (idle-time download) -->
<link rel="prefetch" href="/next-page.html">

<!-- Critical CSS/font: preload (high priority, use sparingly) -->
<link rel="preload" href="/fonts/inter-var.woff2" as="font" crossorigin>
<link rel="preload" href="/critical.css" as="style">

<!-- DNS only -->
<link rel="dns-prefetch" href="https://fonts.googleapis.com">
```

### CDN recommendations
- **Cloudflare** — free plan, excellent for static sites (GitHub Pages, Vercel)
- **Vercel Edge** — if using Next.js
- **GitHub Pages** + Cloudflare proxying for free CDN + caching

---

## CSS & JS Delivery

### Critical CSS
```html
<!-- Inline critical CSS in <head>, defer the rest -->
<style>
  /* Above-fold styles only — hero, nav, typography */
</style>
<link rel="preload" href="/styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="/styles.css"></noscript>
```

### JavaScript
- `defer` for scripts that need DOM (loads after HTML parsed)
- `async` for analytics (loads ASAP, no order guarantee)
- No render-blocking JS (move to end of `<body>` or use `defer`)

```html
<!-- Analytics: async -->
<script src="https://cdn.example.com/analytics.js" async></script>

<!-- App scripts: defer -->
<script src="/app.js" defer></script>
```

---

## Resource Hints Ordering

```
Priority order for <head>:
1. <meta charset>, <meta viewport>
2. <title>, <meta description>
3. preconnect (fonts.googleapis.com, api.yourdomain.com)
4. preload (critical fonts, LCP image)
5. inline critical CSS
6. prefetch (likely next page)
7. dns-prefetch (all other third-parties)
8. deferred stylesheets
9. deferred scripts
```

---

## Single-Page & Static Site Checklist

- [ ] No render-blocking JS above-fold
- [ ] Font-display: swap (no invisible text)
- [ ] Images: AVIF/WebP, explicit dimensions, lazy load below-fold
- [ ] LCP image: preloaded + eager + fetchpriority=high
- [ ] Preconnect to third-party origins
- [ ] Minified HTML/CSS/JS
- [ ] Gzip/Brotli compression (server-level)
- [ ] Cache headers: long TTL for static assets
- [ ] HTTP/2 or HTTP/3 (h2/h3)
- [ ] Prefetch likely navigation targets
- [ ] No unused CSS (purge with Lightning CSS or Tailwind)
- [ ] No excessive DOM depth (< 32 levels)
- [ ] Lighthouse score ≥ 90 (mobile + desktop)

## Measuring

```bash
# Lighthouse CLI
npx lighthouse https://example.com --view --preset=desktop

# WebPageTest — real browser metrics
curl https://www.webpagetest.org/runtest.php?url=https://example.com&f=json

# CrUX Report API (real user data)
curl "https://chromeuxreport.googleapis.com/v1/records:queryRecord?key=$API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"origin": "https://example.com"}'
```

## Common Mistakes
- Lazy-loading LCP image → delays hero by 2-3s
- No explicit image dimensions → CLS spikes
- Invisible text while fonts load (no font-display)
- Too many HTTP requests (bundle CSS/JS)
- Unoptimized images (JPEG > 100KB when WebP would be 30KB)
- No preconnect to critical third-party origins
- HTTP/1.1 instead of HTTP/2 (6 connections limit)
