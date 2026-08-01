---
name: cricket-seo-content
description: 'Генерация SEO-сайта под крикет Индия на GitHub Pages. Статьи, матчи, прогнозы — органический трафик из Google/Yandex.'
domain: web-development
keywords: [seo, cricket, india, content, blog, github-pages, organic-traffic]
---

# Cricket SEO Content — Генератор

## Назначение
Создаёт контентный сайт про крикет для Индии на GitHub Pages. Бесплатный хостинг, SEO-оптимизация, органический трафик. Долгий (3-6 мес до результата), но стабильный поток.

## Когда использовать
- Есть время на раскачку (3-6 месяцев)
- Нужен стабильный источник трафика (не зависит от соцсетей)
- Накопительный эффект — каждая статья работает годами

## Структура сайта
```
projects/cricket-{name}-seo/
├── index.html              # Главная: последние матчи, прогнозы
├── 404.html                # Страница ошибки
├── sitemap.xml             # Для Google Search Console
├── robots.txt              # Для индексации
├── articles/
│   ├── ipl-2026-preview.html
│   ├── india-aus-t20-prediction.html
│   ├── cricket-betting-tips.html
│   └── ...
└── (хостится на GitHub Pages)
```

## SEO-ключевые слова (Индия)
| Категория | Ключевые слова |
|---|---|
| Матчи | India vs Australia live, today match, cricket score, live streaming |
| Ставки | cricket betting tips, today match prediction, toss prediction, dream11 team |
| События | IPL 2026, World Cup 2027, T20 World Cup, Asia Cup |
| Коммерция | betting sites India, online cricket betting, best odds |

## Контент-план
| Тип | Частота | Трафик через |
|---|---|---|
| Превью матча | 2-3/нед | Google Search |
| Прогноз на ставки | 1/день | Google + прямые |
| Результаты/обзор | после матча | Google + соцсети |
| Гайды/советы | 1/нед | Evergreen |

## Оптимизация
- `<title>`: ключевое слово + бренд (60 символов)
- `<meta name="description">`: 150-160 символов, ключ в начале
- `<h1>`: ровно один, ключевое слово
- Alt-тексты у изображений: описание + ключ
- Internal linking: статья → другие статьи → главная
- JSON-LD разметка (SportsEvent, NewsArticle)
- Sitemap.xml + robots.txt → Google Search Console
- Core Web Vitals: быстрый хостинг GitHub Pages, оптимизированные изображения

## Контент стратегия
### Headlines (CTR)
```
🚫 "India vs Australia" → ✅ "India vs Australia LIVE: Score, Prediction & Betting Tips"
🚫 "IPL 2026" → ✅ "IPL 2026: Full Schedule, Teams Predictions & Betting Guide"
```

### CTA на оффер
- In-text: "Check the best odds for this match on [1xBet/1win]"
- End of article: "Ready to bet? Sign up on [partner] and get [bonus]"
- Sidebar: Top betting sites with ratings

## Техническая реализация
1. Создать проект `projects/cricket-{name}-seo/`
2. index.html — лендинг с последними матчами и прогнозами
3. Каждая статья — отдельный HTML-файл в `articles/`
4. Sitemap.xml генерируется автоматом при добавлении статьи
5. GitHub Pages (бесплатный хостинг, HTTPS, быстрый)

## Метрики
| Этап | Цель | Инструмент |
|---|---|---|
| Индексация | < 1 мес | Google Search Console |
| Статьи в топ-10 | < 6 мес | Search Console |
| Посещаемость | 1000+/мес через 6 мес | Google Analytics |
| Конверсия | > 1% с CTA на оффер | Своя аналитика |

## Альтернативы
- **Telegram канал** — быстрее, но менее стабильный
- **YouTube Shorts** — видео-трафик, дольше живут креативы
- **Instagram Reels** — виральный потенциал, но алгоритмы меняются

## Pitfalls
- SEO не работает без контента — минимум 10 статей перед активным продвижением
- Google может не индексировать GitHub Pages если домен в чёрном списке
- Не использовать копипаст — уникальность >90%, иначе санкции
- Keywords stuffing убивает ранжирование — естественные тексты
- Для Индии важен хинди/региональный контент — английский работает но уже
