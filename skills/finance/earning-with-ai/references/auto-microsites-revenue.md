# Auto Microsites — Revenue Generator

## What It Is
JSON → HTML landing page generator for local businesses. 30 seconds to generate, free hosting on GitHub Pages.

## Location
`D:/Portable_Soft/hermes/projects/auto-microsites/`

## How To Use

### Generate a site
```bash
cd D:/Portable_Soft/hermes/projects/auto-microsites
python main.py --from samples/barbershop.json
```

### JSON config format
```json
{
    "project_name": "my-business",
    "business_name": "Название",
    "tagline": "Слоган",
    "phone": "+7 (978) 123-45-67",
    "address": "г. Симферополь, ул. Примерная, 1",
    "working_hours": "Пн-Вс: 09:00-21:00",
    "color_primary": "#2563eb",
    "color_accent": "#f59e0b",
    "cta_text": "Позвонить",
    "about": "Описание бизнеса...",
    "services": [
        {"name": "Услуга", "price": "от 1 000 ₽", "description": "Описание"}
    ],
    "seo_title": "Название — Симферополь",
    "seo_description": "Краткое описание для поисковика"
}
```

### Deploy to GitHub Pages (free)
```bash
python deploy.py barbershop-akcent
# Result: https://user.github.io/barbershop-akcent-site/
```

## Template Features
- Gradient hero section with animated background
- Service cards grid (responsive, auto-fill)
- Sticky "Call" button (floating CTA)
- Scroll animations (IntersectionObserver)
- SEO meta tags (title, description)
- Mobile-first design
- CSS variables for easy color customization

## Sales Pipeline
1. Find business without site (Yandex Maps, 2GIS)
2. Generate demo site from their info (30 sec)
3. Send demo link to owner via Telegram/WhatsApp
4. Sell for 7K-25K rubles (see site-for-biz/PACKAGES.md)

## Target Niches (Simferopol)
| Niche | Client avg ticket | Willingness to pay |
|-------|------------------|-------------------|
| Dental | 5K-50K₽ | High |
| Barbershop | 800-2K₽ | Medium |
| Auto service | 3K-30K₽ | High |
| Restaurant | 1K-3K₽ | Medium |
| Lawyer/accountant | 5K-20K₽ | High |

## Samples
- `samples/barbershop.json` — Барбершоп АКЦЕНТ
- `samples/dental.json` — Стоматология Smile

## Outreach Template
See `OUTREACH.md` in the same project directory.
