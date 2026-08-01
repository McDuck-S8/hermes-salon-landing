---
name: auto-microsites
description: Lightweight JSON→HTML microsite generator for small businesses — Tailwind template, GitHub Pages deploy, $0 budget. Simpler alternative to full web-studio-ops pipeline for testing markets.
version: "1.0"
tags: [microsite, landing-page, small-business, github-pages, tailwind, json-template]
---

# Auto-Microsites Generator

## Summary
A minimal project (`projects/auto-microsites/`) that generates landing pages for small businesses from JSON config files. Uses a single universal Tailwind CSS template (via CDN), deploys to GitHub Pages for free hosting. Designed for $0 budget market testing.

## When to Use This vs web-studio-ops
| Use auto-microsites when... | Use web-studio-ops when... |
|----------------------------|---------------------------|
| Testing a new market with $0 budget | Running ongoing studio operations |
| Need 1-page landing only | Need multi-page sites, booking, CRM |
| Simple businesses (barber, dentist, cafe) | Complex projects needing design review |
| One-person rapid iteration | Team delivery with client approvals |
| Crimea/Simferopol market (payment constraints) | Kyiv/Ukraine market |

## Project Structure
```
projects/auto-microsites/
├── main.py              # JSON → HTML generator
├── deploy.py            # GitHub Pages deploy via gh CLI
├── templates/
│   └── business.html    # Universal Tailwind template
├── samples/             # JSON configs (barbershop, dental, etc.)
├── generated/           # Output sites (local)
└── deploy/              # Git repos for GitHub Pages
```

## Quick Start

### 1. Create a Business Config (JSON)
```json
{
  "project_name": "barin-barbershop",
  "business_name": "БАРИНЪ",
  "tagline": "Мужская классика и стиль",
  "phone": "+7 (978) 116-56-95",
  "address": "г. Симферополь, ул. Карла Маркса, 51",
  "working_hours": "Пн-Вс: 10:00-20:00, без выходных",
  "color_primary": "#1a1a2e",
  "color_accent": "#d4a574",
  "cta_text": "Записаться",
  "about": "Описание бизнеса...",
  "services": [
    {"name": "Мужская стрижка", "price": "от 800 ₽", "description": "..."}
  ],
  "seo_title": "БАРИНЪ — Барбершоп Симферополь",
  "seo_description": "Мужские стрижки от 800₽..."
}
```

### 2. Generate & Deploy
```bash
cd projects/auto-microsites
python main.py --from samples/barin.json
python deploy.py barin-barbershop --repo barin-barbershop-site
# → https://mcduck-s8.github.io/barin-barbershop-site/
```

### 3. Outreach
Use adapted template from `OUTREACH.md`:
- Channels: Яндекс.Карты → Telegram/WhatsApp, 2ГИС, Instagram DM, Авито
- Pricing: 7,000–25,000₽ (vs $300-400 in Kyiv)
- Payment: USDT TRC20 → KuCoin/OKX P2P → Т-Банк

## Template Features (business.html)
- Tailwind CSS via CDN (no build step)
- CSS variables for theming (--primary, --accent)
- Glassmorphism service cards
- Scroll-reveal animations (IntersectionObserver)
- Floating sticky CTA (tel: link)
- Full SEO meta + Open Graph tags
- Mobile-first responsive
- Russian language

## Simferopol Leads (Session 2026-07-14)
| Business | Type | Contact | Site | Demo |
|----------|------|---------|------|------|
## Simferopol Leads (Session 2026-07-14)
| Business | Type | Contact | Site | Demo |
|----------|------|---------|------|------|
| BroBarber | Барбершоп (3 лок.) | @brobarber_simf_01 | Instagram only | ✅ Deployed |
| Edward | Барбершоп | +7 (978) 722-13-13 | Yandex Maps + IG | ✅ Generated |
| МАРИ-ДЕНТ | Стоматология | +7 (978) 123-45-67 | Has site | ✅ Generated |
| БАРИНЪ | Барбершоп | +7 (978) 116-56-95 | Has site | ✅ Deployed |

## Fargo Fixes Applied to This Pipeline (2026-07-14)

**Nav link + button exclusion** — When header nav contains both plain `<a>` links and a CTA `<a class="btn btn-primary">`, the nav link color override on scroll (`.header.scrolled .header-nav a { color: var(--slate-light) }`) will also hit the button, turning its text dark. Fix: scope nav link rules with `:not(.btn)`:

```css
.header-nav a:not(.btn) { color: var(--white); }
.header.scrolled .header-nav a:not(.btn) { color: var(--slate-light); }
.header-nav a:not(.btn):hover { color: var(--terracotta); }
.header.scrolled .header-nav a:not(.btn):hover { color: var(--terracotta); }
```

**Header CTA button color consistency** — Keep the brand color (terracotta) + white text on BOTH dark hero and light scrolled header. Do NOT switch to dark bg on light background — it breaks visual continuity with the hero's primary CTA. The button IS the brand action; its identity must be stable.

```css
.header .btn-primary { background: var(--terracotta); color: var(--white); }
.header.scrolled .btn-primary { background: var(--terracotta); color: var(--white); }  /* same */
```

**GitHub Pages deploy patterns** — See `github-pages-deploy` skill for multi-client subdirectory pattern used in this session (docs/fargo/, docs/fargo-v2/).