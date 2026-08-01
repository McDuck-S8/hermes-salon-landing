# Sensor Run Findings — 2026-07-23 23:06 UTC

## Context
Medium sensor run (hourly) executed via always-on-agent cron. Both `cpa_scanner.py` and `gap_calculator.py` ran with mock data (no API keys configured).

## Key Findings

### 1. Mock Data Confidence Formula Penalizes Low-CR Offers
**File**: `scripts/gap_calculator.py:192`
```python
confidence = min(offer.approval_rate * offer.cr * 10, 1.0)
```

| Offer | CR | Approval | Confidence |
|-------|-----|----------|------------|
| Raid Shadow Legends (gaming) | 0.15 | 0.85 | **1.0** |
| Tinkoff Credit Card (finance) | 0.03 | 0.65 | 0.20 |
| MoneyMan Microloan (finance) | 0.029 | 0.55 | 0.16 |
| Auto Insurance (finance) | 0.034 | 0.70 | 0.24 |

**Problem**: Formula `approval_rate × cr × 10` means offers with CR < 0.1 get confidence < 1.0. Gaming offers typically have higher CR (installs) than finance (leads/sales), creating systematic bias.

**Options**:
1. Normalize by vertical (gaming CR benchmark vs finance CR benchmark)
2. Add manual override flag for "validated mock offers"
3. Use network-reported EPC/CR directly instead of derived confidence

### 2. Cache File Contention Confirmed
`cache/cpa_offers.json` shared by 4 systems with incompatible schemas:
1. CPA Scanner (CPAOffer dataclass)
2. Gap Calculator (reads CPAOffer)
3. TG Channel Poster (simplified `{"offers": [{"id", "title", "description", "url"}]}`)
4. CPA Telegram Bot (same simplified schema)

**Symptom observed**: After TG poster/bot writes, scanner/gap_calc crash with `AttributeError: 'str' object has no attribute 'get'`

**Fix in place** (gap_calculator.py:134-135):
```python
raw = json.loads(offers_cache.read_text(encoding="utf-8"))
offers = raw.get("offers", raw) if isinstance(raw, dict) else raw
```

**Long-term**: Separate cache files per subsystem.

### 3. Creative Radar Sensor NOT Implemented
- Listed in `always-on-agent` SKILL.md as 6h sensor
- Not implemented in `arbitrage-sensors` skill
- Web search fails: `site:facebook.com/ads/library` returns landing pages
- **Requirement**: `browser-automation` + BrowserOS MCP for authenticated scraping

### 4. Gap Calculator Event Emission Works
- Events emitted via `event_bus.emit("arbitrage_gap_found", payload)`
- 6 new gaps emitted in this run (total 126 in cache)
- No downstream consumers triggered (0 jobs) — expected, orchestrator handles scoring

### 5. Multi-Agent Researcher Integration Verified
- 3 workers dispatched for CRITICAL signals
- Delegation ID: `deleg_b29f4072`
- Timeout: 300s with redispatch strategy on timeout
- Workers require `browser-automation` for FB/TikTok creative scraping

## Recommended Code Changes

### gap_calculator.py
1. **Confidence formula**: Add vertical normalization or manual override
2. **Cache loading**: Already format-agnostic ✓
3. **Event payload**: Add `signal_level` (CRITICAL/HIGH/MEDIUM/LOG) and `score` fields

### cpa_scanner.py
1. **Cache separation**: Write to `cache/cpa_offers_scanner.json` instead of shared file
2. **Hash tracking**: Already implemented ✓

### New file needed
- `scripts/traffic_cost_monitor.py` — for 30min fast sensor (currently mock only)
- `scripts/network_health_monitor.py` — for 1h medium sensor (currently mock only)