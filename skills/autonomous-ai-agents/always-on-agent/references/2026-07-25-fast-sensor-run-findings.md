# Fast Sensor Run Findings — 2026-07-25

## Execution Context
- **Trigger**: Scheduled cron job (every 30 min) — `always-on-fast` 
- **Script**: `skills/autonomous-ai-agents/always-on-agent/scripts/fast_sensor_run.py`
- **Run time**: 2026-07-25T19:35:13Z / 2026-07-25T19:36:01Z (two executions)

## Key Findings

### 1. Cron Job Path Discrepancy (CONFIRMED)
**Problem**: Cron job `2e04bc051ee0` invokes `scripts/always_on_fast_fixed.py` which imports `scripts.arbitrage_sensors` — **module does not exist**.

**Correct path**: `skills/autonomous-ai-agents/always-on-agent/scripts/fast_sensor_run.py`

**Root cause**: Cron job created with wrong script reference. The skill script uses proper imports:
- `finance_core` from `HERMES_HOME/scripts`
- `gap_calculator` from `skills/finance/arbitrage-sensors/scripts`

### 2. Alert Generation — 1 CRITICAL Delivered

| Signal | Score | Level | Delivered |
|--------|-------|-------|-----------|
| adm_002 (Raid Shadow Legends) + richads gaming RU | 70 | 🔴 CRITICAL | ✅ Telegram |

**Alert format (plain text, Exfil-Guard safe):**
```
CRITICAL adm_002 admitad + richads gaming RU
ROI: 240p0pct | profit: 1080 perday | Conf: 1p00 | Score: 70
ACTION: Test richads RU gaming with 50 budget
```

**Telegram delivery**: ✅ Success to chat 737433175 via `send_short_alert.py`

### 3. Scoring Alignment Verified
- **Skill script**: `Impact(0-10) × Urgency(0-10) × Confidence(0-10) / 10` → 0-100 scale
- **Thresholds**: ≥70 CRITICAL, ≥50 HIGH (matches MEDIUM sensor spec)
- **Root script (broken)**: `roi * confidence * 2` → unbounded, produced scores 480, 98

### 4. Mock Data Limitations (Reiterated)
- All traffic costs: MOCK (no API keys)
- All CPA offers: MOCK (cached from 2026-07-03, 22 days stale)
- Confidence formula: `min(approval_rate * cr * 10, 1.0)` → CR=15% gaming CPI → confidence 1.0
- **Reality check**: 15% CR for push gaming CPI is unrealistic (realistic: 2.5-5%)
- **All alerts = hypotheses requiring live validation**

### 5. Finance Baselines (Live Data)
- Revenue 30d: $1,492.05
- Spend 30d: $200.01  
- Net 30d: $1,292.04
- 3 active schemes, 4 pending withdrawals, $59.68 tax pending
- **First sensor run with real positive P&L** (see `2026-07-24-revenue-breakthrough.md`)

### 6. Network Health
- admitad, cityads, actionpay: all HEALTHY (postback 0min, 0 pauses)
- Mock data — no real API monitoring

## Action Items

1. **Fix cron job `2e04bc051ee0`** — update to call skill script:
   ```bash
   python skills/autonomous-ai-agents/always-on-agent/scripts/fast_sensor_run.py
   ```

2. **Add realistic CR benchmarks** to mock data (per `arbitrage-sensors` skill Pitfalls):
   - Gaming CPI push: 2.5% realistic (not 15%)
   - Finance CPA push: 1.0% realistic (not 3%)
   - This will lower confidence scores to realistic levels

3. **Implement cache staleness detection** — offers cache >7 days should halve confidence

4. **Creative Radar** — still not implemented (requires browser-automation + BrowserOS MCP)

## Related References
- `2026-07-24-fast-sensor-cron-run-findings.md` — root vs skill script discrepancy
- `2026-07-24-revenue-breakthrough.md` — first real revenue detected
- `arbitrage-sensors/references/2026-07-25-web-research-cpc-benchmarks.md` — real CPC rates