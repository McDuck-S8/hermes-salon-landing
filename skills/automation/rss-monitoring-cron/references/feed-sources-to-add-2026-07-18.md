# Feed Sources to Add — 2026-07-18

Based on session findings, these external sources should be added to `rss_monitor.py` FEEDS list to increase external knowledge intake (currently 14% → target 30%+):

## Reddit Feeds (CPA/Arbitrage Communities)
```python
{
    "id": "reddit_affiliatemarketing",
    "url": "https://www.reddit.com/r/affiliatemarketing/.rss",
    "topic": "cpa-news",
    "method": "rss",
    "keywords": ["case study", "proof", "profit", "roi", "scaling", "traffic source", "offer", "lander", "creative"]
},
{
    "id": "reddit_passive_income",
    "url": "https://www.reddit.com/r/passive_income/.rss",
    "topic": "cpa-news",
    "method": "rss",
    "keywords": ["arbitrage", "cpa", "affiliate", "traffic", "conversion", "roi"]
},
{
    "id": "reddit_crypto",
    "url": "https://www.reddit.com/r/cryptocurrency/.rss",
    "topic": "finance",
    "method": "rss",
    "keywords": ["p2p", "usdt", "offramp", "fiat", "kyc", "exchange"]
}
```

## Additional YouTube Channels (for youtube_watch.py)
```python
CHANNELS = [
    {"id": "easy_traff",      "url": "https://www.youtube.com/@YOSArun/videos",    "topic": "cpa-arbitrage"},
    {"id": "partnerkin",      "url": "https://www.youtube.com/@partnerkin/videos",     "topic": "cpa-affiliate"},
    # ADD THESE:
    {"id": "cpa_rip",         "url": "https://www.youtube.com/@cparip/videos",         "topic": "cpa-arbitrage"},
    {"id": "affiliate_world", "url": "https://www.youtube.com/@affiliateworld/videos",  "topic": "cpa-affiliate"},
    {"id": "adcombo",         "url": "https://www.youtube.com/@adcombo/videos",         "topic": "cpa-offers"},
    {"id": "maxbounty",       "url": "https://www.youtube.com/@maxbounty/videos",       "topic": "cpa-offers"},
    {"id": "clickdealer",     "url": "https://www.youtube.com/@clickdealer/videos",     "topic": "cpa-offers"},
]
```

## GitHub Trending (for tech/automation)
```python
{
    "id": "github_trending_python",
    "url": "https://github.com/trending/python?since=daily",
    "topic": "automation",
    "method": "scrape",  # No RSS, need HTML scrape
    "keywords": ["agent", "automation", "ai", "llm", "browser", "scraper"]
}
```

## Telegram Channels (via RSS bridge)
```python
{
    "id": "tg_arbitrage_chat",
    "url": "https://rsshub.app/telegram/channel/arbitrage_chat",  # Requires RSSHub instance
    "topic": "cpa-news",
    "method": "rss",
}
```

## Priority Order for Implementation
1. **Reddit RSS** — Immediate, no auth, high signal (case studies, proofs)
2. **Additional YouTube** — Already have youtube_watch.py running, just add channels
3. **Telegram via RSSHub** — Need RSSHub instance or public bridge
4. **GitHub Trending** — Weekly scrape for automation/AI tools

## Expected Impact
- Reddit: ~20-30 entries/day per subreddit (filtered by keywords → ~5 notable/day)
- YouTube: ~5-10 new videos/week per channel
- Combined: Could add 50-100 external entries/week to Knowledge Cube
- Would shift external ratio from 14% → 30%+ within 2 weeks