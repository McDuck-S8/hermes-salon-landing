# Medium Sensor Run Findings — 2026-07-23

## Execution Summary
- **Run time**: 2026-07-23T05:18Z (cron-triggered)
- **Script**: `scripts/medium_sensor_run.py`
- **Frequency**: Hourly (MEDIUM tier)
- **Networks scanned**: 8 (admitad, cityads, actionpay, ad1, adcombo, cpa_lead, maxbounty, cpa_trend)
- **Total offers**: 24 (12 original + 12 new from 4 target networks)

## Results

### Arbitrage Gaps Found: 9
| Offer | Network | Traffic | Geo | Vertical | ROI | $/day | Conf | Score | Level |
|-------|---------|---------|-----|----------|-----|-------|------|-------|-------|
| adm_002 | admitad | richads | RU | gaming | 240% | 1080 | 1.00 | **80** | 🔴 CRITICAL |
| adm_001 | admitad | kadam | RU | finance | 244% | 2075 | 0.20 | 18 | 📝 LOW |
| adm_001 | admitad | facebook | RU | finance | 63% | 1125 | 0.20 | 8 | 📝 LOG |
| cit_002 | cityads | kadam | RU | finance | 82% | 697 | 0.24 | 7 | 📝 LOG |
| acb_001 | adcombo | kadam | RU | nutra | 65% | 780 | 0.17 | 5 | 📝 LOG |
| cit_001 | cityads | kadam | RU | finance | 78% | 665 | 0.16 | 5 | 📝 LOG |
| adm_001 | admitad | google | RU | finance | 33% | 725 | 0.20 | 4 | 📝 LOG |
| cpt_002 | cpa_trend | kadam | RU | nutra | 41% | 487 | 0.18 | 2 | 📝 LOG |
| acb_001 | adcombo | tiktok | RU | nutra | 32% | 480 | 0.17 | 2 | 📝 LOG |

## Key Findings

### 1. Only 1 CRITICAL Alert (Score 80)
- **Signal**: Raid Shadow Legends (adm_002, admitad) + RichAds RU gaming
- **ROI**: 240% | **Profit**: $1080/day | **Confidence**: 1.0 (high CR CPI offer)
- **Telegram delivery**: SUCCESS (plain text format, Exfil-Guard safe)

### 2. Extended Networks (4 New Targets) Added
- **AdCombo**: India Cricket PWA (IN, gambling/sports), Brazil Nutra (BR, nutra), WoT (RU, gaming)
- **CPAlead**: Game Cheats (RU, gaming), VPN (RU, utility), Gaming Survey (RU, survey)
- **MaxBounty**: US Loan (US, finance), CA Credit Card (CA, finance), Diet Trial (US, nutra)
- **CPATrend**: Mamba Dating (RU, dating), Joint Cream (RU, nutra), Samsung S24 Sweep (RU, sweepstakes)

### 3. Creative Radar Gap Confirmed
- Listed in `always-on-agent` as 6h sensor but **not implemented**
- Requires `browser-automation` + BrowserOS MCP for authenticated JS-rendered scraping
- Web search returns landing pages, not creatives

### 4. Mock Data Confidence Formula Issue
- Formula: `min(approval_rate × cr × 10, 1.0)` in `gap_calculator.py:192`
- Finance vertical CR ~0.03 → confidence 0.16-0.24 (heavily penalized)
- Gaming CPI CR=0.15, approval=0.85 → confidence 1.0
- **All mock-data alerts = hypotheses requiring live validation**

### 5. FAST Sensor Alignment Needed
- MEDIUM uses 0-100 scale (Impact × Urgency × Confidence / 10)
- FAST uses legacy 0-1000 scale (threshold ≥70 CRITICAL only)
- **Action**: Update `fast_sensor_run.py` to 0-100 scale with HIGH+ threshold ≥50

## Network Health: All 8 Healthy
- 0 postback delays, 0 offer pauses, approval rates 0.55-0.78

## Finance Baselines
- Revenue 30d: $0.00 | Spend: $0.01 | Net: -$0.01
- 1 active scheme | 0 pending withdrawals | Tax pending: $0.00

## Files
- Script: `scripts/medium_sensor_run.py`
- State: `cache/always_on_state.json`
- Gaps cache: `cache/arbitrage_gaps.json` (234 entries)
- Offers cache: `cache/cpa_offers.json` (24 entries)