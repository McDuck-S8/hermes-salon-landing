# External Knowledge Sources for Daily Signal Scanning

Add these to `signal_scanner.py` or a new config file `config/external_sources.yaml`:

## GitHub Trending (daily)
- `https://github.com/trending/python?since=daily` — automation, arbitrage tools
- `https://github.com/trending/javascript?since=daily` — landing pages, bots
- `https://github.com/trending?since=daily&topic=affiliate-marketing`
- `https://github.com/trending?since=daily&topic=cpa-marketing`

## Affiliate/CPA Forums (RSS/HTML scrape)
- AffiliateFix: `https://affiliatefix.com/forums/affiliate-marketing-forum.2/index.rss`
- Partnerkin: `https://partnerkin.com/rss.xml` (case studies, offers)
- CPA.RU: `https://cpa.ru/rss.xml` (Russian CPA network)

## Reddit (JSON API)
- `https://www.reddit.com/r/affiliatemarketing/hot.json?limit=10`
- `https://www.reddit.com/r/crypto/hot.json?limit=10`
- `https://www.reddit.com/r/passive_income/hot.json?limit=10`
- `https://www.reddit.com/r/entrepreneur/hot.json?limit=10`

## YouTube Channels (via yt-dlp / invidious)
- Arbitrage/AI automation channels (add channel IDs to config)
- Search: `arbitrage 2026`, `CPA marketing`, `AI automation income`

## Telegram Channels (via existing tg_channel_poster)
- Already monitored via `tg_channel_poster` skill — ensure signal_scanner reads those logs

## Processing Pipeline

```python
def fetch_external_sources():
    sources = load_yaml('config/external_sources.yaml')
    for source in sources:
        try:
            if source['type'] == 'github_trending':
                items = fetch_github_trending(source['url'])
            elif source['type'] == 'rss':
                items = fetch_rss(source['url'])
            elif source['type'] == 'reddit':
                items = fetch_reddit(source['url'])
            elif source['type'] == 'youtube':
                items = fetch_youtube_channel(source['channel_id'])
            
            for item in items:
                write_to_kc(
                    raw_text=item['title'] + '\n' + item.get('summary', ''),
                    domain=source['domain'],
                    tags=['external', source['type'], 'signal'],
                    source=f"external:{source['name']}"
                )
        except Exception as e:
            log_error(f"External fetch failed: {source['name']}: {e}")
```

## Deduplication

- Group by domain + similar title (fuzzy match >80%)
- Keep only highest-engagement item per cluster
- Write 1 KC entry per cluster with multiple source URLs