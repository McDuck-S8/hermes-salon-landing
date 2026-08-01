# Monitoring Sources Reference

## RSS/Atom Feeds (rss_monitor.py)

| Source | URL | Topic | Status | Notes |
|--------|-----|-------|--------|-------|
| Partnerkin | https://partnerkin.com/rss | cpa-news | Dead RSS | Homepage scrape fallback implemented |
| AffiliateFix | https://www.affiliatefix.com/forums/-/index.rss | cpa-news | Working | 10 entries per run |
| OpenAI Blog | https://openai.com/blog/rss.xml | ai | Working | 10 entries per run |
| Anthropic (RSSHub) | https://rsshub.bestblogs.dev/anthropic/news | ai | Working | Proxy dependency |
| Hacker News | https://hnrss.org/frontpage?count=10 | tech | Working | 10 entries per run |

## YouTube Channels (youtube_watch.py)

Configured in `cache/youtube_watch/channels.json`:

| Channel | Category | Check Frequency |
|---------|----------|-----------------|
| Various AI/tech channels | ai, tech | Every run |

## Telegram Channels (telegram_monitor)

Configured in `cache/telegram_monitor/channels_organized.json`:

| Category | Channels |
|----------|----------|
| ai_news | @openai, @anthropic, @huggingface, etc. |
| crypto | @cryptonews, @defillama, etc. |
| cpa_arbitrage | @cpa_offers, @traffic_tips, etc. |

## Cron Jobs

| Job ID | Name | Script | Schedule | Deliver |
|--------|------|--------|----------|---------|
| fb297032a852 | rss-monitor | scripts/rss_monitor.py | Every 240 min | local |
| bac03cbb9537 | youtube-watch | scripts/youtube_watch.py | Every 120 min | local |
| (various) | telegram-monitor | scripts/telegram_monitor.py | Interval | local |

## Cache Locations

- RSS: `cache/rss_monitor/latest.json`
- YouTube: `cache/youtube_watch/latest.json`
- Telegram: `cache/telegram_monitor/latest.json`
- Daily Digest: `cache/daily_digest/latest.json`

## Integration Points

- `scripts/daily_digest.py` reads from `cache/rss_monitor/latest.json` (line 73)
- Autonomous agent reads cron health via `autonomous_agent.py:read_cron_health()`
- Proactive executor restarts failed cron jobs via `autonomous_agent.py:_action_fix_cron_errors()`