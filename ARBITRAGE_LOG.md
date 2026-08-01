---
name: arbitrage-log
description: "Auto-generated from ARBITRAGE_LOG.md"
trigger: "When user asks about ARBITRAGE_LOG concepts"
usage: arbitrage-log
Revisit: 2026-07-31
---

# Arbitrage Opportunity Scan Log

**Scan Date:** 2026-07-26 15:07 UTC
**Scanner:** arbitrage-sensors (cpa_scanner + gap_calculator)
**Threshold:** ROI > 50% (user-defined)
**Scan Mode:** Scheduled cron job (autonomous)

---

## Summary

| Metric | Value |
|--------|-------|
| Total Offers Scanned | 24 (8 networks) |
| Offers with Matching Traffic | 12 (RU geo only) |
| Gaps Found (ROI > 30%) | 6 |
| **Gaps Exceeding 50% ROI** | **5** |
| Highest ROI | 244.12% (Tinkoff Credit Card + Kadam) |
| Highest Daily Profit | $2,075/day |

---

## 🎯 Opportunities Exceeding 50% ROI

### 1. Tinkoff Credit Card (admitad) → Kadam (RU Finance)
- **Offer:** Кредитная карта Тинькофф (CPA, 1500 RUB payout, 65% approval)
- **Traffic:** Kadam RU Finance (CPC 8.5 RUB, CPM 120)
- **ROI:** 244.12%
- **Projected Profit:** $2,075/day (100 clicks/day assumption)
- **Confidence:** 20% ⚠️ **MOCK DATA - LOW CONFIDENCE**
- **CR:** 3% (finance CPA typical for push)
- **Restrictions:** no_incent, age_18+
- **Cache Age:** 23 days (stale — confidence halved per staleness policy)

### 2. Tinkoff Credit Card (admitad) → Facebook Ads (RU Finance)
- **Offer:** Same as above
- **Traffic:** Facebook RU Finance (CPC 18 RUB, CPM 350)
- **ROI:** 62.5%
- **Projected Profit:** $1,125/day
- **Confidence:** 20% ⚠️ **MOCK DATA - LOW CONFIDENCE**
- **Min Deposit:** $1,000

### 3. Raid Shadow Legends (admitad) → RichAds (RU Gaming)
- **Offer:** Игра Raid Shadow Legends (CPI, 120 RUB payout, 85% approval)
- **Traffic:** RichAds RU Gaming (CPC 4.5 RUB, CPM 80)
- **ROI:** 240%
- **Projected Profit:** $1,080/day
- **Confidence:** 100% ✅ **HIGH CONFIDENCE** (CR 15% for CPI gaming)
- **CR:** 15% (CPI gaming typical)
- **Restrictions:** no_incent, android_only
- **⚠️ CR WARNING:** Mock CR=15% is UNREALISTIC for push traffic. Realistic CR: 2.5% (push gaming). Real ROI would be significantly lower.

### 4. MoneyMan Microloan (cityads) → Kadam (RU Finance)
- **Offer:** Микрозайм MoneyMan (CPA, 950 RUB payout, 55% approval)
- **Traffic:** Kadam RU Finance (CPC 8.5 RUB, CPM 120)
- **ROI:** 78.26%
- **Projected Profit:** $665.25/day
- **Confidence:** 16% ⚠️ **MOCK DATA - LOW CONFIDENCE**
- **CR:** 2.9% (finance CPA)

### 5. Auto Insurance (cityads) → Kadam (RU Finance)
- **Offer:** Страховка авто РасСтрехование (CPS, 650 RUB payout, 70% approval)
- **Traffic:** Kadam RU Finance (CPC 8.5 RUB, CPM 120)
- **ROI:** 82%
- **Projected Profit:** $697/day
- **Confidence:** 24% ⚠️ **MOCK DATA - LOW CONFIDENCE**
- **CR:** 3.4% (finance CPS)

---

## 📊 All Scanned Offers (24 Total)

### Admitad (3 offers)
| Offer | Vertical | Geo | Payout | Type | CR | Status |
|-------|----------|-----|--------|------|-----|--------|
| Тинькофф Кредитка | finance | RU | 1500 RUB | CPA | 3% | ✅ 3 gaps >50% |
| Raid Shadow Legends | gaming | RU | 120 RUB | CPI | 15% | ✅ 1 gap >50% |
| Keto Slim | nutra | RU | 850 RUB | CPS | 3.8% | ⚠️ No traffic match |

### CityAds (2 offers)
| Offer | Vertical | Geo | Payout | Type | CR | Status |
|-------|----------|-----|--------|------|-----|--------|
| MoneyMan | finance | RU | 950 RUB | CPA | 2.9% | ✅ 1 gap >50% |
| РасСтрехование Авто | finance | RU | 650 RUB | CPS | 3.4% | ✅ 1 gap >50% |

### ActionPay (1 offer)
| Offer | Vertical | Geo | Payout | Type | CR | Status |
|-------|----------|-----|--------|------|-----|--------|
| Bybit Registration | crypto | RU | 450 RUB | CPL | 3.3% | ❌ No traffic match |

### AdCombo (5 offers - 2 RU, 3 INTL)
| Offer | Vertical | Geo | Payout | Type | CR | Status |
|-------|----------|-----|--------|------|-----|--------|
| India Cricket PWA | gambling | IN | $4.5 | CPI | 12% | ❌ No traffic match |
| Brazil Nutra | nutra | BR | $28 | CPS | 3.5% | ❌ No traffic match |
| Просталин | nutra | RU | 1200 RUB | CPS | 3.3% | ⚠️ Nutra traffic exists (Kadam/TikTok) |
| iPhone 15 Sweepstakes | sweepstakes | RU | 45 RUB | CPL | 25% | ❌ No traffic match |
| World of Tanks | gaming | RU | 80 RUB | CPI | 18% | ✅ RichAds gaming exists |

### CPALead (3 offers)
| Offer | Vertical | Geo | Payout | Type | CR | Status |
|-------|----------|-----|--------|------|-----|--------|
| US Gaming Content Locker | gaming | US | $1.2 | CPI | 18% | ❌ No US traffic match |
| Dating Email Submit | dating | US | $2.5 | CPL | 8% | ❌ No US traffic match |
| Game Cheats Unlock | gaming | RU | $0.85 | CPI | 50% | ❌ No traffic match (incent allowed) |
| VPN Unlimited | utility | RU | $1.2 | CPI | 45% | ❌ No traffic match |
| Gaming Survey | survey | RU | $2.5 | CPL | 30% | ❌ No traffic match |

### MaxBounty (3 offers)
| Offer | Vertical | Geo | Payout | Type | CR | Status |
|-------|----------|-----|--------|------|-----|--------|
| Canada Credit Card | finance | CA | $45 | CPA | 4.5% | ❌ No CA traffic match |
| US Personal Loan | finance | US | $45 | CPL | 4% | ❌ No US traffic match |
| CA Credit Card | finance | CA | $38 | CPA | 3.5% | ❌ No CA traffic match |
| US Diet Supplement | nutra | US | $55 | CPS | 4% | ❌ No US traffic match |

### CPATrend (3 offers)
| Offer | Vertical | Geo | Payout | Type | CR | Status |
|-------|----------|-----|--------|------|-----|--------|
| DE iPhone 15 Sweepstakes | sweepstakes | DE | $3.8 | CPI | 15% | ❌ No DE traffic match |
| Mamba Dating RU | dating | RU | 180 RUB | CPL | 20% | ❌ No dating traffic match |
| Joint Pain Cream | nutra | RU | 950 RUB | CPS | 3.7% | ⚠️ Nutra traffic exists (Kadam/TikTok) |
| Samsung Galaxy S24 | sweepstakes | RU | 55 RUB | CPL | 30% | ❌ No traffic match |

---

## ⚠️ Critical Notes

### Data Quality
- **All CPA offers are MOCK DATA** (no API keys configured for any network)
- **All traffic costs are MOCK DATA** (hardcoded in gap_calculator.py)
- **Only RU geo has traffic cost data** — 12 of 24 offers have no matching traffic
- **Confidence scores** reflect mock data quality:
  - Finance offers (CR ~3%): 16-24% confidence
  - Gaming CPI (CR 15%): 100% confidence (but CR itself is hypothetical)
  - Nutra/Sweepstakes/Dating: No traffic match → 0 confidence

### Realistic CR Benchmarks (from skill references, 2026-07-25)

| Vertical | Format | Low CR | **Realistic CR** | Optimized CR | Mock CR Used |
|----------|--------|--------|------------------|--------------|--------------|
| Gaming CPI | Push (RichAds) | 1.0% | **2.5%** | 5.0% | 15% ❌ UNREALISTIC |
| Finance CPA | Push (Kadam) | 0.5% | **1.0%** | 2.0% | 3% ⚠️ Optimistic |
| Finance CPL | Push (Kadam) | 1.0% | **2.0%** | 4.0% | — |
| Nutra CPS | Push (Kadam) | 0.3% | **0.8%** | 1.5% | 3.8% ❌ UNREALISTIC |
| Sweepstakes CPI | Push/Pop | 2.0% | **4.0%** | 8.0% | 15-30% ❌ UNREALISTIC |
| Dating CPL | Push/Pop | 1.0% | **2.0%** | 4.0% | 20% ❌ UNREALISTIC |

**→ All ROI projections are UPPER BOUNDS. Real-world ROI will be significantly lower.**

### Data Staleness
- **Cache age:** 23 days (last updated 2026-07-03)
- **Staleness policy:** >7 days = halve confidence, >14 days = critically stale, >30 days = suppress HIGH+ alerts
- **Current status:** All mock data is **CRITICALLY STALE** — confidence scores should be halved again

### Missing Traffic Sources (Need Implementation)
- **US traffic:** Facebook, Google, TikTok, PropellerAds
- **IN traffic:** InMobi, Glance, Facebook India
- **BR traffic:** Facebook Brazil, Google Brazil
- **CA/DE traffic:** Local ad networks
- **Dating vertical:** Push, Pop, Native
- **Sweepstakes vertical:** Pop, Push, Redirect
- **Crypto vertical:** Native, Push, Social
- **Survey/Utility verticals:** Content lockers, Incent networks

---

## 📋 Recommended Actions

| Priority | Action | Effort |
|----------|--------|--------|
| **CRITICAL** | Add real API keys for at least 1 CPA network (Admitad/CityAds) | Medium |
| **CRITICAL** | Implement real traffic cost APIs (Kadam, RichAds, Facebook) | High |
| **HIGH** | Add traffic costs for US, IN, BR, CA, DE geos | Medium |
| **HIGH** | Add traffic costs for dating, sweepstakes, crypto, utility verticals | Medium |
| **MEDIUM** | Apply realistic CR benchmarks to mock data (cap at industry max) | Low |
| **MEDIUM** | Add data staleness detection (>7 days = halve confidence) | Low |
| **LOW** | Implement Creative Radar (FB Ad Library, TikTok Creative Center) | High |

---

## 🔄 Next Scan
- **Scheduled:** Every 30 min (fast sensor) / 60 min (medium sensor)
- **Trigger:** This cron job runs on schedule
- **Alert Threshold:** ROI > 50% (this log filters for >50%)

---

*Generated by Hermes arbitrage-sensors skill*
*Cache files: cache/cpa_offers.json, cache/arbitrage_gaps.json*
*CPC Benchmarks: references/2026-07-25-web-research-cpc-benchmarks.md*