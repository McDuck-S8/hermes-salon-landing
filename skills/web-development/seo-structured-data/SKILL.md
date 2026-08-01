---
name: seo-structured-data
description: "SEO и структурированные данные — meta tags, Open Graph, Twitter Cards, JSON-LD schema (Article, LocalBusiness, FAQ, Product, Organization), sitemap, robots.txt, canonical, hreflang. Load BEFORE generating any production page."
version: 1.0.0
tags: [seo, schema, structured-data, open-graph, json-ld, meta-tags]
---

# SEO & Structured Data

## Critical Meta Tags (every production page)

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <title>Название компании — Услуги в Симферополе | Крым</title>
  <meta name="description" content="Описание до 155 символов с ключевыми словами и регионом.">

  <!-- Canonical (avoid duplicate content) -->
  <link rel="canonical" href="https://example.com/page/">

  <!-- Language / region -->
  <meta http-equiv="content-language" content="ru">

  <!-- Robots -->
  <meta name="robots" content="index, follow">

  <!-- Theme color (mobile browser chrome) -->
  <meta name="theme-color" content="#1a1a2e">
</head>
```

## Open Graph (social previews)

```html
<!-- Facebook / VK / LinkedIn -->
<meta property="og:type" content="website">
<meta property="og:title" content="Заголовок (до 60 символов)">
<meta property="og:description" content="Описание (до 155 символов)">
<meta property="og:url" content="https://example.com/page/">
<meta property="og:image" content="https://example.com/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="ru_RU">
<meta property="og:site_name" content="Название сайта">

<!-- Twitter (X) -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Заголовок">
<meta name="twitter:description" content="Описание">
<meta name="twitter:image" content="https://example.com/og-image.jpg">
```

### OG Image specs
- Size: 1200×630px (1.91:1 ratio)
- Format: PNG or JPG
- Max: 5MB (ideally < 300KB)
- Text: keep center-safe (may be cropped 120px top/bottom on some platforms)
- No transparent PNG — dark mode apps will have white border issues

### Testing
```bash
# Facebook
curl -I "https://graph.facebook.com/v19.0/?id=https://example.com&scrape=true"

# Twitter/X
curl "https://cards-dev.twitter.com/validator" -d "url=https://example.com"

# Yandex preview — no separate validator, check via Yandex.Webmaster
```

---

## JSON-LD Structured Data

### Organization (every business site)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Название компании",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "description": "Описание деятельности",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Симферополь",
    "addressRegion": "Крым",
    "streetAddress": "ул. Ленина, 12"
  },
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+7-978-000-00-00",
    "contactType": "customer service",
    "availableLanguage": ["Russian"]
  },
  "sameAs": [
    "https://t.me/your_channel",
    "https://vk.com/your_page"
  ]
}
</script>
```

### LocalBusiness (for SALON/CLINIC/SHOP — Yandex/Google maps)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": ["LocalBusiness", "BeautySalon"],
  "name": "Салон красоты Название",
  "image": "https://example.com/salon.jpg",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Симферополь",
    "streetAddress": "ул. Ленина, 12"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 44.9482,
    "longitude": 34.1003
  },
  "openingHours": "Mo-Sa 09:00-20:00",
  "telephone": "+7-978-000-00-00",
  "priceRange": "₽₽₽",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "127"
  }
}
</script>
```

### Article / BlogPosting
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Заголовок статьи",
  "description": "Краткое описание",
  "image": "https://example.com/article-image.jpg",
  "datePublished": "2026-06-01T08:00:00+03:00",
  "dateModified": "2026-06-15T10:30:00+03:00",
  "author": {
    "@type": "Organization",
    "name": "Название компании"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Название компании",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }
  }
}
</script>
```

### FAQPage (Q&A sections — rich snippet in search)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "Сколько стоит стрижка?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Стрижка от 1500 рублей."
    }
  }, {
    "@type": "Question",
    "name": "Работаете в воскресенье?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Да, с 10:00 до 18:00."
    }
  }]
}
</script>
```

### BreadcrumbList
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [{
    "@type": "ListItem",
    "position": 1,
    "name": "Главная",
    "item": "https://example.com/"
  }, {
    "@type": "ListItem",
    "position": 2,
    "name": "Услуги",
    "item": "https://example.com/services/"
  }, {
    "@type": "ListItem",
    "position": 3,
    "name": "Стрижка",
    "item": "https://example.com/services/haircut/"
  }]
}
</script>
```

### WebSite search (site search in Google)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://example.com/search?q={search_term_string}"
    },
    "query-input": "required name=search_term_string"
  }
}
</script>
```

### LocalBusiness specific types for Yandex
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BeautySalon",
  "name": "Название салона",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Симферополь",
    "addressRegion": "Крым"
  }
}
</script>
```

Subtypes by vertical: `BeautySalon`, `HairSalon`, `HealthAndBeautyBusiness`, `NailSalon`, `MedicalClinic`, `Dentist`, `AutoRepair`, `Restaurant`, `CafeOrCoffeeShop`, `Store`, `ClothingStore`

---

## Sitemap & Robots

### robots.txt
```txt
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /private/
Sitemap: https://example.com/sitemap.xml
```

### sitemap.xml (static site)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <priority>1.0</priority>
    <changefreq>weekly</changefreq>
  </url>
  <url>
    <loc>https://example.com/services/</loc>
    <priority>0.8</priority>
    <changefreq>monthly</changefreq>
  </url>
  <url>
    <loc>https://example.com/contacts/</loc>
    <priority>0.6</priority>
    <changefreq>monthly</changefreq>
  </url>
</urlset>
```

### Yandex-specific
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- Yandex supports standard sitemaps. Add to Yandex.Webmaster -->
<!-- Also add to Google Search Console -->
```

---

## RU-specific SEO

- **Yandex.Webmaster** — обязателен для RU трафика (Google Search Console тоже)
- **Регион в мета-тегах** — `geo.region`, `geo.position` для локального бизнеса
- **Домен .ru или .рф** — ранжируется выше в Яндексе для RU запросов
- **Hreflang** — для multi-region (Крым/РФ)
```html
<link rel="alternate" hreflang="ru" href="https://example.com/">
<link rel="alternate" hreflang="x-default" href="https://example.com/">
```
- **152-ФЗ** — форма согласия на обработку персональных данных (чекбокс обязателен)
- **Яндекс.Метрика** — вместо Google Analytics (GA заблокирован в РФ)
- **Dzen** — альтернатива Google Discover для RU рынка

---

## Performance-SEO intersection

- LCP ≤ 2.5s — Core Web Vital, влияет на ранжирование
- Mobile-first indexing — Google индексирует мобильную версию
- INP ≤ 200ms — UX метрика, влияет на ранжирование с 2024
- No intrusive interstitials — попапы на весь экран штрафуются

---

## Checklist (pre-publish)

- [ ] `<title>` уникальный на каждой странице, ≤ 60 символов
- [ ] `<meta description>` ≤ 155 символов, с регионом
- [ ] `<link rel="canonical">` — без дублей
- [ ] Open Graph (og:title, og:description, og:image, og:url)
- [ ] Twitter Card (summary_large_image)
- [ ] JSON-LD Organization (всегда)
- [ ] JSON-LD LocalBusiness (для бизнеса с адресом)
- [ ] JSON-LD BreadcrumbList (на внутренних страницах)
- [ ] robots.txt + sitemap.xml
- [ ] Яндекс.Метрика (не GA — заблокирован)
- [ ] Чекбокс 152-ФЗ на формах
- [ ] Mobile-friendly (тест Google)
- [ ] Core Web Vitals (LCP, INP, CLS)
- [ ] Hreflang если multi-region
- [ ] HTTPS (обязательно)

## Testing tools
```bash
# Rich Results Test (Google)
curl "https://search.google.com/test/rich-results?url=https://example.com"

# Schema.org validator
curl "https://validator.schema.org/validate?url=https://example.com"

# Яндекс.Вебмастер
# https://webmaster.yandex.ru/

# PageSpeed Insights
npx lighthouse https://example.com --view

# Mobile-friendly
curl "https://search.google.com/test/mobile-friendly?url=https://example.com"
```
