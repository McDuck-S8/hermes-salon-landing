---
name: small-business-landing-generator
description: Generate and deploy demo landing pages for small businesses (barbershops, salons, clinics, auto repair). Template-based JSON → HTML → GitHub Pages pipeline with anti-slop design standards. Includes outreach workflow for client acquisition.
version: "1.0"
tags: [web, demo, studio, business, automation, github-pages, anti-slop]
---

# Small Business Landing Page Generator

## Overview

Automated pipeline: **JSON config → HTML landing page → GitHub Pages deploy → outreach DM**.

Used for G003 First Revenue Test: build portfolio of demo sites for Simferopol businesses without websites, then pitch owners.

---

## Project Structure

```
auto-microsites/
├── main.py              # Generator: JSON → index.html (single file, inline CSS/JS)
├── deploy.py            # Deploy to GitHub Pages via gh CLI
├── templates/
│   └── business.html    # Template with {{PLACEHOLDERS}}
├── samples/
│   ├── barbershop.json  # Example: barber (high conversion niche)
│   ├── dental.json      # Example: dental (high ticket)
│   ├── barin.json       # Real Simferopol barbershop (only Instagram)
│   ├── edward.json      # Real Simferopol barbershop (Yandex Maps only)
│   ├── mari-dent.json   # Real Simferopol clinic
│   └── brobarber.json   # Real Simferopol network (3 locations, Instagram only)
├── generated/           # Output sites (gitignored)
│   ├── barin-barbershop/index.html
│   ├── brobarber/index.html
│   └── ...
├── deploy/              # Temp clone dir for gh-pages push (gitignored)
├── OUTREACH.md          # DM template + lead sourcing strategy
└── README.md
```

---

## Quick Start

```bash
# Generate from sample
cd D:/Portable_Soft/hermes/projects/auto-microsites
python main.py --from samples/barbershop.json

# Generate from custom JSON
python main.py --from /path/to/custom.json

# Deploy to GitHub Pages (requires gh auth login)
python deploy.py barin-barbershop --repo barin-barbershop-site

# List generated
python main.py --list
```

---

## JSON Config Schema

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
  "about": "БАРИНЪ — барбершоп для мужчин, которые ценят качество...",
  "services": [
    {"name": "Мужская стрижка", "price": "от 800 ₽", "description": "Классическая или модельная стрижка с укладкой"},
    {"name": "Королевское бритьё", "price": "от 700 ₽", "description": "Опасное бритво, горячие полотенца, массаж лица"},
    {"name": "Коррекция бороды", "price": "от 500 ₽", "description": "Моделирование, окантовка, уход"}
  ],
  "seo_title": "БАРИНЪ — Барбершоп Симферополь | Мужские стрижки, бритьё, борода",
  "seo_description": "Барбершоп БАРИНЪ в Симферополе. Мужские стрижки от 800₽, королевское бритьё, коррекция бороды. Запись по телефону +7 (978) 116-56-95. ул. Карла Маркса, 51."
}
```

**Required:** `project_name`, `business_name`, `phone`  
**Optional (with defaults):** all others

---

## Template: `templates/business.html`

Modern single-page landing with:
- **Hero**: gradient dark bg, kinetic headline, sticky CTA (tel:)
- **Services**: responsive grid, hover lift, price badges
- **About**: glassmorphism card, left border accent
- **Contact**: 3-card grid (phone, address, hours)
- **Floating CTA**: fixed bottom-right call button
- **Scroll animations**: IntersectionObserver fade-in
- **SEO**: meta tags, Open Graph, JSON-LD ready

**Design tokens** (CSS variables):
```css
:root {
  --primary: {{COLOR_PRIMARY}};   /* #2563eb default */
  --accent: {{COLOR_ACCENT}};     /* #f59e0b default */
  --dark: #1a1a2e;
  --light: #f8fafc;
  --text: #334155;
  --radius: 12px;
}
```

---

## Anti-Slop Design Integration

**MUST load `anti-slop-design` skill before building**. Template already avoids:
- ❌ Cream/beige backgrounds (`#f5f0e8`, `#f8f5f0`)
- ❌ Brass/gold defaults (`#b08947`)
- ❌ Playfair Display as unquestioned default
- ❌ Em-dashes (—) — use hyphens (-)
- ❌ Three equal cards — template uses varied grid
- ❌ Generic "Elevate/Seamless/Unleash" copy

**Color rotation per niche** (per anti-slop-design Section 2):
| Niche | Primary | Accent | Surface |
|-------|---------|--------|---------|
| Barbershop | Terracotta `#c46a4a` | Amber `#c4954a` | Warm off-white `#f7f4f0` |
| Dental/Clinic | Teal `#0a7b83` | Coral `#e86c4a` | Cool white `#f8fafb` |
| Auto Repair | Blue `#1e3a5f` | Orange `#e67e22` | Light gray `#f8f9fa` |
| Legal/Finance | Slate `#334155` | Emerald `#10b981` | White `#ffffff` |
| Fitness/Yoga | Forest `#166534` | Lime `#84cc16` | Off-white `#f7fef7` |

---

## Deployment: `deploy.py`

```python
# Usage: python deploy.py <project_name> [--repo <repo_name>]
# 1. Checks gh CLI + auth
# 2. Creates repo if missing (public)
# 3. Clones to deploy/<repo>
# 4. Copies generated/<project>/index.html
# 5. Commits + pushes
# 6. Enables GitHub Pages (main branch, / root)
# 7. Returns: https://USER.github.io/REPO/
```

**Requirements**: `gh` CLI installed, `gh auth login` done.

---

## Outreach Workflow (`OUTREACH.md`)

### Lead Sources (Simferopol)
1. **Яндекс.Карты** — search "барбершоп Симферополь", "стоматология Симферополь" → filter no website
2. **2ГИС** — same
3. **Instagram** — business accounts WITHOUT website link in bio
4. **Avito** — business listings → contact phone

### Target Niches (high ticket / willingness to pay)
| Niche | Avg Client Ticket | Willingness |
|-------|-------------------|-------------|
| Dental | 5,000-50,000₽ | High |
| Auto repair | 3,000-30,000₽ | High |
| Legal/Accounting | 5,000-20,000₽ | High |
| Barbershop | 800-2,000₽ | Medium |
| Fitness/Yoga | 2,000-5,000₽ | Medium |

### DM Template (Telegram/WhatsApp)
```
Здравствуйте, [ИМЯ]!

Я Алексей, веб-разработчик из Симферополя. Нашёл ваш [салон/барбершоп/клинику] в [Яндекс.Картах/Instagram] — выглядит отлично!

Заметил, что у вас нет сайта. Это теряет клиентов: люди ищут в Google/Яндекс → не находят → идут к конкуренту.

Я делаю профессиональные сайты для бизнеса:
— Лендинг с услугами и ценами
— Кнопка «Позвонить» (sticky, всегда видна)
— Мобильная версия (70% клиентов с телефона)
— Запись онлайн через Telegram
— SEO-оптимизация (чтобы находили в Яндексе)

Стоимость: от 7 000₽ (одностраничный сайт)
Срок: 3-5 дней. Без предоплаты.

Хотите — покажу пример за 2 минуты. Могу сделать демо-сайт именно для вашего бизнеса бесплатно.

[ССЫЛКА НА ДЕМО-САЙТ]

С уважением,
Алексей
```

---

## Portfolio Index

Generate `docs/index.html` with cards linking to all live demos:

```html
<div class="portfolio-grid">
  <a class="card" href="https://mcduck-s8.github.io/barin-barbershop-site/">
    <h3>БАРИНЪ — Барбершоп</h3>
    <span class="niche">Barbershop</span>
  </a>
  <!-- ... -->
</div>
```

---

## Lessons Learned (Session 2026-07-14)

### Template Quality
- **First template was weak**: generic, no personality, AI-tell colors (dark+gold+glassmorphism)
- **Fix**: Adopt anti-slop-design niche palettes. Rotate terracotta/slate for barbershops, teal/coral for clinics.
- **Copy matters**: Real business names, addresses, phones from Yandex Maps/Instagram — not placeholders.

### Nav mix-blend-mode Pitfall (Session 2026-07-22 — Fargo v3 Trend)

**Problem:** `mix-blend-mode:difference` on a fixed header makes it transparent — it only inverts background colors. Buttons inside the nav appear to "float" directly on the hero photo with no visual container.

**Fix:** Replace with glass-morphism background from load:
```css
.header {
  background: rgba(14,14,14,0.75);
  backdrop-filter: blur(12px);
}
```
See `references/nav-mix-blend-mode-pitfall.md` for full fix and footer social button audit.

### Landing Page Implementation Learnings (Session 2026-07-18 — Beauty Salon Fargo)

**Preloader** — Must dismiss immediately to avoid flash:
```html
<div id="preloader">...</div>
<script>
  const p = document.getElementById('preloader');
  if (p) p.classList.add('loaded');
</script>
```
Inline script right after element — runs before paint.

**Nav Bar** — Solid from Start:
```css
nav {
  background: rgba(10,10,10,0.85);  /* NOT transparent */
  backdrop-filter: blur(20px) saturate(1.2);
  border-bottom: 1px solid var(--glass-border);
}
nav.scrolled { background: rgba(10,10,10,0.95); }
```
No flash of transparent nav over hero content.

**Hero Padding** — Account for fixed nav:
```css
.hero { padding: 160px 40px 80px; }  /* 160px top = nav height + breathing room */
```
Prevents headline being cut off behind nav.

**Nav Structure** — Full menu + actions:
```html
<nav id="nav">
  <a href="#" class="nav-logo">F<span>ARGO</span></a>
  <ul class="nav-links">
    <li><a href="#services">Послуги</a></li>
    <li><a href="#masters">Майстри</a></li>
    <li><a href="#reviews">Відгуки</a></li>
    <li><a href="#booking">Запис онлайн</a></li>
    <li><a href="#contact">Контакти</a></li>
  </ul>
  <div class="nav-actions">
    <a href="#booking" class="nav-cta">📅 Записатися онлайн</a>
    <a href="tel:+380441234567" class="nav-phone">📞 +38 (044) 123-45-67</a>
  </div>
</nav>
```
5 center links + 2 action buttons (gold CTA + ghost phone). Logo in gold with text-shadow for visibility on dark bg.

**Master Photos** — `<img>` with fallback:
```html
<div class="master-photo">
  <img src="https://via.placeholder.com/300x300/1a1a1a/C9A96E?text=Olena" 
       alt="Олена Ковальчук" 
       onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
  <span class="placeholder">👩‍🦰</span>
</div>
```
Placeholder images load fast, emoji fallback if blocked.

**Phone Links** — Full number in href (not masked):
```html
<a href="tel:+380441234567">+38 (044) 123-45-67</a>
```
Masked display (`+380****4567`) breaks click-to-call on mobile.

**Privacy Scan** — Required before deploy:
```bash
python scripts/approval_policies.py docs/portfolio/beauty-salon/
# Must return: ✅ CLEAN — 0 violations
```

### Deployment
- GitHub Pages builds take 30-60s after push. Poll `gh api repos/USER/REPO/pages` until `status: built`.
- Custom domains possible later (`CNAME` file), but free `USER.github.io/REPO/` works for demos.

### Lead Gen
- Businesses with **only Instagram/VK** (no website) are highest intent — they already invest in social but miss search traffic.
- "Без предоплаты" + "сделаю демо бесплатно" removes friction.
- Portfolio of 4+ live demos builds credibility instantly.

---

## Related Skills

- `web-development:anti-slop-design` — **LOAD FIRST** for color/typography/copy rules
- `web-development:demo-site-builder` — studio-quality patterns, Impeccable workflow
- `creative:arbitrage-mindmap` — visualize funnel: lead → demo → outreach → close
- `autonomous-ai-agents:arbitrage-execution` — if scaling to automated outreach

---

## Files

- `references/people-first-structure-for-service-businesses.md` — people-first content model (beauty/wellness)
- `references/outreach-template.md` — full DM script + lead sourcing checklist
- `templates/business.html` — base template (update with anti-slop tokens)
- `scripts/generate.py` — wrapper for batch generation from CSV of leads
- `scripts/verify_deploy.py` — poll Pages build status + verify live URL