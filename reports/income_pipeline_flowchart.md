```mermaid
flowchart LR
    %% ===== STYLE DEFINITIONS =====
    classDef unverified fill:#ff6b6b,color:#fff,stroke:#c92a2a
    classDef testing fill:#ffd93d,color:#000,stroke:#f08c00
    classDef verified fill:#6bcb77,color:#fff,stroke:#37b24d
    classDef source fill:#1e3a5f,color:#fff,stroke:#4d96ff,stroke-width:2px
    classDef proxy fill:#5f3a1e,color:#fff,stroke:#fab005,stroke-width:2px
    classDef offer fill:#1e4d3a,color:#fff,stroke:#6bcb77,stroke-width:2px
    classDef withdrawal fill:#3a1e4d,color:#fff,stroke:#da77f2,stroke-width:2px
    classDef groupBox fill:#0d1117,color:#8b949e,stroke:#30363d,stroke-dasharray: 5 5

    %% ===== TRAFFIC SOURCES (LEFT) =====
    subgraph SRC1["📱 Telegram Channels"]
        direction TB
        S1["TG Organic CPA — FinCPANetwork (Fin"] :: testing
        S2["HotelCrimeaBot + Крымские TG-каналы"] :: testing
        S4["TG Organic CPA — Admitad (Multi-ver"] :: unverified
        S19["Digital Products (Шаблоны / Курсы /"] :: unverified
        S39["Survey/Sweepstakes CPA (Zeydoo)"] :: unverified
        S41["iGaming/Casino CPA (ClickDealer)"] :: unverified
        S44["OnlyFans Management (CrakRevenue)"] :: unverified
        S48["Travel Meta-search (Travelpayouts)"] :: unverified
        S50["Offline → Online (QR/Flyers → TG Bo"] :: unverified
    end
    class SRC1 groupBox
    subgraph SRC2["💼 Freelance Marketplaces"]
        direction TB
        S3["Продажа salon-bot на Kwork/FL.ru"] :: verified
    end
    class SRC2 groupBox
    subgraph SRC3["▶️ YouTube Shorts"]
        direction TB
        S5["YouTube Shorts EN → CPA VPN (Payone"] :: unverified
        S34["YouTube Long-form Reviews → Affilia"] :: unverified
        S38["Mobile CPI (OGAds/CPAlead) — App In"] :: unverified
        S43["Content Locking (CPAGrip/OGAds)"] :: unverified
    end
    class SRC3 groupBox
    subgraph SRC4["🎵 TikTok / Reels"]
        direction TB
        S6["TikTok RU → CPA (FinTech / Games / "] :: unverified
        S25["Micro-Influencer Shoutouts → CPA Da"] :: unverified
        S33["TikTok Shop Affiliate (Продажа това"] :: unverified
        S45["AI Companion / Dating Chat (CrakRev"] :: unverified
    end
    class SRC4 groupBox
    subgraph SRC5["🔗 Other"]
        direction TB
        S7["Avito Услуги → CPA Финтеч (Кредиты "] :: unverified
        S20["P2P Crypto Arbitrage (Spreads между"] :: unverified
        S21["Google Maps Local Lead Gen (Создани"] :: unverified
        S22["Push Notification Ads (PropellerAds"] :: unverified
        S23["Popunder Traffic (PopCash/PopAds) →"] :: unverified
        S24["Native Ads (Taboola/Outbrain/MGID) "] :: unverified
        S26["Quora Answers → CPA (SaaS/Finance/V"] :: unverified
        S27["Medium Articles → Affiliate (SaaS/P"] :: unverified
        S28["LinkedIn B2B Lead Gen (Data Enrichm"] :: unverified
        S29["X/Twitter Threads → CPA (Crypto/AI/"] :: unverified
        S30["Facebook Groups Organic → CPA (E-co"] :: unverified
        S31["Discord Communities → CPA (Crypto/A"] :: unverified
        S36["Domain Parking / Redirects (Expired"] :: unverified
        S37["Adult Traffic CPA (ExoClick/Traffic"] :: unverified
        S40["Nutra COD (AdCombo/CPAmatica) — Пря"] :: unverified
        S47["E-commerce Cashback (Admitad/Rakute"] :: unverified
    end
    class SRC5 groupBox
    subgraph SRC6["📌 Pinterest"]
        direction TB
        S8["Pinterest Organic (AI пины) → CPA G"] :: unverified
        S32["Pinterest AI Pins → Affiliate (Fash"] :: unverified
    end
    class SRC6 groupBox
    subgraph SRC7["🗣️ Reddit"]
        direction TB
        S9["Reddit (Subreddits) → CPA US/Global"] :: unverified
        S16["Email Lead Magnet → CPA Finance/Saa"] :: unverified
        S18["API Wrapper Reselling (AI Chat / Im"] :: unverified
    end
    class SRC7 groupBox
    subgraph SRC8["🌐 SEO Sites (GitHub Pages)"]
        direction TB
        S10["GitHub Pages / Netlify Sites (Сетка"] :: unverified
        S35["SEO Niche Sites (AdSense + Affiliat"] :: unverified
    end
    class SRC8 groupBox
    subgraph SRC9["📋 Craigslist"]
        direction TB
        S11["Craigslist US → Pay-Per-Call (Insur"] :: unverified
        S42["Pay-Per-Call (ClickDealer/Perform[c"] :: unverified
    end
    class SRC9 groupBox
    subgraph SRC10["🏪 OLX PL/UA"]
        direction TB
        S12["OLX PL/UA → CPA Nutra/Finance (COD)"] :: unverified
    end
    class SRC10 groupBox
    subgraph SRC11["🏪 Gumtree UK/AU"]
        direction TB
        S13["Gumtree UK/AU → CPA Local Services"] :: unverified
    end
    class SRC11 groupBox
    subgraph SRC12["🌍 Locanto Global"]
        direction TB
        S14["Locanto Global → CPA Dating/Jobs/Ed"] :: unverified
    end
    class SRC12 groupBox
    subgraph SRC13["🍁 Kijiji CA"]
        direction TB
        S15["Kijiji CA → CPA Finance/Insurance"] :: unverified
    end
    class SRC13 groupBox
    subgraph SRC14["📦 Авито Услуги"]
        direction TB
        S17["Telegram Bot SaaS — Аренда ботов дл"] :: unverified
        S49["Hosting/SaaS Reselling (White-label"] :: unverified
    end
    class SRC14 groupBox
    subgraph SRC15["📧 Email Lead Magnet"]
        direction TB
        S46["SmartLink AI (Mobidea/Zeydoo)"] :: unverified
    end
    class SRC15 groupBox

    %% ===== PROXIES / LAYERS (CENTER) =====
    subgraph PRX1["🎯 Landing Pages"]
        direction TB
        P1["Прямая CPA-ссылка в посте / Telegram-бот"] :: testing
        P4["Прямая диплинк-ссылка / Taplink-лендинг "] :: unverified
        P6["Ссылка в профиле (Linktree/Taplink) → ле"] :: unverified
        P8["Прямая ссылка на лендинг оффера / Taplin"] :: unverified
        P11["CPA-ссылка в объявлении / лендинг с "Ins"] :: unverified
        P13["Объявление на Gumtree → лендинг с "Get F"] :: unverified
        P14["Объявление с "hook" текстом → лендинг / "] :: unverified
        P18["Лендинг с API-интерфейсом / Telegram-бот"] :: unverified
        P19["Etsy/Gumroad магазин + собственный ленди"] :: unverified
        P21["Google Business Profile → сайт-одностран"] :: unverified
        P22["CPA-оффер → landing page (или прямая ссы"] :: unverified
        P23["CPA-оффер → landing page (яркий, кликабе"] :: unverified
        P30["Пост "Полезная подборка" / "Мой опыт" → "] :: unverified
        P32["AI-пин → ссылка на блог/лендинг → affili"] :: unverified
        P36["Домен → Parked page с рекламой / 301 red"] :: unverified
        P37["CPA-оффер → adult landing page"] :: unverified
        P39[""Free Giveaway" лендинг → survey / sweep"] :: unverified
        P40["Advertorial →_COD-лендинг с формой заказ"] :: unverified
        P41["Обзор-лендинг / "Casino Comparison" сайт"] :: unverified
        P45["Видео-обзор AI-companion → ссылка на lan"] :: unverified
        P46["Прямая ссылка / Landing page → SmartLink"] :: unverified
        P47["Сайт с купонами и cashback → пользовател"] :: unverified
        P48["Сайт/бот с поиском билетов → affiliate-с"] :: unverified
        P50["Флаер с QR → Telegram-бот / Landing page"] :: unverified
    end
    class PRX1 groupBox
    subgraph PRX2["🤖 Telegram Bots"]
        direction TB
        P2["HotelCrimeaBot (готовый бот) → ссылка на"] :: testing
        P3["Демо-бот + портфолио + видеодемо"] :: verified
        P17["Демо-бот + портфолио + видеодемо + кейсы"] :: unverified
    end
    class PRX2 groupBox
    subgraph PRX3["🔗 Direct Links"]
        direction TB
        P5["Ссылка в описании / закреплённый коммент"] :: unverified
        P7["Переписка в Авито чате → консультация → "] :: unverified
        P9["Профиль с Linktree / комментарий с реф-с"] :: unverified
        P12["Объявление на OLX → переписка → отправка"] :: unverified
        P26["Ответ на вопрос (1000+ символов, полезны"] :: unverified
        P29["Thread (5-10 твитов с ценностью) → ссылк"] :: unverified
    end
    class PRX3 groupBox
    subgraph PRX4["📦 Other Proxies"]
        direction TB
        P10["Статьи-обзоры / сравнения / "топ-10" с a"] :: unverified
        P15["Объявление "Free Insurance Quote" / "Car"] :: unverified
        P16["Лид-магнит (бесплатный PDF) → автоответч"] :: unverified
        P20["2+ биржи (Binance P2P + Bybit P2P + OKX "] :: unverified
        P24["Advertorial (статья-обзор) → CPA-ссылка "] :: unverified
        P25["Пост/сторис инфлюенсера → ссылка в шапке"] :: unverified
        P27["Статья-обзор "Best VPN 2026" / "Semrush "] :: unverified
        P28["LinkedIn InMail / Connection request → п"] :: unverified
        P31["Бесплатный контент → premium-каналы ($5-"] :: unverified
        P35["SEO-статья (2000+ слов) → AdSense контек"] :: unverified
        P42["Объявление "Free Quote" → виртуальный но"] :: unverified
        P44["Управление аккаунтом OF-модели: контент-"] :: unverified
        P49["White-label хостинг/VPN от провайдера → "] :: unverified
    end
    class PRX4 groupBox
    subgraph PRX5["🎬 Video Scripts"]
        direction TB
        P33["TikTok видео с product tag → TikTok Shop"] :: unverified
        P34["YouTube видео → affiliate-ссылки в описа"] :: unverified
        P38["Видео-обзор → ссылка в описании → conten"] :: unverified
        P43["Видео → "Link in bio" → content locker ("] :: unverified
    end
    class PRX5 groupBox

    %% ===== OFFERS (RIGHT) =====
    subgraph OFF1["💰 FinCPA Network"]
        direction TB
        O1["FinCPANetwork — кредитные офферы RU"] :: testing
        O7["FinCPANetwork / Admitad / Leadbit — кред"] :: unverified
        O50["CPA: Admitad/FinCPANetwork (RU финтех) /"] :: unverified
    end
    class OFF1 groupBox
    subgraph OFF2["✈️ Travelpayouts"]
        direction TB
        O2["Travelpayouts — отели (Booking.com, Ostr"] :: testing
        O48["Travelpayouts — Aviasales (0.5-3% от бро"] :: unverified
    end
    class OFF2 groupBox
    subgraph OFF3["💈 Salon Bot (Own Product)"]
        direction TB
        O3["Продажа готового бота salon-bot (запись "] :: verified
        O17["Собственный продукт: аренда TG-бота для "] :: unverified
    end
    class OFF3 groupBox
    subgraph OFF4["🛒 Admitad"]
        direction TB
        O4["Admitad — 2000+ офферов RU (Ozon, Wildbe"] :: unverified
        O6["Admitad / Travelpayouts / MaxBounty (RU "] :: unverified
        O8["Travelpayouts (отели/авиа), Admitad (тов"] :: unverified
        O30["Admitad (RU: Ozon, WB, AliExpress — 3-10"] :: unverified
        O47["Admitad (RU: Ozon, WB, AliExpress — 3-10"] :: unverified
    end
    class OFF4 groupBox
    subgraph OFF5["💵 MaxBounty"]
        direction TB
        O5["VPN CPA (Surfshark, NordVPN, AtlasVPN, P"] :: unverified
        O9["MaxBounty / ClickDealer / CPAGrip / MyLe"] :: unverified
        O22["MaxBounty / ClickDealer / MyLead — VPN ("] :: unverified
        O29["MaxBounty / MyLead — Crypto ($5-50 KYC),"] :: unverified
        O31["MaxBounty / MyLead — Crypto KYC ($5-50),"] :: unverified
        O36["Parking: Sedo / GoDaddy Parking ($0.01-0"] :: unverified
    end
    class OFF5 groupBox
    subgraph OFF6["🔗 Other Offers"]
        direction TB
        O10["- AdSense (контекстная реклама) — $0.05-"] :: unverified
        O18["Свой продукт: обёртка над бесплатными AI"] :: unverified
        O19["Свой продукт: Notion-шаблон ($5-30), Can"] :: unverified
        O20["Спреды USDT/RUB: покупка на одной бирже "] :: unverified
        O21["Собственный: передача лидов локальным по"] :: unverified
        O28["Собственный: сбор B2B-баз (Email + Phone"] :: unverified
        O33["TikTok Shop Affiliate Program — 5-20% ко"] :: unverified
        O44["Собственный: 20-40% от дохода модели (ma"] :: unverified
    end
    class OFF6 groupBox
    subgraph OFF7["💵 ClickDealer"]
        direction TB
        O11["Pay-Per-Call (ClickDealer, Perform[cb]) "] :: unverified
        O14["CrakRevenue / ClickDealer — Dating CPA ("] :: unverified
        O23["CrakRevenue / ClickDealer / CPAGrip — Da"] :: unverified
        O41["ClickDealer / Income Access / NetRefer —"] :: unverified
        O42["ClickDealer / Perform[cb] / Ringba — Hom"] :: unverified
    end
    class OFF7 groupBox
    subgraph OFF8["💊 AdCombo"]
        direction TB
        O12["AdCombo / CPAmatica / Everad — Nutra COD"] :: unverified
        O40["AdCombo / CPAmatica / Everad — Nutra COD"] :: unverified
    end
    class OFF8 groupBox
    subgraph OFF9["🤝 Impact"]
        direction TB
        O13["Impact / CJ Affiliate — UK/AU сервисы: H"] :: unverified
        O15["CJ Affiliate / Impact — CA Finance: Insu"] :: unverified
        O16["Impact / CJ Affiliate — SaaS: Semrush ($"] :: unverified
        O24["CJ Affiliate / Impact — Finance ($20-100"] :: unverified
        O26["Impact / CJ Affiliate — SaaS: Semrush ($"] :: unverified
        O27["Impact / CJ Affiliate — SaaS (Semrush, A"] :: unverified
        O34["Impact / CJ Affiliate — VPN ($2-30/insta"] :: unverified
        O35["Google AdSense ($0.10-5/клик) + Impact/C"] :: unverified
    end
    class OFF9 groupBox
    subgraph OFF10["💵 MyLead"]
        direction TB
        O25["CrakRevenue (Dating $2-8 регистрация), I"] :: unverified
        O45["CrakRevenue / MyLead — AI Dating Apps ($"] :: unverified
    end
    class OFF10 groupBox
    subgraph OFF11["🤝 CJ Affiliate"]
        direction TB
        O32["Amazon Associates (3-8%), ShareASale (fa"] :: unverified
    end
    class OFF11 groupBox
    subgraph OFF12["💘 CrakRevenue"]
        direction TB
        O37["CrakRevenue / ExoClick affiliate — Datin"] :: unverified
    end
    class OFF12 groupBox
    subgraph OFF13["💵 CPAGrip"]
        direction TB
        O38["OGAds ($5-12/install Tier-1), CPAGrip ($"] :: unverified
        O39["Zeydoo / CPAGrip / MyLead — Sweepstakes "] :: unverified
        O43["CPAGrip ($1-8/lead), OGAds ($2-12/instal"] :: unverified
    end
    class OFF13 groupBox
    subgraph OFF14["🔒 VPN Offers"]
        direction TB
        O46["Mobidea SmartLinks / Zeydoo SmartLinks —"] :: unverified
        O49["Собственный: white-label хостинг ($3-10/"] :: unverified
    end
    class OFF14 groupBox

    %% ===== WITHDRAWAL (BOTTOM) =====
    subgraph WDR1["💎 USDT → P2P → Карта"]
        direction TB
        W1["USDT (TRC20) → Binance P2P → Т-Банк"] :: testing
        W5["Payoneer → USDT (Binance) → Т-Банк "] :: unverified
        W6["WebMoney / USDT / Прямая карта (зав"] :: unverified
        W7["USDT / WebMoney / Прямая карта"] :: unverified
        W8["WebMoney / USDT / Payoneer / Wire"] :: unverified
        W9["Payoneer / Wire / USDT / Crypto"] :: unverified
        W11["Payoneer / Wire (US банк) / USDT (P"] :: unverified
        W12["WebMoney / USDT TRC20 → P2P"] :: unverified
        W14["Payoneer / USDT / WebMoney"] :: unverified
        W15["Payoneer / Wire / USDT"] :: unverified
        W18["Stripe / PayPal → Wise → USDT → P2P"] :: unverified
        W19["Stripe / PayPal → Wise → USDT → P2P"] :: unverified
        W22["Payoneer / USDT / WebMoney"] :: unverified
        W23["Payoneer / USDT / WebMoney"] :: unverified
        W25["Payoneer / USDT / Crypto"] :: unverified
        W26["Payoneer / Wire / USDT"] :: unverified
        W27["Payoneer / Wire / USDT"] :: unverified
        W29["Payoneer / USDT / Crypto"] :: unverified
        W30["WebMoney / Payoneer / USDT"] :: unverified
        W31["PayPal / Stripe / Crypto / USDT"] :: unverified
        W32["Amazon Gift Card / Wire / PayPal → "] :: unverified
        W33["TikTok Shop bank transfer → US банк"] :: unverified
        W34["Wire / Payoneer / USDT"] :: unverified
        W35["AdSense: Wire → Payoneer / Affiliat"] :: unverified
        W36["PayPal / Wire / USDT"] :: unverified
        W37["Payoneer / Wire / Crypto / USDT"] :: unverified
        W38["Payoneer / PayPal / USDT / Crypto"] :: unverified
        W39["Payoneer / USDT / WebMoney"] :: unverified
        W40["WebMoney / USDT / Wire"] :: unverified
        W41["Payoneer / Wire / Crypto (USDT)"] :: unverified
        W42["Payoneer / Wire / USDT"] :: unverified
        W43["Payoneer / PayPal / USDT / Crypto"] :: unverified
        W44["PayPal / Wire / Crypto / USDT"] :: unverified
        W45["Payoneer / Crypto / USDT"] :: unverified
        W46["Payoneer / USDT / Crypto"] :: unverified
        W47["WebMoney / Payoneer / USDT"] :: unverified
        W48["WebMoney / PayPal / USDT / Wire"] :: unverified
    end
    class WDR1 groupBox
    subgraph WDR2["🌐 WebMoney → Карта"]
        direction TB
        W2["WebMoney → Т-Банк карта"] :: testing
        W4["WebMoney → Т-Банк карта"] :: unverified
        W17["СБП / Карта РФ / WebMoney"] :: unverified
        W49["СБП / Карта РФ / WebMoney"] :: unverified
        W50["СБП / Карта РФ / WebMoney"] :: unverified
    end
    class WDR2 groupBox
    subgraph WDR3["⚡ СБП / Прямой перевод"]
        direction TB
        W3["Прямой перевод на карту (СБП / по н"] :: verified
        W21["СБП / Карта РФ / Venmo (если US ном"] :: unverified
    end
    class WDR3 groupBox
    subgraph WDR4["💳 Payoneer → USDT/P2P"]
        direction TB
        W10["- AdSense: Wire → банк РФ (сложно с"] :: unverified
        W13["Payoneer / Wire (UK банк)"] :: unverified
        W16["Payoneer / Wire (US банк)"] :: unverified
        W24["Payoneer / Wire (US банк)"] :: unverified
    end
    class WDR4 groupBox
    subgraph WDR5["🔗 Other"]
        direction TB
        W20["Карта РФ → Биржа → P2P → Карта РФ ("] :: unverified
    end
    class WDR5 groupBox
    subgraph WDR6["🏦 Wire Transfer"]
        direction TB
        W28["PayPal / Wise / Wire"] :: unverified
    end
    class WDR6 groupBox

    %% ===== FLOW CONNECTIONS =====
    S1 -->|traffic| P1 :: testing
    P1 -->|leads| O1 :: testing
    O1 -->|payout| W1 :: testing
    S2 -->|traffic| P2 :: testing
    P2 -->|leads| O2 :: testing
    O2 -->|payout| W2 :: testing
    S3 -->|traffic| P3 :: verified
    P3 -->|leads| O3 :: verified
    O3 -->|payout| W3 :: verified
    S4 -->|traffic| P4 :: unverified
    P4 -->|leads| O4 :: unverified
    O4 -->|payout| W4 :: unverified
    S5 -->|traffic| P5 :: unverified
    P5 -->|leads| O5 :: unverified
    O5 -->|payout| W5 :: unverified
    S6 -->|traffic| P6 :: unverified
    P6 -->|leads| O6 :: unverified
    O6 -->|payout| W6 :: unverified
    S7 -->|traffic| P7 :: unverified
    P7 -->|leads| O7 :: unverified
    O7 -->|payout| W7 :: unverified
    S8 -->|traffic| P8 :: unverified
    P8 -->|leads| O8 :: unverified
    O8 -->|payout| W8 :: unverified
    S9 -->|traffic| P9 :: unverified
    P9 -->|leads| O9 :: unverified
    O9 -->|payout| W9 :: unverified
    S10 -->|traffic| P10 :: unverified
    P10 -->|leads| O10 :: unverified
    O10 -->|payout| W10 :: unverified
    S11 -->|traffic| P11 :: unverified
    P11 -->|leads| O11 :: unverified
    O11 -->|payout| W11 :: unverified
    S12 -->|traffic| P12 :: unverified
    P12 -->|leads| O12 :: unverified
    O12 -->|payout| W12 :: unverified
    S13 -->|traffic| P13 :: unverified
    P13 -->|leads| O13 :: unverified
    O13 -->|payout| W13 :: unverified
    S14 -->|traffic| P14 :: unverified
    P14 -->|leads| O14 :: unverified
    O14 -->|payout| W14 :: unverified
    S15 -->|traffic| P15 :: unverified
    P15 -->|leads| O15 :: unverified
    O15 -->|payout| W15 :: unverified
    S16 -->|traffic| P16 :: unverified
    P16 -->|leads| O16 :: unverified
    O16 -->|payout| W16 :: unverified
    S17 -->|traffic| P17 :: unverified
    P17 -->|leads| O17 :: unverified
    O17 -->|payout| W17 :: unverified
    S18 -->|traffic| P18 :: unverified
    P18 -->|leads| O18 :: unverified
    O18 -->|payout| W18 :: unverified
    S19 -->|traffic| P19 :: unverified
    P19 -->|leads| O19 :: unverified
    O19 -->|payout| W19 :: unverified
    S20 -->|traffic| P20 :: unverified
    P20 -->|leads| O20 :: unverified
    O20 -->|payout| W20 :: unverified
    S21 -->|traffic| P21 :: unverified
    P21 -->|leads| O21 :: unverified
    O21 -->|payout| W21 :: unverified
    S22 -->|traffic| P22 :: unverified
    P22 -->|leads| O22 :: unverified
    O22 -->|payout| W22 :: unverified
    S23 -->|traffic| P23 :: unverified
    P23 -->|leads| O23 :: unverified
    O23 -->|payout| W23 :: unverified
    S24 -->|traffic| P24 :: unverified
    P24 -->|leads| O24 :: unverified
    O24 -->|payout| W24 :: unverified
    S25 -->|traffic| P25 :: unverified
    P25 -->|leads| O25 :: unverified
    O25 -->|payout| W25 :: unverified
    S26 -->|traffic| P26 :: unverified
    P26 -->|leads| O26 :: unverified
    O26 -->|payout| W26 :: unverified
    S27 -->|traffic| P27 :: unverified
    P27 -->|leads| O27 :: unverified
    O27 -->|payout| W27 :: unverified
    S28 -->|traffic| P28 :: unverified
    P28 -->|leads| O28 :: unverified
    O28 -->|payout| W28 :: unverified
    S29 -->|traffic| P29 :: unverified
    P29 -->|leads| O29 :: unverified
    O29 -->|payout| W29 :: unverified
    S30 -->|traffic| P30 :: unverified
    P30 -->|leads| O30 :: unverified
    O30 -->|payout| W30 :: unverified
    S31 -->|traffic| P31 :: unverified
    P31 -->|leads| O31 :: unverified
    O31 -->|payout| W31 :: unverified
    S32 -->|traffic| P32 :: unverified
    P32 -->|leads| O32 :: unverified
    O32 -->|payout| W32 :: unverified
    S33 -->|traffic| P33 :: unverified
    P33 -->|leads| O33 :: unverified
    O33 -->|payout| W33 :: unverified
    S34 -->|traffic| P34 :: unverified
    P34 -->|leads| O34 :: unverified
    O34 -->|payout| W34 :: unverified
    S35 -->|traffic| P35 :: unverified
    P35 -->|leads| O35 :: unverified
    O35 -->|payout| W35 :: unverified
    S36 -->|traffic| P36 :: unverified
    P36 -->|leads| O36 :: unverified
    O36 -->|payout| W36 :: unverified
    S37 -->|traffic| P37 :: unverified
    P37 -->|leads| O37 :: unverified
    O37 -->|payout| W37 :: unverified
    S38 -->|traffic| P38 :: unverified
    P38 -->|leads| O38 :: unverified
    O38 -->|payout| W38 :: unverified
    S39 -->|traffic| P39 :: unverified
    P39 -->|leads| O39 :: unverified
    O39 -->|payout| W39 :: unverified
    S40 -->|traffic| P40 :: unverified
    P40 -->|leads| O40 :: unverified
    O40 -->|payout| W40 :: unverified
    S41 -->|traffic| P41 :: unverified
    P41 -->|leads| O41 :: unverified
    O41 -->|payout| W41 :: unverified
    S42 -->|traffic| P42 :: unverified
    P42 -->|leads| O42 :: unverified
    O42 -->|payout| W42 :: unverified
    S43 -->|traffic| P43 :: unverified
    P43 -->|leads| O43 :: unverified
    O43 -->|payout| W43 :: unverified
    S44 -->|traffic| P44 :: unverified
    P44 -->|leads| O44 :: unverified
    O44 -->|payout| W44 :: unverified
    S45 -->|traffic| P45 :: unverified
    P45 -->|leads| O45 :: unverified
    O45 -->|payout| W45 :: unverified
    S46 -->|traffic| P46 :: unverified
    P46 -->|leads| O46 :: unverified
    O46 -->|payout| W46 :: unverified
    S47 -->|traffic| P47 :: unverified
    P47 -->|leads| O47 :: unverified
    O47 -->|payout| W47 :: unverified
    S48 -->|traffic| P48 :: unverified
    P48 -->|leads| O48 :: unverified
    O48 -->|payout| W48 :: unverified
    S49 -->|traffic| P49 :: unverified
    P49 -->|leads| O49 :: unverified
    O49 -->|payout| W49 :: unverified
    S50 -->|traffic| P50 :: unverified
    P50 -->|leads| O50 :: unverified
    O50 -->|payout| W50 :: unverified

    %% ===== SUMMARY AGGREGATE EDGES =====
    %% Source Summary
    SRC_SUM1["📱 Telegram Channels\n9 schemes"] :: source
    S1 -.-> SRC_SUM1
    SRC_SUM2["💼 Freelance Marketplaces\n1 schemes"] :: source
    S3 -.-> SRC_SUM2
    SRC_SUM3["▶️ YouTube Shorts\n4 schemes"] :: source
    S5 -.-> SRC_SUM3
    SRC_SUM4["🎵 TikTok / Reels\n4 schemes"] :: source
    S6 -.-> SRC_SUM4
    SRC_SUM5["🔗 Other\n16 schemes"] :: source
    S7 -.-> SRC_SUM5
    SRC_SUM6["📌 Pinterest\n2 schemes"] :: source
    S8 -.-> SRC_SUM6
    SRC_SUM7["🗣️ Reddit\n3 schemes"] :: source
    S9 -.-> SRC_SUM7
    SRC_SUM8["🌐 SEO Sites (GitHub Pages)\n2 schemes"] :: source
    S10 -.-> SRC_SUM8
    SRC_SUM9["📋 Craigslist\n2 schemes"] :: source
    S11 -.-> SRC_SUM9
    SRC_SUM10["🏪 OLX PL/UA\n1 schemes"] :: source
    S12 -.-> SRC_SUM10
    SRC_SUM11["🏪 Gumtree UK/AU\n1 schemes"] :: source
    S13 -.-> SRC_SUM11
    SRC_SUM12["🌍 Locanto Global\n1 schemes"] :: source
    S14 -.-> SRC_SUM12
    SRC_SUM13["🍁 Kijiji CA\n1 schemes"] :: source
    S15 -.-> SRC_SUM13
    SRC_SUM14["📦 Авито Услуги\n2 schemes"] :: source
    S17 -.-> SRC_SUM14
    SRC_SUM15["📧 Email Lead Magnet\n1 schemes"] :: source
    S46 -.-> SRC_SUM15

    %% Proxy Summary
    PRX_SUM1["🎯 Landing Pages\n24 schemes"] :: proxy
    P1 -.-> PRX_SUM1
    PRX_SUM2["🤖 Telegram Bots\n3 schemes"] :: proxy
    P2 -.-> PRX_SUM2
    PRX_SUM3["🔗 Direct Links\n6 schemes"] :: proxy
    P5 -.-> PRX_SUM3
    PRX_SUM4["📦 Other Proxies\n13 schemes"] :: proxy
    P10 -.-> PRX_SUM4
    PRX_SUM5["🎬 Video Scripts\n4 schemes"] :: proxy
    P33 -.-> PRX_SUM5

    %% Offer Summary
    OFF_SUM1["💰 FinCPA Network\n3 schemes"] :: offer
    O1 -.-> OFF_SUM1
    OFF_SUM2["✈️ Travelpayouts\n2 schemes"] :: offer
    O2 -.-> OFF_SUM2
    OFF_SUM3["💈 Salon Bot (Own Product)\n2 schemes"] :: offer
    O3 -.-> OFF_SUM3
    OFF_SUM4["🛒 Admitad\n5 schemes"] :: offer
    O4 -.-> OFF_SUM4
    OFF_SUM5["💵 MaxBounty\n6 schemes"] :: offer
    O5 -.-> OFF_SUM5
    OFF_SUM6["🔗 Other Offers\n8 schemes"] :: offer
    O10 -.-> OFF_SUM6
    OFF_SUM7["💵 ClickDealer\n5 schemes"] :: offer
    O11 -.-> OFF_SUM7
    OFF_SUM8["💊 AdCombo\n2 schemes"] :: offer
    O12 -.-> OFF_SUM8
    OFF_SUM9["🤝 Impact\n8 schemes"] :: offer
    O13 -.-> OFF_SUM9
    OFF_SUM10["💵 MyLead\n2 schemes"] :: offer
    O25 -.-> OFF_SUM10
    OFF_SUM11["🤝 CJ Affiliate\n1 schemes"] :: offer
    O32 -.-> OFF_SUM11
    OFF_SUM12["💘 CrakRevenue\n1 schemes"] :: offer
    O37 -.-> OFF_SUM12
    OFF_SUM13["💵 CPAGrip\n3 schemes"] :: offer
    O38 -.-> OFF_SUM13
    OFF_SUM14["🔒 VPN Offers\n2 schemes"] :: offer
    O46 -.-> OFF_SUM14

    %% Withdrawal Summary
    WDR_SUM1["💎 USDT → P2P → Карта\n37 schemes"] :: withdrawal
    W1 -.-> WDR_SUM1
    WDR_SUM2["🌐 WebMoney → Карта\n5 schemes"] :: withdrawal
    W2 -.-> WDR_SUM2
    WDR_SUM3["⚡ СБП / Прямой перевод\n2 schemes"] :: withdrawal
    W3 -.-> WDR_SUM3
    WDR_SUM4["💳 Payoneer → USDT/P2P\n4 schemes"] :: withdrawal
    W10 -.-> WDR_SUM4
    WDR_SUM5["🔗 Other\n1 schemes"] :: withdrawal
    W20 -.-> WDR_SUM5
    WDR_SUM6["🏦 Wire Transfer\n1 schemes"] :: withdrawal
    W28 -.-> WDR_SUM6

    %% MAIN PIPELINE FLOW
    SRC_MAIN["📥 ALL TRAFFIC SOURCES\n50 schemes"] :: source
    PRX_MAIN["⚙️ ALL PROXIES / LAYERS\nLanding + Bot + Video + Direct"] :: proxy
    OFF_MAIN["💰 ALL OFFERS / NETWORKS\nFinCPA, Admitad, Travelpayouts, MaxBounty, VPN, Own"] :: offer
    WDR_MAIN["💸 ALL WITHDRAWAL PATHS\nUSDT→P2P, WebMoney, Payoneer, Wire, СБП"] :: withdrawal

    SRC_MAIN -->|50 schemes traffic| PRX_MAIN
    PRX_MAIN -->|leads/conversions| OFF_MAIN
    OFF_MAIN -->|payouts| WDR_MAIN

    %% ===== LEGEND =====
    LEG_UNV["🔴 UNVERIFIED (47)"] :: unverified
    LEG_TST["🟡 TESTING (2)"] :: testing
    LEG_VER["🟢 VERIFIED (1)"] :: verified
    style LEG_UNV fill:#ff6b6b,color:#fff
    style LEG_TST fill:#ffd93d,color:#000
    style LEG_VER fill:#6bcb77,color:#fff
```