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

### Alerts Emitted (HIGH+ ≥ 50): **1 CRITICAL**
- **adm_002 (Raid Shadow Legends) + RichAds RU gaming** — Score 80
- Telegram delivery: **SUCCESS** (plain text, Exfil-Guard safe format)

### Network Health: All 8 Healthy
- 0 postback delays, 0 offer pauses, approval rates 0.55–0.78

### Finance Baselines
- Revenue 30d: $0.00
- Spend 30d: $0.01
- Net 30d: -$0.01
- Active schemes: 1
- Pending withdrawals: 0

## Key Issues Identified

1. **Creative Radar not implemented** — Requires `browser-automation` + BrowserOS MCP
2. **Mock data confidence low** — Only high-CR offers (gaming CPI) score Conf 1.0; finance/nutra Conf 0.16–0.24
3. **FAST sensor misaligned** — Uses 0-1000 scale, only CRITICAL threshold; needs 0-100 with HIGH+ ≥50
4. **Target networks mock-only** — AdCombo, CPAlead, MaxBounty, CPATrend have mock data in medium_sensor_run.py but not in cpa_scanner.py
5. **Deep-dive dispatch unavailable** — `delegate_task` not accessible in cron environment

## Recommendations
1. Add mock offers for 4 target networks to `cpa_scanner.py` for consistency
2. Implement Creative Radar with browser-automation workers
3. Align FAST sensor scoring to 0-100 scale with HIGH+ threshold
4. Ensure `delegate_task` available for deep-dive dispatch
5. Validate CRITICAL alert (Raid+RichAds) with live test before deployment