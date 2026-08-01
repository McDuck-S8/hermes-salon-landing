---
name: cpa-telegram-bot-generator
description: Use when creating Telegram bots for CPA traffic — 3 templates (cpa_offers, content_locker, vpn_promo), /start → offer button, /offer command, admin stats, requirements.txt, .env.example
---

# CPA Telegram Bot Generator

Generates ready-to-deploy Telegram bots for CPA traffic arbitrage. Each bot receives traffic, presents offer, tracks clicks.

## When to Use

- Need bot to bridge social media traffic → CPA landing page
- Content locking flow: user completes offer → gets unlock code
- Promo bot for specific vertical (VPN, gaming, finance)
- Zero-code deployment: just add bot token and offer URL

## Templates (3)

| Template | Use Case | Start Message | Offer Button |
|----------|----------|---------------|--------------|
| `cpa_offers` | General CPA offers | "Welcome! Click below to claim your offer." | 🚀 GET OFFER |
| `content_locker` | Content locking (V-Bucks, Robux) | "🔓 Unlock exclusive content — free V-Bucks, Robux!" | 🔓 UNLOCK NOW |
| `vpn_promo` | VPN affiliate promo | "🔒 Protect your privacy. Get 60% OFF + 3 months free!" | 🔥 CLAIM DISCOUNT |

## Generated Structure

```
projects/cpa-bot-{template}/
├── bot.py              # Main bot (aiogram 3.x)
├── requirements.txt    # python-telegram-bot>=21.0
├── .env.example        # CPA_BOT_TOKEN, CPA_OFFER_URL
└── README.md           # Deploy instructions
```

## Usage

```bash
# List templates
python scripts/cpa_bot_generator.py list

# Generate single bot
python scripts/cpa_bot_generator.py generate content_locker

# Generate all 3
python scripts/cpa_bot_generator.py batch

# Deploy
cd projects/cpa-bot-content_locker
cp .env.example .env
# Edit .env: CPA_BOT_TOKEN=xxx, CPA_OFFER_URL=https://...
pip install -r requirements.txt
python bot.py
```

## Bot Features

- **`/start`** — Welcome message with inline offer button (links to CPA landing)
- **`/offer`** — Re-sends offer details with button
- **`/stats`** — Admin only: shows bot uptime, user count (placeholder)
- **Inline keyboard** — Single button, URL from `CPA_OFFER_URL` env var
- **Error handling** — Graceful startup, logging
- **No database** — Stateless, scalable

## Configuration (.env)

```env
CPA_BOT_TOKEN=your_token_from_@BotFather
CPA_OFFER_URL=https://mcduck-s8.github.io/hermes-salon-landing/cpa/gaming/
ADMIN_IDS=123456789,987654321  # comma-separated Telegram user IDs
```

## Integration

- **Upstream:** `cpa-income-pipeline`, `cpa-landing-generator` (matching niche)
- **Downstream:** `cpa-video-script-generator` (video CTA → "Link in bio" → bot username)
- **Tracking:** UTM in offer URL → `utm_source=telegram_bot&utm_medium=bot&utm_campaign=content_locking&utm_content={niche}_{variant}`

## Deployment Options

| Platform | Cost | Setup |
|----------|------|-------|
| VPS (Ubuntu) | $4-6/mo | systemd service, nginx reverse proxy optional |
| Railway | $5/mo | `railway up`, auto-deploy from GitHub |
| Render | Free tier | Web service, auto-deploy |
| Fly.io | Free tier | `fly launch`, `fly deploy` |

## Customization

Edit `BOT_TEMPLATES` in `scripts/cpa_bot_generator.py`:
- `start_msg`: welcome text
- `offer_text`: offer details text
- `offer_button`: button label
- `fallback_text`: when offer expired
- `admin_ids`: list of admin user IDs (int)

## Bot Flow

```
User clicks video bio link / searches bot username
        ↓
/start command → welcome + offer button
        ↓
User taps button → opens CPA landing (GitHub Pages)
        ↓
User completes offer → CPA network tracks conversion
        ↓
(Optional) Bot sends unlock code via webhook from CPA network
```