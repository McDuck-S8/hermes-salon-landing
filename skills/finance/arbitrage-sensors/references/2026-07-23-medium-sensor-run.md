# Medium Sensor Run Findings — 2026-07-23 (This Session)

## Summary
- **Run type**: MEDIUM (hourly)
- **Sensors executed**: CPA Offer Scanner, Gap Calculator
- **Sensor NOT executed**: Creative Radar (NOT IMPLEMENTED — requires `browser-automation` + BrowserOS MCP)
- **Duration**: ~10 seconds
- **API keys configured**: NONE (all mock data)

## Results

### CPA Offer Scanner
- Networks scanned: Admitad, CityAds, ActionPay, Ad1
- Offers found: 6 total, 0 new (already cached from previous runs)
- Data source: Mock (no ADMITAD_API_KEY, CITYADS_API_KEY, ACTIONPAY_API_KEY, AD1_API_KEY)
- **Target networks from prompt (AdCombo, CPAlead, MaxBounty, CPATrend)**: Already present in cache from fast sensor run (6 new offers added), but not scanned this run since scanner only has 4 networks configured

### Gap Calculator
- Offers processed: 12 (6 original + 6 new from fast run)
- New arbitrage gaps: 6 (deduplicated to 6 unique offer+traffic combos)
- Total gaps in cache: 210 (accumulated across runs)

### Signal Scoring (Formula: Score = Impact × Urgency × Confidence / 10, 0-100 scale)

| Level | Score | Offer | Network | Traffic | ROI | Profit/day | Confidence |
|-------|-------|-------|---------|---------|-----|------------|------------|
| 🔴 CRITICAL | 70 | adm_002 (Raid Shadow Legends) | Admitad | RichAds RU gaming | 240% | $1,080 | **1.0** ⭐ |
| 🔵 LOW | 20 | adm_001 (Tinkoff Credit Card) | Admitad | Kadam RU finance | 244% | $2,075 | 0.20 |
| ⚪ LOG | 7 | adm_001 | Admitad | Facebook RU finance | 62.5% | $1,125 | 0.20 |
| ⚪ LOG | 3 | adm_001 | Admitad | Google RU finance | 33% | $725 | 0.20 |
| ⚪ LOG | 4 | cit_001 (MoneyMan) | CityAds | Kadam RU finance | 78% | $665 | 0.16 |
| ⚪ LOG | 6 | cit_002 (Auto Insurance) | CityAds | Kadam RU finance | 82% | $697 | 0.24 |

**Thresholds**: ≥70 CRITICAL, ≥50 HIGH, ≥30 MEDIUM, ≥10 LOW, <10 LOG

## Key Findings

### 1. Only ONE high-confidence signal: Raid Shadow Legends + RichAds
- Confidence 1.0 comes from high mock CR (15%) → `0.85 × 0.15 × 10 = 1.275 → capped at 1.0`
- All other offers have CR 2.9–3.8% → confidence 0.16–0.24
- **This is a mock data artifact** — formula penalizes low-CR offers

### 2. Creative Radar is LISTED but NOT IMPLEMENTED
- `always-on-agent` SKILL.md lists "Creative Radar" as a 6h sensor
- `arbitrage-sensors` SKILL.md confirms: "Creative radar... **not implemented in this skill**"
- Web search for `site:facebook.com/ads/library` returns landing pages, NOT creatives
- **Requirement**: Deploy `browser-automation` skill + BrowserOS MCP for authenticated JS-rendered scraping

### 3. Multi-agent researcher dispatch successful
- 1 worker dispatched for CRITICAL signal (delegation_id: `deleg_b996aaf2`)
  - Deep dive Raid Shadow Legends (Admitad adm_002): verify payout history, cap changes, creative requirements, AM contact, validate RichAds gaming RU CPC/CPM for live testing
- Timeout set: 300s (5 min) per worker
- On timeout: redispatch with simplified brief + explicit `browser-automation` requirement

### 4. State persisted
- File: `cache/always_on_state.json`
- Contains: last_run, sensors_executed, signals_scored, critical_signals with DISPATCHED_DEEP_DIVE status

### 5. Telegram Delivery
- **Skipped**: No `TELEGRAM_BOT_TOKEN` environment variable configured
- When configured: Use `format_short_alert.py` for <8 line plain-text messages (Exfil-Guard safe)

## Actions Required

| Priority | Action | Blocked By |
|----------|--------|------------|
| 🔴 CRITICAL | Configure CPA network API keys (Admitad, CityAds, ActionPay, Ad1) | Network access, AM contacts |
| 🔴 CRITICAL | Deploy `browser-automation` + BrowserOS MCP for Creative Radar | BrowserOS MCP setup |
| 🟠 HIGH | Configure traffic source APIs (FB Marketing API, TikTok Ads API, Google Ads API) | API access, approval |
| 🟠 HIGH | Adjust confidence formula or add manual override for "known good" mock offers | Code change in gap_calculator.py:192 |
| 🟢 MEDIUM | Split `cpa_offers.json` cache per subsystem (scanner, gap_calc, TG poster, TG bot) | Refactor, see Pitfalls in arbitrage-sensors |
| 🟢 MEDIUM | Add mock entries for AdCombo, CPAlead, MaxBounty, CPATrend to cpa_scanner.py NETWORKS | Code change |

## Confidence Assessment
- **Raid + RichAds (Score 70)**: Confidence 1.0 (CR=0.15, approval=0.85) — high quality mock, still needs live validation
- **All other gaps**: Confidence 0.16–0.24 — all hypotheses requiring live validation
- **Rule**: All mock-data alerts = hypotheses requiring live validation before deploy