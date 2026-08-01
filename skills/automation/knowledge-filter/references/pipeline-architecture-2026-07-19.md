# Knowledge Pipeline Architecture — 2026-07-19

## Pipeline Script
`scripts/knowledge_pipeline.py` — unified entry point for RSS→YT→Filter→KC.

## Cron Job
- **ID:** `fbf81e5c8be1`
- **Name:** `knowledge-pipeline-rss-yt-kc`
- **Schedule:** every 2 hours
- **Script:** `knowledge_pipeline.py`

## Flow
```
knowledge_pipeline.py (every 2h)
  ├── rss_monitor.py → cache/rss_monitor/latest.json
  ├── youtube_watch.py → cache/youtube_watch/latest.json
  └── filter.py --test-rss --limit 50 → kc_entries via kc_rag.upsert()
```

## Feed Inventory (2026-07-19)

### RSS Feeds (15 total)
| Feed ID | Source | Topic | Status |
|---------|--------|-------|--------|
| partnerkin | partnerkin.com | cpa-news | ✅ |
| affiliatefix | affiliatefix.com | cpa-news | ✅ |
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

### YouTube Channels (5 total)
| Channel ID | Handle | Topic | Status |
|------------|--------|-------|--------|
| easy_traff | @YOSArun | cpa-arbitrage | ✅ |
| partnerkin | @partnerkin | cpa-affiliate | ✅ |
| icpsquad | @icpsquad | cpa-arbitrage | ✅ |
| traffic_hunter | @TrafficHunter | cpa-arbitrage | ✅ NEW |
| webvork | @webvork | cpa-affiliate | ✅ NEW |

## KC Stats After Pipeline (2026-07-19)
- Total kc_entries: 445
- knowledge_filter entries: 48
- External (rss + yt + filter): 155 / 445 = 34.8%
- Target: 30% ✅

## Removed Feeds (garbage for CPA context)
- openai_blog — AI research, not CPA-relevant
- anthropic_rsshub — AI research, proxy-dependent
- hackernews — tech news, not CPA-relevant
- affiliateuniverse (YouTube) — no videos tab
- mikhailsharm (YouTube) — 404 not found
