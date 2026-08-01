# Monitoring Sources Configuration

Все платформы, настроенные на мониторинг. Источники = Telegram + YouTube + RSS/сайты + соцсети.

## Telegram (активный мониторинг)

| Канал | Тема | Приоритет |
|-------|------|-----------|
| @openai | OpenAI, GPT, релизы | Высокий |
| @anthropic | Claude, безопасность AI | Высокий |
| @deepseek | Open-source модели, исследования | Высокий |
| @hugging_face | ML-модели, датасеты | Высокий |
| @GoogleAI | Gemini, TensorFlow | Средний |
| @peraboratory | AI-инструменты, промпты | Средний |
| @nabormi_ai | AI-новости, обзоры | Средний |
| @binance | Криптобиржа, листинги | Высокий |
| @whale_alert | Крупные крипто-переводы | Высокий |
| @vcru | Стартапы, разработка | Высокий |
| @techcrunch | Стартапы, инвестиции | Высокий |
| @producthunt | Новые продукты | Средний |
| @news_ycombinator | Hacker News | Высокий |
| @securitylab | Кибербезопасность | Высокий |
| @github | Trending репозитории | Высокий |

Источник: `cache/telegram_monitor/channels_organized.json`

## YouTube

| Канал | Тема | Статус |
|-------|------|--------|
| @easy_traff | CPA-арбитраж, GramGPT, нейрокомментинг | ✅ Работает |
| @partnerkin | CPA-маркетинг, новости партнёрок | ✅ Работает |

Скрипт: `scripts/youtube_watch.py`
Cron: каждые 6ч (job: bac03cbb9537)
Вывод: `cache/youtube_watch/latest.json`

## RSS/Atom

| Фиды | Тема | Статус |
|------|------|--------|
| partnerkin.com/rss | CPA-новости, офферы | ✅ 50+ entries |
| affiliatefix.com/forums/-/index.rss | CPA-форум | ✅ 20 entries |
| openai.com/blog/rss.xml | AI-новости | ✅ 10 entries |
| rsshub.bestblogs.dev/anthropic/news | Anthropic AI | ✅ 10 entries |
| hnrss.org/frontpage | Hacker News | ✅ 10 entries |

Скрипт: `scripts/rss_monitor.py`
Cron: каждые 4ч (job: fb297032a852)
Вывод: `cache/rss_monitor/latest.json`

## AI OFM Content Generator

Генерация AI-изображений для Tribute-канала.
Скрипт: `projects/ai-ofm-tribute/scripts/cron.sh`
Cron: каждые 3ч (job: fbb3a8e05695)
Провайдер: Pollinations.ai (бесплатно, без ключа)
Вывод: `projects/ai-ofm-tribute/content/sessions/`

## Настройка

Все скрипты в `scripts/`. Cron jobs созданы через cronjob API.
При добавлении новых источников: создать скрипт → проверить → создать cron → обновить этот файл.
