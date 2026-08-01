# Veo 3.1 Knowledge Base — Hermes Agent

> Дата: 2026-07-21
> Источник: исследование интернета (Google, YouTube, Reddit, AffiliateFix, RichAds, Partnerkin)
> Цель: закрыть дыры контент (30%), продажи (25%), коммуникация (15%)

---

## 1. Veo 3.1 — Возможности и Лимиты

### 1.1 Технические характеристики

| Параметр | Значение |
|---|---|
| Разрешение | 720p, 1080p |
| Соотношение сторон | 16:9, 9:16 |
| Длина клипа | 4, 6, 8 секунд (один запрос) |
| Аудио | Нативное, синхронизированное, диалоги |
| Водяной знак | SynthID (обязательно) |
| Image-to-video | Да |
| First/Last frame | Да (плавный переход между кадрами) |
| Ingredients to video | Да (референс-изображения) |
| Add/remove object | Да (через Veo 2) |
| Увеличение видео | Да (extend) |

### 1.2 API Лимиты

| Метод доступа | RPM | Concurrent | Макс. видео/запрос |
|---|---|---|---|
| Production API (veo-3.1-generate-001) | 50 | 10 | 4 |
| Preview API (veo-3.1-generate-preview) | 10 | 10 | 4 |
| Google AI Pro ($19.99/мес) | — | — | 3 видео/день, 720p |
| Google AI Ultra ($249.99/мес) | — | — | 5 видео/день, 1080p |

### 1.3 Цены (API)

| Режим | Цена/сек | 4 сек | 8 сек |
|---|---|---|---|
| Fast (720p/1080p) | $0.15/сек | $0.60 | $1.20 |
| Standard (720p/1080p) | $0.40/сек | $1.60 | $3.20 |
| 4K | дороже | — | — |

### 1.4 Через Composio

- Composio SDK 0.17.1 — подключён, ключ `ak_9gvDb4WnN1zJyPx3eeyr` WORKING
- Gemini toolkit — No Auth (7 actions)
- GEMINI_GENERATE_VIDEOS — асинхронный: operation_id → ожидание → download
- Лимиты через Composio = лимиты Gemini API (50 RPM production)
- Бесплатно через Composio? Нет чётких данных — скорее всего квота Gemini API действует

### 1.5 Коммерческое использование

- Разрешено через Vertex AI и Gemini Enterprise
- Все AI-видео должны иметь SynthID водяной знак
- Удалять логотип Gemini НЕЛЬЗЯ
- ML Training запрещён (нельзя тренировать модели на сгенерированных видео)
- TikTok, YouTube Shorts, Instagram Reels требуют маркировки AI-контента

### 1.6 Соцсети и AI-контент

| Платформа | Правила AI-контента |
|---|---|
| TikTok | Требует маркировку "AI-generated". Банят за не маркированный AI. |
| YouTube Shorts | Требует маркировку (Creative Commons + "Altered or synthetic content"). |
| Instagram Reels | Требует маркировку "Made with AI". Штрафы за сокрытие. |

---

## 2. Промпты для AI-видео

### 2.1 Формула Google Cloud (Veo 3.1)

```
[Кинематография] + [Субъект] + [Действие] + [Контекст] + [Стиль и Атмосфера]
```

**Пример:**
> Cinematography: Slow dolly forward. Subject: A man in his 30s, casual clothes. Action: Smiles and points at a smartphone screen showing a winning bet. Context: Modern living room, evening, warm lamp light. Style & ambiance: Cinematic, golden hour lighting, shallow depth of field.

### 2.2 Формула Runway (универсальная)

```
[Движение камеры] + [Сцена] + [Действие] + [Детали]
```

**Пример:**
> Slow dolly forward through misty forest. Ancient trees tower overhead. Figure in red coat walks away from camera. Sunlight pierces through canopy.

### 2.3 Типы движения камеры

| Тип | Эффект |
|---|---|
| Static (locked tripod) | Формально, контролируемо |
| Handheld steady | Органично, лично |
| Dolly forward | Приближение, intimacy |
| Dolly backward | Раскрытие контекста |
| Tracking (parallel) | Следование |
| Crane up/down | Смена перспективы |
| Pan (horizontal) | Обзор локации |
| Tilt (vertical) | Раскрытие масштаба |
| Orbit | Вокруг субъекта |
| Dolly zoom | Эффект Хичкока (vertigo) |
| FPV racing style | Адреналин |
| Drone ascending | Величие, масштаб |

### 2.4 Продвинутые техники

- **Positional prompting**: "left third", "upper right corner"
- **Motion brush**: указать направление движения для конкретного объекта
- **Reference images**: "ingredients to video" — сохранить стиль/персонажа между сценами
- **First frame + last frame**: плавный переход между двумя кадрами
- **Speed ramping**: нормальная → замедленная → нормальная
- **Audio prompting**: описать звуки как часть промпта ("wind whistling through trees, distant thunder")

### 2.5 Промпты для CPA-контента (адаптированные)

**Gambling/Betting:**
> Cinematography: Fast dolly zoom into smartphone screen. Subject: Hand holding phone, gold coins animation overlay. Action: Screen shows "YOU WON $2,450" with confetti. Context: Dark room, neon light reflections on screen. Style & ambiance: High-energy, bright flashes, cinematic 24fps.

**Finance/Crypto:**
> Cinematography: Slow push forward. Subject: Bitcoin glowing on dark background. Action: Coins multiply and stack upward. Context: Digital grid environment with data streams. Style & ambiance: Futuristic, matrix-style, blue/orange contrast.

**Nutra/Health:**
> Cinematography: Static shot, soft focus. Subject: Before/after body transformation. Action: Morph from overweight to fit. Context: White background, soft lighting. Style & ambiance: Clean, medical-grade, aspirational.

---

## 3. Виральные форматы TikTok/Shorts 2026

### 3.1 Топ-7 хуков по данным 8,426 видео

| # | Тип хука | Engagement | Как работает |
|---|---|---|---|
| 1 | **Hot Take** | 7.8% | Смелое утверждение → заставляет соглашаться/спорить |
| 2 | **Flip the Script** | 6.3% | Обратная сторона общеизвестного → "wait, what?" |
| 3 | **Talk to the Camera** | 6.1% | Сырая, неподготовленная энергия |
| 4 | **Pull Them In** | 6.1% | Вопрос или загадка → любопытство |
| 5 | **Show Something Wild** | 5.4% | Показать то, чего не видели |
| 6 | **Predict the Future** | 5.4% | Что будет дальше → тренды |
| 7 | **Lead with Proof** | 5.2% | Число/результат в первой секунде |

### 3.2 9 паттернов хуков (Socialync — 64+ шаблона)

| Паттерн | Пример | Почему работает |
|---|---|---|
| **Identity Call** | "If you're getting 200 views per TikTok, watch this." | Называет точную боль |
| **Confession** | "I lost $4,000 trying to grow on TikTok before I learned this." | Конкретная потеря = доверие |
| **Contrarian Strike** | "Everyone says post daily. Here's why that's killing your growth." | Называет священную корову и обещает вскрытие |
| **Open Loop** | "I found the algorithm loophole that took my account from 500 to 50K in 30 days." | "Loophole" подразумевает секрет |
| **Authority + Heresy** | "I've been a creator for 5 years and I'm telling you: most scheduling advice is wrong." | Авторитет + ересь |
| **Specific Number** | "I got 30 views per video for 3 months. Then I changed this and hit 100K." | До/После с числами |
| **Pain Point** | "If your Reels keep flopping, this is why." | Называет фрустрацию |
| **Curiosity Gap** | "Nobody tells you this part of being a content creator." | Недоговорённость |
| **Direct Command** | "Stop posting 60-second videos." | Атакует дефолтное поведение |

### 3.3 Структура вирального видео (7-секундное правило)

```
Секунды 1-3: Хук (остановить скролл)
Секунды 4-7: Зацепка (почему должны досмотреть)
Секунды 8-15: Контент (ценность/история)
Секунды 15-20: CTA (что делать)
```

### 3.4 Что НЕ работает в 2026

- Общие обращения ("hey guys", "hello everyone")
- Длинные интро с логотипом
- Скучные explainer без хука
- "Сырой" AI-контент без маркировки
- Спам ссылками в первый же секунде

---

## 4. CPA-офферы: Копирайтинг и Воронки

### 4.1 Топ CPA-сетки 2026

| Сеть | Вертикали | Особенности |
|---|---|---|
| Cpamatica | Nutra, Dating, Gambling | In-house offers |
| CrakRevenue | Dating, Gambling | Сильные креативы |
| Mobidea | Nutra, Gambling, Finance | Хороший аппрув |
| Zeydoo | Nutra, Sweepstakes, Gambling | Быстрые выплаты |
| ClickDealer | Finance, Gambling, Nutra | Профессиональный менеджмент |
| N1 Partners | iGaming, Betting | Strong CPA/RevShare |

### 4.2 Продающие заголовки для CPA

**Gambling/Betting:**
- "$2,450 в день? Вот proof" → Lead with Proof
- "Я нашёл баг в этой букмекерской конторе" → Open Loop
- "Большинство проигрывает из-за одной ошибки" → Hot Take + Identity Call

**Finance/Crypto:**
- "Как я заработал $500 за 10 минут (без риска)" → Specific Number
- "Банки ненавидят этот трюк" → Contrarian Strike
- "Твой депозит работает против тебя" → Pain Point

**Nutra/Health:**
- "Я скинул 15 кг за 30 дней. Вот как." → Lead with Proof
- "Врачи молчат об этой добавке" → Flip the Script
- "Твоя диета не работает. Вот почему." → Contrarian Strike

### 4.3 Структура воронки Content Locking

```
Traffic (TikTok/Shorts/Ads)
    ↓
Telegram Mini App / Landing Page
    ↓
Content Locker ("Complete 1 offer to unlock")
    ↓
CPA Offer (Gambling/Finance/Nutra)
    ↓
Payout (CPA/RevShare)
```

**Ключевые элементы контент-локера:**
- Привлекательный тизер (что увидят после прохождения)
- 1-3 простых оффера (анкета, установка приложения, регистрация)
- Прогресс-бар выполнения
- Social proof ("Уже 2,847 человек разблокировали")

### 4.4 Telegram воронки 2026

- CPC от $0.015 (push-style ads в Mini Apps)
- 3 модели: funnels (заменяют лендинги), paid placements, Telegram Ads
- RevShare лучше для Telegram community трафика (выше LTV)
- Важно: чёткое разделение между рекламным кабинетом и ссылками (чтобы не блокировали)

---

## 5. Сообщества арбитражников

### 5.1 Telegram-каналы и чаты (RichAds, 2026)

| Название | Тип | Фокус |
|---|---|---|
| **Partnerkin** | Канал | Новости, кейсы, гайды |
| **RichAds** | Канал | Traffic acquisition, Telegram ads |
| **AffiliateWeapons** | Канал | Инструменты, креативы |
| **Affiliate Marketing** | Чат | Обсуждения, вопросы |
| **Wise Affiliate** | Канал | Обучение, стратегии |
| **Affsecret** | Чат | Эксклюзивные связки |
| **Zeydoo CPA** | Канал | CPA офферы, промо |
| **Mobidea Affiliate Hub** | Чат | Новости, обсуждения |
| **ClickDealer** | Канал | Affiliate менеджмент |
| **Affiliate Insiders** | Чат | Закрытый клуб |

### 5.2 Форумы

- **AffiliateFix** — крупнейший форум (Gambling, Dating, Nutra секции)
- **Partnerkin** — русскоязычный форум (сертификация, кейсы)
- **STM Forum** — платный, но эксклюзивный

### 5.3 Как находить партнёров

- Вступать в Telegram чаты, а не только читать каналы
- Делиться своими кейсами (даже маленькими) — привлекает партнёров
- Модели партнёрства: RevShare 50/50, CPA + RevShare hybrid
- Искать на AffiliateFix в разделе "Looking for partner"

---

## 6. Топ-10 Виральных форматов для CPA

| # | Формат | Хук | Структура | CTA | Пример для CPA |
|---|---|---|---|---|---|
| 1 | **"Я нашёл баг"** | Open Loop: "Я нашёл баг в [казино/бирже]" | Показать скриншот выигрыша → объяснить "схему" → оффер | "Ссылка в описании/бот" | Gambling/Crypto |
| 2 | **Proof-видео** | Lead with Proof: "$2,450 за 10 минут" | Экран с балансом → ускоренная съёмка → результат | "Хочешь так же? Жми ссылку" | Finance |
| 3 | **Hot Take** | "Букмекеры разводят вас" | Смелое заявление → разбор → альтернатива | "Подпишись, пока не удалили" | Gambling |
| 4 | **Before/After** | Specific Pain: "15 кг за месяц" | Морфинг тела → продукт → результат | "Ссылка в шапке профиля" | Nutra |
| 5 | **Flip the Script** | "Врачи не хотят чтобы вы знали" | Статистика → разоблачение → решение | "Тыкни сюда" | Nutra/Health |
| 6 | **Secrets Revealed** | Identity + Curiosity: "Топ-трейдеры это скрывают" | Тёмная комната → графики → "секретная стратегия" | "Бесплатный сигнал в боте" | Crypto |
| 7 | **Tutorial + CTA** | Pull Them In: "Как вывести $100 за 5 минут?" | Инструкция на экране → простые шаги → результат | "Повтори сам по ссылке" | Finance/Betting |
| 8 | **Trend Jacking** | Predict the Future: "Через месяц это взлетит" | Новость → анализ → "я уже вложился" | "Быстрее всех тут" | Crypto |
| 9 | **UGC Product Showcase** | Show Something Wild: выглядит как пользовательский обзор | Держит продукт → эмоция → "работает 100%" | "Заказать тут (ссылка)" | Nutra |
| 10 | **Социальное доказательство** | Lead with Proof: "2,000 человек уже заработали" | Скриншоты отзывов → статистика → оффер | "Не отставай" | Любая вертикаль |

---

## 7. План действий (Синтез)

### Этап 1: Контент (30% → 60%)
- Использовать Veo 3.1 через Composio для генерации 8-секундных клипов
- Применять формулу Google Cloud: [Cinematography] + [Subject] + [Action] + [Context] + [Style]
- Тестировать форматы #1-#4 из таблицы топ-10
- Постить на TikTok + Shorts с маркировкой "AI-generated"

### Этап 2: Продажи (25% → 50%)
- Настроить Telegram воронку с Content Locker
- CPA-сетки: Cpamatica (gambling), CrakRevenue (dating), Zeydoo (nutra)
- Трекинг: Keitaro или Binom (самый дешёвый)

### Этап 3: Коммуникация (15% → 30%)
- Вступить в Partnerkin, AffiliateWeapons, Affsecret (Telegram)
- Зарегистрироваться на AffiliateFix
- Делиться кейсами → привлекать партнёров

---

## 8. Источники

- [Google Cloud — Ultimate prompting guide for Veo 3.1](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1)
- [Runway — AI Video Prompting Guide: 92 Ready-to-Use Prompts](https://runwayml.com/resources/ai-video-prompting-guide)
- [Socialync — 64+ Viral Hooks That Actually Work in 2026](https://www.socialync.io/viral-hooks-library)
- [The Content Labs — 7 TikTok Hooks That Actually Go Viral 2026](https://thecontentlabs.app/blog/tiktok-hooks-that-work)
- [AIFreeAPI — Veo 3.1 API Rate Limit Guide](https://www.aifreeapi.com/en/posts/veo-3-1-api-rate-limit)
- [RichAds — 17 Best Affiliate Marketing Telegram Groups](https://richads.com/blog/affiliate-marketing-telegram-groups)
- [AffiliateFix — Creating Killer Landing Pages To Promote CPA Offers](https://www.affiliatefix.com/threads/creating-killer-landing-pages-to-promote-cpa-offers.9357)
- [RichAds + Partnerkin — Landing page best practices](https://richads.com/blog/10-high-converting-landing-page-examples-for-affiliate-marketing-best-practices)
- [ClickBank — 12 Tips for Writing Affiliate Marketing Headlines](https://www.clickbank.com/blog/affiliate-marketing-headlines)
- [Pay2.House — Telegram Funnels in Affiliate Marketing 2026](https://pay2.house/blogs/article/telegram-voronki-v-arbitrazhe-2026)
