# Knowledge Filter Test Results — 2026-07-18

## Test Data
- **RSS cache:** 60 articles from 9 feeds (partnerkin, affiliatefix, reddit_affiliatemarketing, reddit_crypto, reddit_passive_income, reddit_entrepreneur, openai_blog, anthropic_rsshub, hackernews)
- **YouTube cache:** 10 videos from 2 channels (easy_traff, partnerkin)

## Results Summary

| Source | Total | Passed | Rejected | Pass Rate |
|--------|-------|--------|----------|-----------|
| RSS (all feeds) | 60 | 18 | 42 | 30% |
| YouTube (2 channels) | 10 | 4 | 6 | 40% |
| **TOTAL** | **70** | **22** | **48** | **31%** |

## Key Passed Articles (Examples)

### RSS — Gambling/Arbitrage
- "Большая сетка iGaming-сайтов с доходом в $225 000" (partnerkin) — HS:65, AA:50, SP:62
- "ZixiPay: грандиозный скам 2026 года" (partnerkin) — HS:65, AA:85, SP:68
- "Как получить средний чек 75$+ и до 1200% RD в Узбекистане" (partnerkin) — HS:75, AA:100, SP:66
- "EVADAV TRAFFIC GROUP – Performance..." (affiliatefix) — HS:65, AA:80, SP:68

### RSS — Crypto/Fintech
- "Daily Crypto Discussion" (reddit_crypto) — HS:65, AA:70, SP:66
- "TRUMP looks like a textbook rug pull" (reddit_crypto) — HS:65, AA:65, SP:55
- "FTX Customers to Receive Up to 120%" (reddit_crypto) — HS:65, AA:65, SP:38
- "Zero trading fees on Bitfinex" (reddit_crypto) — HS:100, AA:65, SP:68

### YouTube
- "Рекламодатель VS медиабайер: кто отвечает за качество трафика" — HS:60, AA:50, SP:48
- "The Hottest SEO Traffic Trends in 2026" — HS:60, AA:50, SP:54
- "Арбитраж трафика RIP — не лей, пока не посмотришь" — HS:90, AA:50, SP:50
- "SEO in iGaming: Why 95% of Websites Won't Earn" — HS:60, AA:70, SP:45

## Key Rejected Patterns

### Stage 1 (Human-Source) — Hard Blocks
- Facebook/Google Ads content → "HARD BLOCK: Google Ads API required"
- Selfie/video verification guides → "HARD BLOCK: Selfie/FaceID required"
- Budget/investment required articles → penalty applied (not hard block)

### Stage 1 — Low Score (HS:50 base, threshold 60)
- Generic intros ("Hi from Harsha", "Looking For casino Traffic")
- Broad questions without actionable content
- Non-arbitrage AI/tech news (OpenAI, Anthropic, HN)

### Stage 2 (Audience-Analyzer) — Low Relevance
- Articles with no vertical keywords (gambling/fintech/content)
- No geo match for target geos (IN, BR, MX, LATAM, RU/CIS)
- Generic marketing discussions without CPA/arbitrage angle

### Stage 3 (Skill-Pathfinder) — Low Novelty
- Similar to existing KC entries (similarity > 50%)
- YouTube videos similar to previously indexed ones from same channel

## Threshold Tuning Applied

| Filter | Original | Adjusted | Reason |
|--------|----------|----------|--------|
| Human-Source | 60 | 60 | Kept — good balance |
| Audience-Analyzer | 50 | 30 | Too strict; 1 keyword hit sufficient |
| Skill-Pathfinder | 70 | 50 | Too strict; allow near-duplicates with new angles |

## Decision Logic Change

**Original:** All three stages must pass (AND logic)
**Changed:** Human-Source MUST pass + (Audience OR Pathfinder) pass
- Rationale: Some articles are novel (high SP) but not yet matched to vertical; others match vertical but are similar to existing. Both valuable.

## External KC Growth

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Total external sources | 44 | 82 | +38 |
| External % of total KC | 14% | ~27% | +13pp |
| New RSS sources | 0 | 6 feeds | +6 |
| New YouTube sources | 2 | 2 | — |

## Lessons Learned

1. **Human-Source boost keywords are critical** — without them, most arbitrage articles score 50 (base) and fail. Added explicit Russian keywords (арбитраж, ставки, букмекер, etc.)

2. **Audience-Analyzer needs ≥1 keyword hit, not ≥2** — many relevant articles mention only "traffic" + "betting" = 2 hits but in different contexts. Single strong keyword (cricket, 1xbet, P2P) should suffice.

3. **Skill-Pathfinder similarity threshold too aggressive** — Jaccard on keywords gives high similarity for same-domain articles. Lowered to 50% novelty threshold.

4. **Hard blocks should be ONLY truly blocking items** — KYC, passport, selfie, Google Gemini, Playwright, Chrome headless. Budget/legal/paid-API should be penalties, not blocks.

5. **RSS parser needs more feeds** — Added 6 Reddit feeds (PPC, adtech, growthhacking, digital_marketing, SEO, passive_income) to increase volume.

6. **YouTube content needs better extraction** — Currently only title+duration. Should fetch descriptions/transcripts for better filtering.

## Next Steps

- [ ] Add cron job for knowledge_filter_cron.py (every 60-120min)
- [ ] Fetch YouTube descriptions via yt-dlp --get-description
- [ ] Add more Reddit feeds: r/affiliatefix, r/mediabuying, r/traffic
- [ ] Monitor external KC count toward 100+ target (currently 82)
- [ ] Tune thresholds based on 3-day conversion data