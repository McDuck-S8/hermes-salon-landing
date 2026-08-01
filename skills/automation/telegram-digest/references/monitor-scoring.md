# Telegram Monitor — Scoring & Presets

## Scoring Algorithm (monitor.py)

Each message gets a score based on:

| Factor | Points | Condition |
|--------|--------|-----------|
| Views vs avg | +3 | views > 2x channel average |
| Viral | +5 | views > 50,000 |
| Trending | +3 | views > 10,000 |
| Forwards | +3 | forwards > 100 |
| Keyword hit | +1 each | matches hot keyword list |

**Threshold for "interesting":** score >= 3

## Hot Keywords

```
breaking, just launched, announcing, new release,
partnership, acquisition, funding, raised,
open source, free, limit, banned,
security, hack, vulnerability,
г成長, запуск, партнёрство, покупка,
бесплатно, новый релиз, обновление
```

## Channel Presets

| Preset | Channels | Use case |
|--------|----------|----------|
| `ai_news` | openai, GoogleAI, anthropic, deepseek, hugging_face, nabormi_ai, peraboratory | AI industry |
| `crypto` | binance, coinbase, crypto, whale_alert | Crypto market |
| `tech_news` | techcrunch, producthunt, news_ycombinator | Tech startups |
| `ru_news` | rt_russian, tass_agency, rianovosti, vcru, rbk_news | Russian news |
| `all` | from channels.json | Everything |

## Channels Config

File: `cache/telegram_monitor/channels.json`

```json
{
  "channels": ["openai", "GoogleAI", "anthropic"],
  "hours": 24,
  "description": "AI & Tech news channels"
}
```

## Report Output

- Raw JSON: `cache/telegram_monitor/latest_raw.json`
- Markdown report: `cache/telegram_monitor/latest_report.md`
- Interesting items: `cache/telegram_monitor/latest_interesting.json`

## Cron Schedule

- Job name: `telegram-monitor`
- Schedule: every 6 hours
- Script: `~/.hermes/scripts/telegram_cron_monitor.py`
- Deliver: local (check via `cronjob action='list'`)
