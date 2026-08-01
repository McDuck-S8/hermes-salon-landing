# RSS Monitor Feed Inventory — 2026-07-19

## Active Feeds (16 total)

### CPA/Arbitrage (2)
| Feed ID | URL | Method | Notes |
|---------|-----|--------|-------|
| partnerkin | partnerkin.com/rss | homepage scrape | RSS dead, scrapes blog/tribuna/stati |
| affiliatefix | affiliatefix.com/forums/-/index.rss | RSS 2.0 | Forum threads, HTML in summaries |

### Reddit (14)
| Feed ID | Subreddit | Topic | Status |
|---------|-----------|-------|--------|
| reddit_affiliatemarketing | r/affiliatemarketing | cpa-news | ✅ |
| reddit_passive_income | r/passive_income | cpa-news | ⚠️ rate limited |
| reddit_crypto | r/CryptoCurrency | crypto | ✅ |
| reddit_entrepreneur | r/Entrepreneur | business | ⚠️ rate limited |
| reddit_ppc | r/PPC | cpa-news | ⚠️ rate limited |
| reddit_adtech | r/adtech | cpa-news | ⚠️ rate limited |
| reddit_growthhacking | r/growthhacking | cpa-news | ✅ |
| reddit_digital_marketing | r/digital_marketing | cpa-news | ⚠️ rate limited |
| reddit_seo | r/SEO | cpa-news | ⚠️ rate limited |
| reddit_sportsbetting | r/sportsbetting | gambling | ✅ NEW |
| reddit_beermoney | r/beermoney | side-income | ✅ NEW |
| reddit_workonline | r/workonline | side-income | ✅ NEW |
| reddit_juststart | r/juststart | affiliate-seo | ✅ NEW |
| reddit_sidehustle | r/sidehustle | side-income | ✅ NEW |

## Removed Feeds (2026-07-19)
- openai_blog — AI research, not CPA-relevant
- anthropic_rsshub — AI research, proxy-dependent
- hackernews — tech news, not CPA-relevant

## YouTube Channels (5)
| Channel ID | Handle | Topic | Status |
|------------|--------|-------|--------|
| easy_traff | @YOSArun | cpa-arbitrage | ✅ |
| partnerkin | @partnerkin | cpa-affiliate | ✅ |
| icpsquad | @icpsquad | cpa-arbitrage | ✅ |
| traffic_hunter | @TrafficHunter | cpa-arbitrage | ✅ NEW |
| webvork | @webvork | cpa-affiliate | ✅ NEW |

## Cache Format
```json
{
  "timestamp": "2026-07-19T01:29:31",
  "feeds": {
    "partnerkin": [{"title": "...", "url": "...", "summary": "..."}],
    "affiliatefix": [...],
    ...
  }
}
```

## YouTube Cache Format
```json
{
  "timestamp": "2026-07-19T01:25:00",
  "channels": {
    "easy_traff": {
      "url": "https://www.youtube.com/@YOSArun/videos",
      "topic": "cpa-arbitrage",
      "videos": [
        {
          "id": "...",
          "title": "...",
          "url": "https://youtube.com/watch?v=...",
          "duration": "12:34",
          "description": "...(2000 chars)...",
          "tags": ["tag1", "tag2"]
        }
      ]
    }
  }
}
```
