# Pinterest Automation Pattern (2026-06-25)

## What It Is
Automated pinning to Pinterest at scale (100+ pins/day) using free tools. Drives traffic to website/affiliate links.

## The Scheme
1. Get free images from Pexels API (keyword-based)
2. AI generates titles/descriptions (Google Gemini)
3. Bulk post to Pinterest (Selenium/Puppeteer)
4. Each pin links to website/affiliate offer
5. Pinterest algorithm distributes pins → traffic → conversions

## Tools Found
- **bot-pinterest-ai** (GitHub): AI + GitHub Actions, 24/7 free. BUT requires license key (obfuscated code).
- **PinterestBulkPostBot** (GitHub): Selenium-based, bulk upload, CSV import, MIT license.
- **Custom bot** (pinterest_bot.py): Written in this session. No license needed.

## Required APIs
- Pexels API: Free (pexels.com/api) — 200 requests/hour
- Google Gemini API: Free tier — ai.google.dev
- Pinterest account + cookies export

## Monetization
- Affiliate links in pin destination URLs
- Drive traffic to blog/website with ads
- CPA offers (travel, fashion, home decor)
- Etsy/Amazon affiliate programs

## Key Insights
- Pinterest is visual search engine, not social media
- Pins have long lifecycle (months/years of traffic)
- Low competition compared to Google/Meta
- Free traffic source (no ad spend needed)
- Works in Russia/Crimea (no restrictions)

## Implementation Status
- Cloned bot-pinterest-ai (requires license)
- Created pinterest_bot.py (Python, no license)
- Created keywords_ru.txt (Russian keywords)
- NEED: Pexels API key, Gemini API key, Pinterest cookies

## Files
- projects/bot-pinterest-ai/pinterest_bot.py
- projects/bot-pinterest-ai/keywords_ru.txt
- projects/bot-pinterest-ai/config.json
