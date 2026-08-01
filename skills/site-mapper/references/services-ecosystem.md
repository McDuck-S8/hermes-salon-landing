# Services Ecosystem Registry

## JSON Database
`data/services_registry.json` — полная база сервисов:
- AI-генерация (изображения, видео, голос, музыка)
- Хостинг и деплой (GitHub Pages, Netlify, Vercel, Cloudflare Pages)
- Домены (Freenom, NIC.UA, Cloudflare Registrar)
- Фриланс (FL.ru, Kwork, Upwork, Fiverr, Telegram)
- Накрутка соцсетей (Smos, JustAnotherPanel, TelegramBooster)
- CPA-сети (CPAGrip, Adverline, Monetizer, OGAds)
- Платёжные системы (BestChange, Telega.io, KuCoin)

## Граф связей
`reports/services_ecosystem.html` — визуальная карта:
Идея → AI → Контент → Хостинг → Домен → Продвижение → Деньги

## Как использовать
- Добавлять новые сервисы в JSON (id, name, url, category, free, login, vpn, proxy, mapped)
- Cloudflare-сайты помечать blocked_by_cf: true
