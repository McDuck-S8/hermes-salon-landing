---
name: salon-lumiere-builder
description: Build a beauty salon landing page from template. Includes: hero with user-perspective copy, services with prices, master cards with photos, reviews, booking form, contact section. Deploys to GitHub Pages at docs/portfolio/{slug}/index.html.
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
├── index.html              # Main landing page
├── assets/
│   ├── logo.png            # 800x800 brand logo
│   ├── og-image.jpg        # 1200x630 social preview
│   └── masters/            # Master photos (300x300)
│       ├── master-1.jpg
│       ├── master-2.jpg
│       ├── master-3.jpg
│       └── master-4.jpg
├── robots.txt              # SEO
├── sitemap.xml             # SEO
└── README.md               # Documentation
```

## Build Steps

### 1. Input Parameters (required)

```python
params = {
    "slug": "beauty-salon",           # URL slug: docs/portfolio/beauty-salon/
    "salon_name": "Fargo",            # Brand name
    "location": "Позняки, Київ",      # Area, city
    "address": "вул. Григоренка, 12", # Full address
    "phone": "+380441234567",         # Phone for tel: links
    "telegram": "@fargo_salon",       # Telegram username
    "hours": "10:00–20:00 щодня",     # Working hours
    "services": [                     # 6 services max
        {"name": "Стрижки та укладка", "icon": "✂️", "desc": "Жіночі, чоловічі, дитячі...", "price": "350"},
        {"name": "Колористика", "icon": "🎨", "desc": "Повне фарбування, мелірування...", "price": "800"},
        {"name": "Манікюр та педикюр", "icon": "💅", "desc": "Апаратний, класичний...", "price": "400"},
        {"name": "Масаж та догляд", "icon": "💆", "desc": "Розслабляючий, лікувальний...", "price": "500"},
        {"name": "Вії та брови", "icon": "👁️", "desc": "Ламінування вій, брау-ламінування...", "price": "350"},
        {"name": "Кератин та ботокс", "icon": "🤍", "desc": "Кератинове випрямлення...", "price": "1200"}
    ],
    "masters": [                      # 4 masters max
        {"name": "Олена Ковальчук", "spec": "Топ-колорист • 8 років", "bio": "Спеціалізується на складному фарбуванні...", "photo": "master-1.jpg"},
        {"name": "Андрій Шевченко", "spec": "Художник-перукар • 6 років", "bio": "Майстер жіночих та чоловічих стрижок...", "photo": "master-2.jpg"},
        {"name": "Марія Петренко", "spec": "Майстер манікюру/педикюру • 5 років", "bio": "Апаратний манікюр без поранень...", "photo": "master-3.jpg"},
        {"name": "Анна Бондар", "spec": "Лешмейкер / Бровіст • 4 роки", "bio": "Ламінування вій, брау-ламінування...", "photo": "master-4.jpg"}
    ],
    "reviews": [                      # 3 reviews
        {"author": "Катерина М.", "service": "Колористика", "time": "2 тижні тому", "text": "Довго шукала колориста...", "rating": 5},
        {"author": "Олександр Д.", "service": "Стрижка", "time": "місяць тому", "text": "Андрій — один з найкращих...", "rating": 5},
        {"author": "Юлія С.", "service": "Манікюр + дизайн", "time": "3 дні тому", "text": "Марія робить найкращий...", "rating": 5}
    ],
    "user_perspective": {             # 4 questions (MANDATORY)
        "who": "Жінка 28-45 років, Київ (Позняки), шукає стрижку/колористику/манікюр. Має роботу, обмежений час, хоче бачити портфоліо майстра ДО візиту.",
        "five_sec": "Fargo — салон на Позняках. Чесні ціни на сайті, портфоліо майстрів, запис онлайн за 30 сек. Без дзвінків.",
        "action": "Натисне 'Записатися онлайн' (золота кнопка в герої) → вибере послугу → дату → час → відправить форму.",
        "why": "Устала від сюрпризів у чеку. Хоче бачити роботу Олени (колорист) перед візитом, знати ціну наперед, записатися без дзвінків адміністратору."
    }
}
```

### 2. Template Engine

The skill uses a Jinja2-like template in `template.html` with these variables:
- `{{salon_name}}`, `{{location}}`, `{{address}}`, `{{phone}}`, `{{telegram}}`, `{{hours}}`
- `{{services}}` — array of service objects
- `{{masters}}` — array of master objects
- `{{reviews}}` — array of review objects
- `{{user_perspective}}` — dict with 4 questions
- `{{hero_badge}}` — location badge text
- `{{hero_headline}}` — main H1
- `{{hero_sub}}` — hero subtext
- `{{hero_cta_primary}}` — primary CTA text
- `{{hero_cta_secondary}}` — secondary CTA text
- `{{trust_items}}` — array of trust badges

### 3. CSS Architecture

Single-file HTML with embedded CSS using CSS custom properties:

```css
:root {
  --gold: #C9A96E;
  --gold-dark: #A8884A;
  --bg: #0A0A0A;
  --bg2: #111111;
  --bg3: #1A1A1A;
  --text: #F0EDE8;
  --text-muted: #8A8680;
  --glass: rgba(255,255,255,0.03);
  --glass-border: rgba(255,255,255,0.06);
  --radius: 20px;
}
```

Key components:
- **Preloader** — inline script dismisses immediately on `readyState === 'complete'`
- **Nav** — solid dark background from load, `backdrop-filter: blur(20px)`, scrolled state darkens
- **Hero** — `padding-top: 160px` to clear fixed nav, centered content, dual CTA row
- **Services** — CSS Grid `repeat(auto-fit, minmax(280px, 1fr))`, cards with hover lift
- **Masters** — Grid with photo area (`aspect-ratio: 1`), `<img>` + fallback emoji placeholder
- **Reviews** — Cards with stars, avatar initials, meta line
- **Booking** — Form with selects (service, master), date/time inputs, name/phone
- **Contact** — Two-column grid, info cards + contact form
- **Responsive** — Mobile-first, nav links hidden on <768px, hamburger not implemented (keep simple)

### 4. Master Photo Handling

```html
<div class="master-photo">
  <img src="assets/masters/{{master.photo}}" alt="{{master.name}}" 
       onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
  <span class="placeholder">{{master.icon}}</span>
</div>
```

CSS:
```css
.master-photo { aspect-ratio: 1; overflow: hidden; background: linear-gradient(...); }
.master-photo img { width: 100%; height: 100%; object-fit: cover; }
.master-photo .placeholder { display: none; font-size: 3rem; color: var(--gold)44; }
```

### 5. Preloader Dismissal (CRITICAL)

```html
<div id="preloader"><div class="preloader-glow"></div></div>
<script>
  const p = document.getElementById('preloader');
  if (p) p.classList.add('loaded');
</script>
```

Inline script AFTER preloader element, BEFORE nav. No flash.

### 6. Deployment

```bash
# 1. Build output to docs/portfolio/{slug}/
mkdir -p docs/portfolio/beauty-salon/
cp index.html docs/portfolio/beauty-salon/

# 2. Privacy scan
python scripts/approval_policies.py docs/portfolio/beauty-salon/

# 3. Git commit + push
git add docs/portfolio/beauty-salon/
git commit -m "Deploy beauty salon landing to docs/portfolio/beauty-salon/"
git push origin <branch>

# 4. Live URL: https://{user}.github.io/{repo}/portfolio/beauty-salon/
```

### 7. Quality Gates (run before deploy)

```bash
# Privacy scan
python scripts/approval_policies.py docs/portfolio/{slug}/

# HTML structure check
python -c "
from bs4 import BeautifulSoup
soup = BeautifulSoup(open('docs/portfolio/{slug}/index.html'), 'html.parser')
assert soup.find('h1')
assert soup.find('form', id='booking-form')
assert soup.select('.master-photo img')
assert soup.find(id='preloader')
print('✅ Structure OK')
"

# User-perspective validation
python -c "
params = {...}  # from step 1
required = ['who', 'five_sec', 'action', 'why']
for q in required:
    assert params['user_perspective'][q], f'Missing user_perspective.{q}'
print('✅ User-perspective OK')
"
```

## Usage Example

```python
# In agent code or script
from skills.web_development.salon_lumiere_builder import build_salon_landing

params = {
    "slug": "fargo-kyiv-pozniaky",
    "salon_name": "Fargo",
    "location": "Позняки, Київ",
    "address": "вул. Григоренка, 12",
    "phone": "+380441234567",
    "telegram": "@fargo_salon",
    "hours": "10:00–20:00 щодня",
    "services": [...],
    "masters": [...],
    "reviews": [...],
    "user_perspective": {...}
}

result = build_salon_landing(params)
# Returns: {"html_path": "docs/portfolio/fargo-kyiv-pozniaky/index.html", "live_url": "..."}
```

## References

- `references/beauty-salon-landing-fixes-2026-07-18.md` — Logo visibility, hero padding, nav structure, master photos
- `references/salon-landing-fix-2026-07-18.md` — Complete fix log for Fargo landing
- `references/social-preview-fixes.md` — OG image, branded text card, Telegram cache
- `references/salon-pexels-booking-pattern-2026-07-10.md` — Booking form UX patterns
- `references/salon-lumiere-fix-2026-07-02.md` — Earlier salon project fixes

---

**Remember:** Every landing must pass the 4-question user-perspective check before generation. No generic templates — each salon has real clients with specific needs.