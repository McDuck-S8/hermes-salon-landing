# RSS Feed Sources for Monitoring

Verified RSS feeds that work with the monitoring pipeline. Each entry notes format, quirks, and known issues.

## AI / LLM Industry

| Feed | URL | Format | Notes |
|------|-----|--------|-------|
| OpenAI Blog | `https://openai.com/blog/rss.xml` | RSS 2.0 | Long descriptions with HTML |
| Anthropic News | `https://rsshub.bestblogs.dev/anthropic/news` | RSS 2.0 (via RSSHub proxy) | **Descriptions in `<content:encoded>`** — the feed puts full article HTML in `<content:encoded>` rather than `<description>`. The parser checks `content:encoded` as fallback and strips HTML |

## CPA / Arbitrage

| Feed | URL | Format | Notes |
|------|-----|--------|-------|
| Partnerkin | `https://partnerkin.com/rss` | RSS 2.0 (DEAD) | **RSS stopped updating Nov 2025**. The monitor now uses `_scrape_partnerkin()` to scrape the homepage (https://partnerkin.com) for recent articles. Fetches each article page for date+description. Returns up to 15 entries. Site is alive (Jun/Jul 2026 articles) but RSS is not regenerated |
| AffiliateFix | `https://www.affiliatefix.com/forums/-/index.rss` | RSS 2.0 (XenForo) | **Descriptions available** — XenForo RSS includes first-post content in `<description>` tags. All 10 entries have non-empty descriptions. If a future version stops including descriptions, fetch from URL (~3-5s per URL) |

## Tech / Hacker News

| Feed | URL | Format | Notes |
|------|-----|--------|-------|
| HN Front Page | `https://hnrss.org/frontpage?count=10` | RSS 2.0 | Reliable, always fresh. Descriptions = HN comment thread URLs |

## YouTube (not RSS, uses yt-dlp)

| Channel | URL | Topic | Status |
|---------|-----|-------|--------|
| easy_traff | `https://www.youtube.com/@easy_traff/videos` | CPA arbitrage | ✅ Working |
| partnerkin | `https://www.youtube.com/@partnerkin/videos` | CPA analytics | ✅ Working |
| partaboratory | `https://www.youtube.com/@partaboratory/videos` | CPA experiments | ✅ Working |
| nabormi_ai | `https://www.youtube.com/@nabormi_ai/videos` | AI automation | ✅ Working |

**Note:** Not all channels have a `/videos` tab (e.g. `@PartnerkinMedia`). Drop without `/videos` tab.

## Implementation Notes

- **Date parsing**: RSS feeds use multiple date formats (RFC 2822 `"Thu, 14 Jul 2026 12:00:00 +0000"`, ISO 8601 `"2026-07-14T12:00:00Z"`, simple date `"2026-07-14"`). Parse with a format list in `datetime.strptime`
- **HTML stripping**: `re.sub(r'<[^>]+>', '', text)` followed by entity decode (`&amp;`→`&`, `&lt;`→`<`, `&gt;`→`>`, `&quot;`→`"`, `&#39;`→`'`)
- **Timeout**: 15s per feed; feeds that hang are reported with error and skipped
- **Entry limit**: 10 entries per feed (15 for Partnerkin scraping); descriptions truncated to 500 chars
- **Date filtering**: CPA/Arbitrage entries are EXEMPT from the "remove old entries" filter. Even Partnerkin articles from 2022-2023 contain valuable case studies and must be kept
