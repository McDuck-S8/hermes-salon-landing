# Simferopol Auto-Microsites Session — 2026-07-14

## Context
Tested the **auto-microsites** method (from `projects/auto-microsites/`) for Simferopol/Crimea market with $0 budget. Different from Kyiv web-studio-ops pipeline — uses JSON→HTML template + GitHub Pages deploy.

## Method: Auto-Microsites Project

### Structure
```
projects/auto-microsites/
├── main.py              # JSON → HTML generator (Tailwind, animations, SEO, floating CTA)
├── deploy.py            # GitHub Pages deploy via gh CLI
├── templates/business.html  # Modern template (glassmorphism, scroll animations)
├── samples/             # JSON configs for businesses
├── generated/           # Output sites
└── deploy/              # Git repos for GitHub Pages
```

### Generation Flow
```bash
# 1. Create JSON config for business
# 2. Generate HTML
python main.py --from samples/barin.json
# 3. Deploy to GitHub Pages (free)
python deploy.py barin-barbershop --repo barin-barbershop-site
# Result: https://mcduck-s8.github.io/barin-barbershop-site/
```

### Template Features
- Tailwind via CDN (no build step)
- Glassmorphism cards, scroll-reveal animations (IntersectionObserver)
- Floating CTA button (tel: link)
- SEO meta tags + Open Graph
- Mobile-first responsive
- Color customization via CSS variables (--primary, --accent)
- Russian language

## Simferopol Leads Found (No Website / Only Social)

| Business | Type | Contact | Site Status | Demo Status |
|----------|------|---------|-------------|-------------|
| **BroBarber** | Барбершоп (3 локации) | @brobarber_simf_01, +7 (978) 048-53-35 | Only Instagram | ✅ Deployed |
| **Edward Barbershop** | Барбершоп (ул. Чехова, 13) | +7 (978) 722-13-13 | Yandex Maps + Instagram | ✅ Generated |
| **МАРИ-ДЕНТ** | Стоматология (ул. Александра Невского, 7) | +7 (978) 123-45-67 | Has site (mari-dent.ru) | ✅ Generated (portfolio) |
| **БАРИНЪ** | Барбершоп (ул. Карла Маркса, 51) | +7 (978) 116-56-95 | Has site (b-barin.ru) | ✅ Deployed (portfolio) |

## Key Differences from Kyiv Pipeline

| Aspect | Kyiv (web-studio-ops) | Simferopol (auto-microsites) |
|--------|----------------------|------------------------------|
| **Generator** | `scripts/demo_generator.py` (3 templates) | `main.py` (1 universal template) |
| **Deploy** | Manual to `docs/{client}/` | `deploy.py` → GitHub Pages repos |
| **Templates** | Category-specific (salon/medical/cafe) | Universal business template |
| **OG Images** | Studio-branded preview.jpg | Uses template defaults |
| **Location** | Kyiv | Simferopol / Crimea |
| **Language** | RU/UA/EN | Russian only |

## Outreach Adaptation for Crimea

From `OUTREACH.md`:
- Target niches: Стоматология (high), Барбершоп (medium), Автосервис (high), Юрист (high), Фитнес (medium)
- Channels: Яндекс.Карты → Telegram/WhatsApp from card, 2ГИС, Instagram DM, Авито
- Pricing: 7,000–25,000₽ (vs $300-400 in Kyiv)
- Payment: USDT TRC20 → KuCoin/OKX P2P → Т-Банк (Binance/Bybit blocked in Crimea)

## Scripts Created This Session
- `samples/barin.json` — БАРИНЪ барбершоп config
- `samples/brobarber.json` — BroBarber (Instagram-only lead) config
- `samples/edward.json` — Edward Barbershop config
- `samples/mari-dent.json` — МАРИ-ДЕНТ стоматология config

## Next Actions for Revenue Test
1. Deploy Edward + Mari-Dent demos (2 more live portfolio links)
2. Scrape 10+ Simferopol leads without sites (Yandex Maps API or manual)
3. Generate personalized demos for each (30 sec each)
4. Send outreach via Telegram/WhatsApp/Instagram using adapted template
5. Track responses → first paid contract = test passed

## Pitfalls / Notes
- **GitHub Pages build time** — 30-60 seconds after push, check `gh api repos/{user}/{repo}/pages` for status
- **Deploy script requires gh CLI auth** — `gh auth status` must show logged in
- **Simferopol businesses often only on Instagram/VK** — need to extract phone from bio or Yandex Maps
- **Crimea payment constraints** — USDT TRC20 → KuCoin P2P is the working rail
- **Template is universal** — no category-specific variants yet; could add salon/medical/auto variants later