# Weekly Network Reconnaissance — 2026-07-26

**Session Type:** Automated cron job (Sunday 09:00) — part of weekly portfolio review
**Skill:** multi-agent-researcher (dispatched by ai-financial-coach)
**Status:** ✅ DISPATCHED — 3 workers running in parallel
**Delegation ID:** `deleg_ac3479af`

---

## Dispatch Summary

| Worker | Target Network | Target Geos | Target Verticals | Status |
|--------|----------------|-------------|------------------|--------|
| Worker 1 | AdCombo | IN, BR, RU | gambling/sports, nutra, sweepstakes, gaming | 🟢 Running |
| Worker 2 | CPAlead | RU | gaming, utility, survey | 🟢 Running |
| Worker 3 | MaxBounty | US, CA | finance, nutra | 🟢 Running |

**Timeout:** 300s (5 minutes) per worker
**Expected Completion:** Within 5 minutes of dispatch

---

## Worker Briefs (Full)

### Worker 1: AdCombo Reconnaissance
```
GOAL: Profile CPA network AdCombo
CONTEXT:
  - Target geos: IN, BR, RU
  - Target verticals: gambling/sports, nutra, sweepstakes, gaming
ACCEPTANCE:
  - Offer count by vertical
  - Payout ranges per vertical
  - Conversion flow confirmed (CPA/CPL/CPI/CPS)
  - Restrictions documented (age, gender, creatives, incent)
  - Landing page URLs captured
  - Creative angles identified
  - Approval requirements (pre-landers, cloaking, etc.)
  - Payment terms (net-X, min payout, methods)
  - Reputation (shaves, bans, support quality)
  - Exclusive offers list
  - Account manager responsiveness
FORMAT: JSON with fields: network, verticals, offers[], terms, reputation, exclusives, am_quality, score
```

### Worker 2: CPAlead Reconnaissance
```
GOAL: Profile CPA network CPAlead
CONTEXT:
  - Target geos: RU
  - Target verticals: gaming, utility, survey
ACCEPTANCE: (same as above, focused on RU gaming/utility/survey)
```

### Worker 3: MaxBounty Reconnaissance
```
GOAL: Profile CPA network MaxBounty
CONTEXT:
  - Target geos: US, CA
  - Target verticals: finance, nutra
ACCEPTANCE: (same as above, focused on US/CA finance/nutra)
```

---

## Synthesis Rules (For When Results Return)

1. **Score each offer 1-10 on:** payout stability, conversion ease, creative freedom, geo fit
2. **Flag red flags:** shady network, cloaking required, unstable payouts
3. **Rank by expected ROI** = (payout × estimated_CR) / traffic_cost
4. **Output:** Ranked table + top 3 recommendations + risks

---

## Integration with Portfolio Review

Results will be used in next week's budget allocation:
- **$200 reserved** (20% of test budget) for top 3 researched offers
- Each offer gets ~$65 test budget
- If any shows ROI > 100% in 3 days → scale per budget allocation rules

---

## Notes for Future Sessions

- This dispatch pattern is now the standard for "find 3 new offers to test" weekly task
- Workers run in parallel — total wall time ~5 min vs 15 min sequential
- If delegate_task unavailable in cron env: log and fall back to manual web research
- Results should be saved to `cache/network_recon/` with timestamp for history