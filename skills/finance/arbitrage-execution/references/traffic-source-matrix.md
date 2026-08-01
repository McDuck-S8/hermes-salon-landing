# Traffic Source Matrix — Полная карта источников трафика

**Дата:** 2026-07-21
**Версия:** 1.0
**Источники:** ARBITRAGE_BONDS.md (50 схем), Voluum, Adsterra, ClickBank, GitHub Topics, BlackHatWorld, исследования

---

## Как пользоваться этой матрицей

1. **Выбери источник трафика** — по бюджету ($0 или paid), по geo, по типу оффера
2. **Найди инструменты** — GitHub-репозитории для автоматизации этого источника
3. **Оцени интеграцию** — что из этого можно подключить к Hermes (ghost-surfer, posting.py, cron, terminal)
4. **Оцени потенциал** — CPA payout, конверсия, сложность, риск бана

---

## 1. TIKTOK — Видео-контент (Short-form)

| Характеристика | Значение |
|---|---|
| Тип | Organic / Paid |
| Бюджет | $0 (organic), $100+ (ads) |
| Формат | Shorts 15-60s, прямая ссылка в bio |
| Цель | CPA (Content Locking, Mobile CPI, SmartLink) |
| Geo | Any, best US/UK/IN |

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция | Потенциал |
|------------|------|------|-----------|-----------|
| **chunhuduc/tiktok-multi-account-management-geelark** | Python, Geelark, ffmpeg | 50-100 аккаунтов, облачные телефоны | ⭐⭐⭐ — Python, тот же стек | Высокий |
| **l-portet/tiktok-warmup-bot** (663⭐) | Node.js, iOS Voice Control | Безопасный прогрев | ⭐⭐ — через cron + SSH | Средний |
| **Hormold/tiktok-warmup** (53⭐) | TypeScript, ADB | Android-прогрев, ADB | ⭐⭐⭐ — ADB через terminal | Средний |
| **jiajasper/ttwarmup** (7⭐) | Python, PyAutoGUI | Запись/воспроизведение мыши | ⭐⭐⭐ — чистый Python | Низкий |
| **terafear/TikTok-Automation-Bot** | Python, Selenium, Zefoy | Накрутка лайков/просмотров | ⭐⭐ — Selenium | Средний |
| **sudoguy/tiktokpy** | Python | Фреймворк взаимодействий | ⭐⭐⭐ — Python API | Средний |
| **Our ghost-surfer posting.py** | Python, Playwright | TikTokPoster (базовый) | ✅ **УЖЕ ЕСТЬ** | Высокий |

### Наш стек
✅ **ghost-surfer** (TikTokPoster) — posting.py:122-204
✅ **tiktok-account-farm** — создан навык
⬜ Нужна доработка: anti-detect, CAPTCHA, session persistence, multi-account queue

---

## 2. YOUTUBE — Видео-контент (Long-form + Shorts)

| Характеристика | Значение |
|---|---|
| Тип | Organic / Paid |
| Бюджет | $0 (organic), $50+ (YouTube Ads) |
| Формат | Shorts, Long-form видео, описания |
| Цель | CPA (Content Locking, SmartLink, Nutra) |
| Geo | Any |

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция | Потенциал |
|------------|------|------|-----------|-----------|
| **yt-dlp/yt-dlp** (100k⭐) | Python | Скачивание видео | ✅ Уже используется | Высокий |
| **Our content-pipeline** | Python, ffmpeg | Генерация/редактирование | ✅ Уже есть | Высокий |
| **Omar-Ahmed-Yahia/YouTube-Short-Downloader** | Python | Даунлоадер Shorts | ⭐⭐⭐ | Средний |
| **pytube/pytube** (12k⭐) | Python | YouTube API обёртка | ⭐⭐⭐ | Низкий |
| **youtube-transcript** | Python | Получение транскриптов | ✅ Уже есть (youtube-research) | Средний |

### Наш стек
✅ **content-pipeline** — генерация/редактирование видео
✅ **cpa-video-pipeline** — сценарии и монтаж
✅ **youtube-research** — анализ транскриптов
⬜ Нужен: YouTubeUploader для автоматической загрузки Shorts

---

## 3. TELEGRAM — Мессенджер

| Характеристика | Значение |
|---|---|
| Тип | Organic |
| Бюджет | $0 |
| Формат | Каналы, чаты, Mini Apps, боты |
| Цель | CPA (Content Locking, SmartLink, Nutra, Pay-Per-Call) |
| Geo | RU, UA, IN, ID, BR |

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция | Потенциал |
|------------|------|------|-----------|-----------|
| **Our telegram-channel-poster** | Python | Постинг в каналы | ✅ **УЖЕ ЕСТЬ** | Высокий |
| **Our telegram-digest** | Python | Сбор с каналов | ✅ **УЖЕ ЕСТЬ** | Средний |
| **Our cpa-telegram-bot-generator** | Python | Генерация ботов | ✅ **УЖЕ ЕСТЬ** | Высокий |
| **Our TG-MiniApp-CPA** | HTML/JS | Mini App для CPA | ✅ В плане деплоя | Высокий |
| **RohithBoppey/telegram-bot** | Python | Автоматизация чатов | ⭐⭐⭐ | Средний |
| **TelegramOrg/telegram-api** | TDLib | Нативный API Telegram | ⭐⭐⭐ | Высокий |

### Наш стек
✅ **telegram-channel-poster** — готовый постинг
✅ **cpa-telegram-bot-generator** — 3 шаблона ботов
✅ **TG-MiniApp-CPA** — Mini App для CPA лидогенерации
✅ **telegram-digest** — сбор контента с каналов
✅ **telegram-service-bot** — booking bots (кросс-навык)

---

## 4. INSTAGRAM — Соцсеть (Reels + Stories)

| Характеристика | Значение |
|---|---|
| Тип | Organic |
| Бюджет | $0 |
| Формат | Reels 15-60s, Stories, Carousel |
| Цель | CPA (Content Locking, SmartLink, Nutra) |
| Geo | Any, best US, RU, BR |

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция | Потенциал |
|------------|------|------|-----------|-----------|
| **Our ghost-surfer posting.py** | Python, Playwright | InstagramPoster | ✅ **УЖЕ ЕСТЬ** | Высокий |
| **Julian Ivaldy OTG Control** | Node.js | iPhone Voice Control farm | ⭐⭐ — через MCP | Средний |
| **SHAHINK/instabot** (7.6k⭐) | Python | API для взаимодействий | ⭐⭐⭐ | Средний |
| **instagrapi** (7.5k⭐) | Python | Неофициальный API Instagram | ⭐⭐⭐ | Высокий (риск бана) |

### Наш стек
✅ **ghost-surfer** (InstagramPoster) — posting.py
⬜ Нужна: мультиаккаунт ферма (как TikTok) с прогревом и уникализацией

---

## 5. PINTEREST — Визуальный поиск

| Характеристика | Значение |
|---|---|
| Тип | Organic |
| Бюджет | $0 |
| Формат | Pin-изображения, Idea Pins |
| Цель | SmartLink, Nutra, E-com CPA |
| Geo | US, UK, CA, AU — премиум трафик |
| CPA payout | $2-15 (Nutra), $0.50-3 (SmartLink) |

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция | Потенциал |
|------------|------|------|-----------|-----------|
| **SoCloseSociety/PinterestBulkPostBot** | Python, Selenium | Bulk постинг, CSV, планировщик | ⭐⭐⭐ — Python + Selenium | Высокий |
| **geekodour/pinterest-dashbot** | Python, Selenium | Дашборд + автопостинг | ⭐⭐ — Selenium | Средний |
| **bstoilov/py3-pinterest** | Python | Питон-API для Pinterest | ⭐⭐⭐ — чистый API | Высокий |
| **sergioteula/pinterest-automation** | Python | Тематический автопостинг | ⭐⭐⭐ | Средний |

### Наш стек
⬜ **НЕТ** — Pinterest не автоматизирован. Нужен навык `pinterest-automation` с интеграцией:
- PinterestBulkPostBot (Selenium) или py3-pinterest (API) через ghost-surfer
- Pin-генерация через Fal.ai → Bulk Upload
- Планировщик постинга

---

## 6. REDDIT — UGC-сообщество

| Характеристика | Значение |
|---|---|
| Тип | Organic |
| Бюджет | $0 |
| Формат | Посты в сабреддитах, комментарии, ссылки |
| Цель | SmartLink, Content Locking, Pay-Per-Call |
| Geo | US, UK, CA, AU |
| CPA payout | $1-5 (SmartLink), $3-10 (Content Locking) |

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция | Потенциал |
|------------|------|------|-----------|-----------|
| **praw-dev/praw** (3.5k⭐) | Python | Reddit API wrapper | ⭐⭐⭐ — нативный Python | Высокий |
| **eligrey/reddit-bots** | Python | Коллекция ботов | ⭐⭐⭐ | Средний |
| **RedditFeedAutoPoster** | Python | Автопостинг RSS→Reddit | ⭐⭐⭐ | Средний |
| **turnr/reddit-account-creator** | Python | Создание аккаунтов | ⭐⭐ | Средний |
| **Various BHW scripts** | Python | Multi-account Reddit poster | ⭐⭐ — PRAW + прокси | Высокий |

### Наш стек
⬜ **НЕТ** — Reddit не автоматизирован. Нужен навык `reddit-traffic-automation`:
- PRAW + ghost-surfer IdentityDB для управления аккаунтами
- Планировщик постинга по сабреддитам
- Парсинг трендовых тем для A/B тестирования офферов
- Auto-rotate аккаунтов при shadowban

---

## 7. PUSH NOTIFICATIONS — Web Push

| Характеристика | Значение |
|---|---|
| Тип | Paid |
| Бюджет | $10-100 старт, CPC $0.001-0.05 |
| Формат | Push-уведомление → Landing Page |
| Цель | Dating, Gambling, Nutra, Sweepstakes |
| Geo | Any, best IN, ID, PH, BR |
| CPA payout | $1-10 |
| ROI | До 350% (по кейсам EvaDav) |

### Платформы для покупки
- **EvaDav** — push + pop, CPC от $0.001
- **PropellerAds** — push, pop, native, CPC от $0.003
- **RichAds** — push + pop, автоматические правила
- **AdMaven** — push + pop + native
- **ROIads** — AI-driven оптимизация
- **Clickadu** — push + pop

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция | Потенциал |
|------------|------|------|-----------|-----------|
| **OneSignal API** | REST | Push-уведомления (сервер) | ⭐⭐⭐ — REST API | Средний |
| **Adverticing-Networks** | Docs | Описание сеток | Справочно | Информация |
| **Voluum/RedTrack/Binom** | API | Трекинг кампаний | ⭐⭐ — через API | Высокий |

### Наш стек
⬜ **НЕТ** — Push это paid-механика. Нужен:
- Аналитик: трекинг через Voluum API/Binom
- Оптимизатор: автоматическое правило white/black list
- Навык: `push-traffic-ads`

---

## 8. POPUNDER / POP — Pop-up трафик

| Характеристика | Значение |
|---|---|
| Тип | Paid |
| Бюджет | $5-50 старт, CPM $0.50-5 |
| Формат | Popup → Landing Page |
| Цель | SmartLink, Dating, Nutra, Mobile CPI |
| Geo | Any, best IN, ID, TH, VN, BR |
| CPA payout | $0.50-5 |

### Платформы для покупки
- PropellerAds — CPM от $0.50
- EvaDav — CPM от $0.30
- PopAds — CPM от $0.10
- Clickadu — CPM от $0.50
- RichAds — CPM от $0.50

### Инструменты GitHub

| Инструмент | Стэк | Суть |
|-----------|------|------|
| **Binom** | PHP + MySQL | Self-hosted трекинг |
| **Voluum** | SaaS | Облачный трекинг |
| **Keitaro** | PHP | Self-hosted трекинг + AB тесты |

### Наш стек
⬜ **НЕТ** — Popunder = media buying. Нужен:
- Трекер (Binom self-hosted или Keitaro)
- Система правил для автоматической оптимизации

---

## 9. NATIVE ADS — Нативная реклама

| Характеристика | Значение |
|---|---|
| Тип | Paid |
| Бюджет | $50-500 старт, CPC $0.05-0.50 |
| Формат | Статья/виджет → Landing Page |
| Цель | Nutra, Dating, Sweepstakes, Content Locking |
| Geo | US, UK, CA, AU (премиум), IN, PH (бюджет) |
| CPA payout | $5-40 (Nutra), $1-10 (Sweepstakes) |

### Платформы для покупки
- MGID — CPC от $0.05
- Taboola — CPC от $0.10 (мин $50)
- Outbrain — CPC от $0.15 (мин $100)
- RevContent — CPC от $0.08
- Adsterra Native — CPM от $1

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция |
|------------|------|------|-----------|
| **Various A/B test tools** | Python | A/B тестирование landing | ⭐⭐⭐ — через content-pipeline |

### Наш стек
⬜ **НЕТ** — Native = media buying с большим бюджетом.
- Требуется трекер и лендинги (у нас есть content-locking-cpa-test)
- Нужна: система pre-lander → offer routing

---

## 10. SEO — Поисковый трафик

| Характеристика | Значение |
|---|---|
| Тип | Organic |
| Бюджет | $0 (кроме хостинга) |
| Формат | Статьи, Landing Page, PBN |
| Цель | SmartLink, Nutra, E-com CPA |
| Geo | Any |
| Время выхода | 2-6 месяцев |

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция | Потенциал |
|------------|------|------|-----------|-----------|
| **serpapi/awesome-seo-tools** | Docs | 50+ SEO инструментов | Справочно | Информация |
| **GetPureScore/AutoSEO** | Python | Автоматическая SEO-оптимизация | ⭐⭐⭐ | Средний |
| **Ahrefs API / SEMrush API** | REST | Ключевые слова, конкуренты | ⭐⭐ — через API | Высокий |
| **WordPress + Yoast/RankMath** | PHP | CMS + SEO плагины | ✅ Уже есть WP навыки | Средний |
| **seo-automation** scripts | Python | Bulk мета-теги, sitemap | ⭐⭐⭐ | Средний |

### Наш стек
✅ **cricket-seo-content** — генерация SEO-сайтов под крикет (GitHub Pages)
✅ **premium-multipage-site** — генерация мультистраничных сайтов
⬜ Нужен: PBN менеджер, массовый SEO-аудит

---

## 11. EMAIL — Email-маркетинг

| Характеристика | Значение |
|---|---|
| Тип | Organic + Paid |
| Бюджет | $0-30 (SMTP сервер) |
| Формат | Письмо → Landing Page |
| Цель | Nutra, SmartLink, E-com CPA, Dating |
| Geo | Any, best US, UK, RU |
| CPA payout | $3-20 (Nutra) |
| Конверсия | 0.5-5% от отправленных |

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция | Потенциал |
|------------|------|------|-----------|-----------|
| **eracle/OpenOutreach** | Python, AI | AI-лидогенерация + email outreach | ⭐⭐⭐ — нативный Python | Высокий |
| **mailpy** | Python | SMTP-рассылка | ⭐⭐⭐ | Средний |
| **mailsend** | Python | Bulk email sender | ⭐⭐⭐ | Средний |
| **symfony/mailer** | PHP | Почтовый компонент | ⭐⭐ | Средний |
| **Mautic** | PHP | Open Source Marketing Automation | ⭐⭐⭐ | Высокий |
| **Our sending.py** | Python, SMTP | Базовая отправка | ✅ **УЖЕ ЕСТЬ** | Средний |

### Наш стек
✅ **ghost-surfer/email_automation.py** — SMTPSender, IMAPReceiver
⬜ Нужен: спам-тест, Warm-up писем, Multi-SMTP ротация, AI-персонализация (OpenOutreach)

---

## 12. FACEBOOK / META — Соцсети (Ads + Organic)

| Характеристика | Значение |
|---|---|
| Тип | Paid / Organic |
| Бюджет | $5-500 (ads), $0 (organic) |
| Формат | Ads, Marketplace, Groups, Pages |
| Цель | SmartLink, E-com CPA, Pay-Per-Call |
| Geo | Any |
| Риск | **Высокий** — строгие правила, частые баны |

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция | Потенциал |
|------------|------|------|-----------|-----------|
| **Facebook Marketing API SDK** | Python | API для рекламы | ⭐⭐ — API доступ | Высокий |
| **Meta Ad Library Scraper** | Python | Парсинг конкурентов | ⭐⭐⭐ — через BrowserClaw | Средний |
| **Various Marketplace bots** | Python | Автоматизация Marketplace | ⭐⭐ — Selenium | Низкий (бан) |
| **playwright-stealth** | Python | Антидетект Playwright | ⭐⭐⭐ — уже в ghost-surfer | Средний |

### Наш стек
✅ **ghost-surfer** — антидетект браузер
⬜ Нужен: Facebook Ads API, Ad Library аналитик

---

## 13. X (TWITTER) — Микроблогинг

| Характеристика | Значение |
|---|---|
| Тип | Organic |
| Бюджет | $0 |
| Формат | Твиты, треды, ссылки |
| Цель | SmartLink, Content Locking |
| Geo | US, JP, UK, IN |
| CPA payout | $0.50-3 |

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция | Потенциал |
|------------|------|------|-----------|-----------|
| **tweepy** (10k⭐) | Python | Twitter API wrapper | ⭐⭐⭐ | Высокий |
| **twikit** | Python | Неофициальный API Twitter | ⭐⭐⭐ | Средний |
| **Various automation bots** | Python | Авто-ретвит, авто-фоллов | ⭐⭐ | Низкий |

### Наш стек
⬜ **НЕТ** — X не автоматизирован. Нужен:
- Tweepy-интеграция с IdentityDB для мультиаккаунтов
- Планировщик твитов

---

## 14. DISCORD — Сообщества

| Характеристика | Значение |
|---|---|
| Тип | Organic |
| Бюджет | $0 |
| Формат | Сообщения, серверы, ссылки |
| Цель | SmartLink, Content Locking, iGaming |
| Geo | US, UK, EU |
| CPA payout | $1-5 |

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция | Потенциал |
|------------|------|------|-----------|-----------|
| **discord.py** (15k⭐) | Python | Discord API | ⭐⭐⭐ | Высокий |
| **Our cronjob + MCP** | Python | Cross-posting | ✅ Частично | Средний |

### Наш стек
⬜ **НЕТ** — нужна интеграция discord.py + ghost-surfer

---

## 15. LINKEDIN — B2B трафик

| Характеристика | Значение |
|---|---|
| Тип | Organic / Paid |
| Бюджет | $0-100 |
| Формат | Посты, статьи, InMail |
| Цель | B2B CPA, SaaS Affiliate, Pay-Per-Call |
| Geo | US, UK, EU |
| CPA payout | $10-100 (высокая ценность) |

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция | Потенциал |
|------------|------|------|-----------|-----------|
| **linkedin-api** (700⭐) | Python | LinkedIn API | ⭐⭐⭐ | Высокий |
| **tomquirk/linkedin-api** (500⭐) | Python | Неофициальный API | ⭐⭐ | Средний |
| **spinrise/linkedin-promoter** | Python | LinkedIn автопостинг | ⭐⭐⭐ | Средний |

### Наш стек
⬜ **НЕТ** — LinkedIn не автоматизирован

---

## 16. QUORA — Q&A платформа

| Характеристика | Значение |
|---|---|
| Тип | Organic |
| Бюджет | $0 |
| Формат | Ответы, ссылки в профиле |
| Цель | SmartLink, Content Locking |
| Geo | US, IN, UK |
| CPA payout | $0.50-2 |

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция |
|------------|------|------|-----------|
| **selenium-based Quora answer bots** | Python | Bulk ответы | ⭐⭐ — Selenium |

### Наш стек
⬜ **НЕТ**

---

## 17. MEDIUM — Блог-платформа

| Характеристика | Значение |
|---|---|
| Тип | Organic |
| Бюджет | $0 |
| Формат | Статьи, ссылки в тексте |
| Цель | SmartLink, Nutra, E-com CPA |
| Geo | US, UK, IN |

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция |
|------------|------|------|-----------|
| **medium-api** (500⭐) | Python | Публикация через API | ⭐⭐⭐ |
| **medium-selenium** | Python | Публикация через Selenium | ⭐⭐ |

### Наш стек
⬜ **НЕТ**

---

## 18. ADULT TRAFFIC — Adult-трафик

| Характеристика | Значение |
|---|---|
| Тип | Organic / Paid |
| Бюджет | $0-200 |
| Формат | Porn sites → Landing |
| Цель | Dating, Nutra, SmartLink |
| Geo | Any |
| Риск | **Высокий** — репутационный, для некоторых офферов запрещён |

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция |
|------------|------|------|-----------|
| **ExoClick API** | REST | Adult ad network | ⭐⭐ |
| **TrafficJunky API** | REST | Adult traffic | ⭐⭐ |

### Наш стек
⬜ **НЕТ** — Низкий приоритет, только при соответствующем оффере

---

## 19. INFLUENCER MARKETING — Инфлюенсеры

| Характеристика | Значение |
|---|---|
| Тип | Paid |
| Бюджет | $50-1000/пост |
| Формат | Shoutout, обзор, ссылка |
| Цель | Nutra, E-com, SmartLink |
| Geo | Any |
| CPA payout | $5-50 |

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция |
|------------|------|------|-----------|
| **AspireIQ / Grin** | SaaS | Платформы управления | - |
| **Telegram influencer search bots** | - | Поиск инфлюенсеров | ⭐ |

### Наш стек
⬜ **НЕТ** — Нужен менеджер поиска инфлюенсеров

---

## 20. CRAIGSLIST / OLX / AVITO — Classifieds

| Характеристика | Значение |
|---|---|
| Тип | Organic |
| Бюджет | $0 |
| Формат | Объявления, ссылки |
| Цель | Pay-Per-Call, SmartLink |
| Geo | US (Craigslist), RU (Avito), IN (OLX) |

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция |
|------------|------|------|-----------|
| **Avito/OLX posting scripts** | Python | Автопостинг | ⭐⭐ — Selenium |
| **Our Avito bot** | Python | ✅ **УЖЕ ЕСТЬ** (g003-avito-mortgage-template) | ✅ |

### Наш стек
✅ **Avito-шаблон** — в arbitrage-execution/templates

---

## 21. GOOGLE ADS — Поисковая реклама

| Характеристика | Значение |
|---|---|
| Тип | Paid |
| Бюджет | $50-500 старт |
| Формат | Текстовая реклама |
| Цель | SmartLink, E-com, Pay-Per-Call |
| Geo | Any |
| Сложность | **Высокая** — нужно качество аккаунта |

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция |
|------------|------|------|-----------|
| **google-ads-api** (Python) | Python | Официальный API | ⭐⭐⭐ |
| **Google Ads MCP** | MCP | MCP-интеграция | ⭐⭐⭐ |
| **Optmyzr** | SaaS | Автоматизация правил | - |

### Наш стек
⬜ **НЕТ** — низкий приоритет, большой бюджет

---

## 22. INSTANT CONTENT LOCKING — Блокировка контента

| Характеристика | Значение |
|---|---|
| Тип | Organic |
| Бюджет | $0 |
| Формат | Видео/статья → Замок → CPA |
| Цель | Content Locking (MobieLocks, CPAGrip, AdWork) |
| Geo | Any |
| CPA payout | $1-10 |

### Инструменты GitHub

| Репозиторий | Стэк | Суть | Интеграция |
|------------|------|------|-----------|
| **Our content-locking-cpa-test** | Python | ✅ **УЖЕ ЕСТЬ** (активный тест) | ✅ |
| **Our a-b-test-content-locking** | Python | ✅ **УЖЕ ЕСТЬ** (A/B тест) | ✅ |

### Наш стек
✅ **content-locking-cpa** — Активный тест #1, $235 pending
✅ **a-b-test-content-locking** — FOMO vs Social Proof vs Control

---

## 23. WHITELABEL / WHITE-LABEL — Под ключ

| Характеристика | Значение |
|---|---|
| Тип | Passive |
| Бюджет | $0 |
| Формат | Готовый бизнес под брендом |
| Цель | SaaS, VPS, Streaming |
| Geo | Any |

### Инструменты
- **Our cpa-bot-generator** — готовые брендированные боты
- **premium-multipage-site** — белые сайты под клиентов

### Наш стек
✅ **cpa-telegram-bot-generator** — 3 шаблона
✅ **premium-multipage-site** — мультистраничные сайты

---

## Сводная таблица приоритетов интеграции

| # | Источник | Бюджет | Есть в Hermes | Инструменты GitHub | Приоритет интеграции |
|---|----------|--------|--------------|-------------------|---------------------|
| 1 | **TikTok** | $0 | ✅ posting.py, tiktok-account-farm | chunhuduc, l-portet, Hormold | **КРИТИЧЕСКИЙ** |
| 2 | **Telegram** | $0 | ✅ channel-poster, TG-MiniApp-CPA | telethon, python-telegram-bot | **КРИТИЧЕСКИЙ** |
| 3 | **Content Locking** | $0 | ✅ тест #1 активен | — | **КРИТИЧЕСКИЙ** |
| 4 | **YouTube** | $0 | ✅ content-pipeline | yt-dlp | **ВЫСОКИЙ** |
| 5 | **Instagram** | $0 | ✅ posting.py | instagrapi | **ВЫСОКИЙ** |
| 6 | **Reddit** | $0 | ❌ | praw | **ВЫСОКИЙ** |
| 7 | **Pinterest** | $0 | ❌ | py3-pinterest, PinterestBulkPostBot | **ВЫСОКИЙ** |
| 8 | **Email** | $0-30 | ✅ email_automation.py | OpenOutreach, Mautic | **СРЕДНИЙ** |
| 9 | **SEO** | $0 | ✅ cricket-seo-content | AutoSEO | **СРЕДНИЙ** |
| 10 | **X/Twitter** | $0 | ❌ | tweepy | **СРЕДНИЙ** |
| 11 | **Discord** | $0 | ❌ | discord.py | **СРЕДНИЙ** |
| 12 | **Push** | $10+ | ❌ | — | Paid — **НИЗКИЙ** |
| 13 | **Popunder** | $5+ | ❌ | — | Paid — **НИЗКИЙ** |
| 14 | **Native** | $50+ | ❌ | — | Paid — **НИЗКИЙ** |
| 15 | **Facebook** | $5+ | ❌ | facebook-api | Paid — **НИЗКИЙ** |
| 16 | **LinkedIn** | $0 | ❌ | linkedin-api | **НИЗКИЙ** |
| 17 | **Quora** | $0 | ❌ | selenium | **НИЗКИЙ** |
| 18 | **Medium** | $0 | ❌ | medium-api | **НИЗКИЙ** |
| 19 | **Adult** | $0-200 | ❌ | ExoClick | **НИЗКИЙ** (по офферу) |
| 20 | **Google Ads** | $50+ | ❌ | google-ads-api | **НИЗКИЙ** (paid) |
| 21 | **Craigslist/Avito** | $0 | ✅ Avito template | — | **НИЗКИЙ** |
| 22 | **Influencer** | $50+ | ❌ | — | **НИЗКИЙ** |
| 23 | **Whitelabel** | $0 | ✅ cpa-bot-generator | — | **СРЕДНИЙ** |

---

## Стратегия внедрения (по приоритетам)

### Фаза 1 — Укрепить что есть (1-3 дня)
1. Довести до ума **tiktok-account-farm** — anti-detect, CAPTCHA, multi-account queue
2. **Content Locking** — завершить тест #1 ($235), масштабировать
3. **TG-MiniApp-CPA** — разблокировать, деплоить

### Фаза 2 — Organic $0 источники (3-7 дней)
4. **Reddit** — навык `reddit-traffic-automation` (PRAW + IdentityDB)
5. **Pinterest** — навык `pinterest-automation` (py3-pinterest + bulk poster)
6. **Instagram** — расширить posting.py до фермы (по аналогии с TikTok)

### Фаза 3 — Расширение (7-14 дней)
7. **Email** — OpenOutreach integration (AI-персонализация)
8. **X/Twitter** — tweepy + IdentityDB
9. **Discord** — discord.py + автопостинг
10. **SEO** — PBN manager, bulk-аудит

### Фаза 4 — Paid (условно, при бюджете)
11. Push, Popunder, Native, Facebook, Google Ads

---

**Вывод:** У нас уже есть 5 из 23 источников трафика в разной степени готовности. 
**Самый быстрый выхлоп:** TikTok + Telegram + Content Locking (всё $0, всё частично работает).
**Самый большой потенциал:** Pinterest + Reddit (премиум трафик, $0, есть готовые GitHub-инструменты).

*Создано: 2026-07-21*
