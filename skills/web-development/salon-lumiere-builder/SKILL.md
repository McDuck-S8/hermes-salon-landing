---
name: salon-lumiere-builder
description: "Build a beauty salon landing page from template. Includes: hero with user-perspective copy, services with prices, master cards with photos, reviews, booking form, contact section. Deploys to GitHub Pages at docs/portfolio/{slug}/index.html."
trigger: when user asks to build a salon/beauty landing page
usage: salon-lumiere-builder
tags: [web-development, landing-page, beauty-salon, template]
---

# Salon Lumiere Builder

Complete beauty salon web project generator. Creates production-ready landing pages with:
- User-perspective hero (4 questions answered)
- Services grid with prices
- Master cards with photo placeholders
- Reviews section
- Booking form (service, master, date, time, name, phone)
- Contact info + map link
- SEO meta tags
- Privacy-compliant (no PII leaks)

## Project Structure

```
salon-{slug}/
├── index.html
├── assets/
│   ├── logo.png
│   ├── og-image.jpg
│   └── masters/
│       ├── master-1.jpg
│       ├── master-2.jpg
│       ├── master-3.jpg
│       └── master-4.jpg
├── robots.txt
├── sitemap.xml
└── README.md
```

## Build Steps

### 1. Input Parameters

```python
params = {
    "slug": "beauty-salon",
    "salon_name": "Fargo",
    "location": "Позняки, Київ",
    "address": "вул. Григоренка, 12",
    "phone": "+380441234567",
    "telegram": "@fargo_salon",
    "hours": "10:00–20:00 щодня",
    "services": [
        {"name": "Стрижки та укладка", "icon": "✂️", "desc": "Жіночі, чоловічі, дитячі...", "price": "350"},
        {"name": "Колористика", "icon": "🎨", "desc": "Повне фарбування, мелірування...", "price": "800"},
        {"name": "Манікюр та педикюр", "icon": "💅", "desc": "Апаратний, класичний...", "price": "400"},
        {"name": "Масаж та догляд", "icon": "💆", "desc": "Розслабляючий, лікувальний...", "price": "500"},
        {"name": "Вії та брови", "icon": "👁️", "desc": "Ламінування вій, брау-ламінування...", "price": "350"},
        {"name": "Кератин та ботокс", "icon": "🤍", "desc": "Кератинове випрямлення...", "price": "1200"}
    ],
    "masters": [
        {"name": "Олена Ковальчук", "spec": "Топ-колорист • 8 років", "bio": "Спеціалізується на складному фарбуванні...", "photo": "master-1.jpg"},
        {"name": "Андрій Шевченко", "spec": "Художник-перукар • 6 років", "bio": "Майстер жіночих та чоловічих стрижок...", "photo": "master-2.jpg"},
        {"name": "Марія Петренко", "spec": "Майстер манікюру/педикюру • 5 років", "bio": "Апаратний манікюр без поранень...", "photo": "master-3.jpg"},
        {"name": "Анна Бондар", "spec": "Лешмейкер / Бровіст • 4 роки", "bio": "Ламінування вій, брау-ламінування...", "photo": "master-4.jpg"}
    ],
    "reviews": [
        {"author": "Катерина М.", "service": "Колористика", "time": "2 тижні тому", "text": "Довго шукала колориста...", "rating": 5},
        {"author": "Олександр Д.", "service": "Стрижка", "time": "місяць тому", "text": "Андрій — один з найкращих...", "rating": 5},
        {"author": "Юлія С.", "service": "Манікюр + дизайн", "time": "3 дні тому", "text": "Марія робить найкращий...", "rating": 5}
    ],
    "user_perspective": {
        "who": "Жінка 28-45 років, Київ (Позняки), шукає стрижку/колористику/манікюр. Має роботу, обмежений час, хоче бачити портфоліо майстра ДО візиту.",
        "five_sec": "Fargo — салон на Позняках. Чесні ціни на сайті, портфоліо майстрів, запис онлайн за 30 сек. Без дзвінків.",
        "action": "Натисне 'Записатися онлайн' (золота кнопка в герої) → вибере послугу → дату → час → відправить форму.",
        "why": "Устала від сюрпризів у чеку. Хоче бачити роботу Олени (колорист) перед візитом, знати ціну наперед, записатися без дзвінків адміністратору."
    }
}
```

### 2. Template Engine

Variables: `{{salon_name}}`, `{{location}}`, `{{address}}`, `{{phone}}`, `{{telegram}}`, `{{hours}}`, `{{services}}`, `{{masters}}`, `{{reviews}}`, `{{user_perspective}}`, `{{hero_badge}}`, `{{hero_headline}}`, `{{hero_sub}}`, `{{hero_cta_primary}}`, `{{hero_cta_secondary}}`, `{{trust_items}}`.

### 3. CSS Architecture

Single-file HTML with embedded CSS using custom properties. Key components: preloader, nav, hero, services grid, masters, reviews, booking form, contact, responsive mobile-first.

### 4. Master Photo Handling

```html
<div class="master-photo">
  <img src="assets/masters/{{master.photo}}" alt="{{master.name}}"
       onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
  <span class="placeholder">{{master.icon}}</span>
</div>
```

### 5. Preloader Dismissal (CRITICAL)

```html
<div id="preloader"><div class="preloader-glow"></div></div>
<script>
  const p = document.getElementById('preloader');
  if (p) p.classList.add('loaded');
</script>
```

### 6. Deployment

```bash
mkdir -p docs/portfolio/beauty-salon/
cp index.html docs/portfolio/beauty-salon/
python scripts/approval_policies.py docs/portfolio/beauty-salon/
git add docs/portfolio/beauty-salon/
git commit -m "Deploy site"
git push origin <branch>
```

Variant with gh-pages worktree (this repo):
```bash
cp index.html /d/gh-pages-deploy/cosmetologist/
cp -r assets/* /d/gh-pages-deploy/cosmetologist/assets/
cd /d/gh-pages-deploy
ALL_PROXY=socks5://127.0.0.1:10806 git add cosmetologist/ && git commit -m "update" && git push origin gh-pages
```

### 7. Quality Gates

```bash
python scripts/approval_policies.py docs/portfolio/{slug}/
python scripts/design_critic.py "path/to/index.html" | python -c "import sys,json; d=json.load(sys.stdin); print(f'{d[\"overall_score\"]}/100')"
```

### ⚠️ CRITICAL: JS-Preservation Guard (before deployment)

When rewriting index.html with `write_file`, ALL existing JS functionality must be preserved. The most common failure: `onclick` handlers in HTML that reference undefined functions.

**Guard checklist before any full-file rewrite:**
1. Scan the **old** file for `onclick="..."` references and list every function name
2. Scan the **new** file's `<script>` section for each function
3. If any are missing → ADD them to the new script section before writing
4. Also check: `window['functionName']` assignments, `addEventListener` calls, DOM element IDs referenced in JS

**Failure mode (observed 2026-07-29):** Full rewrite dropped `initCarousel()`, `moveSlide()`, `goToSlide()` — carousel buttons rendered useless. User found the bug, not the agent. Fix cost: 2 extra commits + user frustration.

**Remedy:** After EVERY write_file of index.html, run this check before reporting done:
```bash
grep -oP 'onclick="\K[^"]+' index.html | sort -u > /tmp/needed_funcs.txt
grep -oP '(function \w+|window\[\x27\K[^\x27]+)' index.html | sort -u > /tmp/defined_funcs.txt
# Compare — every needed func must be defined
```

## Container Queries

```css
.services-grid, .ba-grid { container-type: inline-size; }
@container (max-width: 500px) {
  .services-grid, .ba-grid { grid-template-columns: 1fr; }
}
```

## Design Critic 100/100

The critic checks 11 features. All must be present for perfect score:

1. Glassmorphism (`backdrop-filter`)
2. Dark mode (`@media prefers-color-scheme: dark`)
3. Micro-animations (`transition`/`animation`)
4. Fluid typography (`clamp()`)
5. Container queries (`container-type`)
6. CSS Grid
7. Flexbox
8. Semantic HTML (>=3 tags)
9. ARIA (`aria-`)
10. Viewport meta
11. Meta description

If missing any, max 76/100. See `references/design-critic-100-checklist.md`.

## Dark Mode Pitfalls

See `references/dark-mode-css-pitfalls-2026-07-29.md` for:
- ONE :root + ONE @media (no duplicate blocks)
- Hardcoded light colors need explicit dark overrides
- Button text: use `#fff` hardcoded, not `var(--white)`

## Usage Example

```python
from skills.web_development.salon_lumiere_builder import build_salon_landing
result = build_salon_landing(params)
```

## References

- `references/beauty-salon-landing-fixes-2026-07-18.md`
- `references/salon-landing-fix-2026-07-18.md`
- `references/social-preview-fixes.md`
- `references/dark-mode-css-pitfalls-2026-07-29.md`
- `references/design-critic-100-checklist.md`
- `references/deploy-privacy-protocol.md`
- `references/js-preservation-guard-2026-07-29.md`

---

**Remember:** Every landing must pass the 4-question user-perspective check. No generic templates.
