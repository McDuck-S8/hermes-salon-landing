# Session 2026-07-25: CPA Funnel Build — Key Artifacts

## Created Files

| File | Purpose | Location |
|------|---------|----------|
| `cpa_telegram_bot.py` | aiogram 3.x bot with FSM, lead magnet delivery, drip campaign, offer display | `scripts/` |
| `n8n_telegram_cpa_funnel.json` | Complete n8n workflow: webhook → welcome → lead magnet → offers → drip sequence | `scripts/` |
| `lead_magnet.md` | "Smart Home in One Evening" checklist — 7 ESPHome schemes, shopping list, ESPHome config, next steps | `scripts/` |
| `requirements_cpa_bot.txt` | Python deps: aiogram, aiohttp, python-dotenv | `scripts/` |

## Key Patterns Implemented

### 1. FSM State Machine (aiogram 3.x)
```python
class LeadState(StatesGroup):
    waiting_start = State()
    got_lead_magnet = State()
    in_sequence = State()
```

### 2. Built-in Drip Campaign (no external scheduler needed)
```python
SEQUENCE = [
    {"delay_h": 2, "text": "Tip: start with ESP8266 + DHT22..."},
    {"delay_h": 24, "text": "Case study: how I made $XXX on smart plugs..."},
    {"delay_h": 48, "text": "Hot offer: Smart plugs — $3/lead..."},
    {"delay_h": 72, "text": "Advanced: Node-RED automations..."},
]
```
Background task checks every 5 min and sends next message when delay elapsed.

### 3. n8n Workflow Structure
```
Telegram Webhook
    → Parse Message (Function)
    → Is Start Command? (IF)
        → Save New User (Function)
        → Send Welcome + Lead Magnet Offer (Telegram)
    → Wants Lead Magnet? (IF)
        → Send Lead Magnet PDF (Telegram)
        → Update State: Got Lead Magnet (Function)
    → Wants Offers? (IF)
        → Send CPA Offers (Telegram)
    → Wants n8n Info? (IF)
        → Send n8n Automation Info (Telegram)
    → Back to Menu? (IF)
        → Send Main Menu (Telegram)
```

### 4. Lead Magnet Content Structure
- **Hook**: "7 schemes, $50 parts, 1 evening"
- **Shopping list**: AliExpress/ChipDip links with prices
- **7 schemes**: Climate, Auto-light, Smart socket, Leak detector, CO2/ventilation, Smart blinds, Security
- **ESPHome configs**: Ready-to-flash YAML for each
- **Next steps**: HA integration, Telegram notifications, monetization via CPA

## CPA Offers Mapped to Smart Home Niche

| Offer | Network | Payout | GEO | Fit |
|-------|---------|--------|-----|-----|
| Smart plugs (Tuya/Sonoff clones) | MyLead | $2-5 | RU/UA/KZ/BY/EU | Perfect — direct hardware upsell |
| Zigbee sensors (Aqara/Xiaomi) | Admitad | $3-8 | RU/EU | High ticket, good for "advanced" sequence |
| DIY smart home kits | KMA.biz | $5-15 | CIS | Bundle upsell after trust built |
| Home Assistant Cloud / Nabu Casa | Admitad | $10-20 | Global | Recurring, high LTV |
| VPN for IoT security | MyLead | $2-4 | RU/Global | Cross-sell in security sequence |

## Deployment Checklist

- [ ] Add `BOT_TOKEN` to `.env`
- [ ] Add `ADMIN_ID` to `.env`
- [ ] Create `lead_magnet.pdf` from `lead_magnet.md` (pandoc/weasyprint/fpdf2)
- [ ] Run `pip install -r requirements_cpa_bot.txt`
- [ ] Test locally: `python scripts/cpa_telegram_bot.py`
- [ ] Import `n8n_telegram_cpa_funnel.json` into n8n
- [ ] Configure n8n Telegram credentials + webhook URL
- [ ] Set up n8n cron for drip sequence (or use bot's built-in)
- [ ] Deploy bot to Fly.io / VPS with systemd
- [ ] Add CPA network API keys to bot config

## Lessons Learned

1. **Bot's built-in sequence > external scheduler** for simple funnels — fewer moving parts
2. **n8n workflow** is better when you need: webhooks from CPA networks, complex branching, multi-channel (email + Telegram), visual debugging
3. **Lead magnet must be immediately actionable** — "7 schemes you can build tonight" beats "ultimate guide to smart home"
4. **Map each CPA offer to a funnel stage** — don't dump all offers at once
5. **SubID tracking essential** — use `{user_id}_{offer_id}_{timestamp}` format for postback attribution

## Next Steps for Production

1. Add PostgreSQL + Redis for multi-instance scaling
2. Implement click tracking redirector (short domain → log click → 302 to offer)
3. Add postback endpoints per CPA network (`/postback/mylead`, `/postback/admitad`)
4. Build admin panel: user stats, offer management, broadcast
5. A/B test lead magnet titles: "Checklist" vs "7 Schemes" vs "Free PDF"