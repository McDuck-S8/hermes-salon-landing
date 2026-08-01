---
name: finance-core
description: "Core finance ledger for autonomous arbitrage agent: P&L, Cash Flow, Unit Economics, Tax Ledger, Withdrawal Tracker. SQLite backend, integrates with autonomous_agent and arbitrage-execution."
version: 1.0.0
author: Hermes
metadata:
  hermes:
    tags: [finance, pnl, cash-flow, unit-economics, tax, withdrawal, arbitrage]
    trigger: auto-loaded by autonomous_agent.py
---

# Finance Core — Autonomous Arbitrage Ledger

## Purpose
Single source of financial truth for autonomous agent. Tracks every spend, revenue, withdrawal, tax accrual per scheme. Enables finance-aware decisions in autonomous agent.

## Database Schema (cache/finance_core.db)

```sql
CREATE TABLE finance_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    event_type TEXT NOT NULL,           -- spend, revenue, withdrawal, withdrawal_received, tax_accrual, tax_paid, fee, refund
    amount_usd REAL NOT NULL,
    amount_rub REAL NOT NULL,
    usd_rate REAL NOT NULL,
    cost_center TEXT,                   -- traffic, tools, infrastructure, outsource, content, other
    revenue_stream TEXT,                -- cpa_network, affiliate, own_product, traffic_sale, other
    scheme_name TEXT,                   -- links to ARBITRAGE_WORKSHOP.md scheme
    network TEXT,                       -- CPAGrip, OGAds, Admitad, etc.
    offer_name TEXT,
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    utm_content TEXT,
    click_id TEXT,
    withdrawal_method TEXT,
    fee_usd REAL DEFAULT 0,
    status TEXT DEFAULT 'pending',      -- pending, confirmed, failed, cancelled
    tax_accrued_usd REAL DEFAULT 0,
    notes TEXT,
    source TEXT DEFAULT 'manual',       -- manual, auto_poster, arbitrage_execution, cpa_webhook
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_finance_ts ON finance_events(ts);
CREATE INDEX idx_finance_type ON finance_events(event_type);
CREATE INDEX idx_finance_scheme ON finance_events(scheme_name);
CREATE INDEX idx_finance_network ON finance_events(network);
CREATE INDEX idx_finance_status ON finance_events(status);

CREATE TABLE usd_rates (
    date TEXT PRIMARY KEY,
    rate REAL NOT NULL,
    source TEXT DEFAULT 'cbr'
);

CREATE TABLE tax_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE scheme_unit_economics (
    scheme_name TEXT PRIMARY KEY,
    total_spend_usd REAL DEFAULT 0,
    total_revenue_usd REAL DEFAULT 0,
    total_leads INTEGER DEFAULT 0,
    total_conversions INTEGER DEFAULT 0,
    cpc_usd REAL DEFAULT 0,
    ctr REAL DEFAULT 0,
    cr REAL DEFAULT 0,
    epc_usd REAL DEFAULT 0,
    roi_pct REAL DEFAULT 0,
    payback_days REAL DEFAULT 0,
    status TEXT DEFAULT 'testing',
    last_calculated TEXT
);
```

## Core API (Python)

```python
from scripts.finance_core import FinanceCore, FinanceEvent, EventType

fc = FinanceCore()

# Log spend (traffic, tools, infra)
fc.add_event(FinanceEvent(
    event_type=EventType.SPEND,
    amount_usd=50.0,
    cost_center="traffic",
    scheme_name="Content-Locking-CPA",
    network="CPAGrip",
    click_id="abc123",
    notes="TikTok ads test"
))

# Log revenue (CPA conversion)
fc.add_event(FinanceEvent(
    event_type=EventType.REVENUE,
    amount_usd=25.0,
    revenue_stream="cpa_network",
    scheme_name="Content-Locking-CPA",
    network="CPAGrip",
    offer_name="Free V-Bucks",
    utm={"source": "tiktok", "medium": "organic", "campaign": "vbucks_free"},
    source="arbitrage_execution"
))

# Log withdrawal request
fc.add_event(FinanceEvent(
    event_type=EventType.WITHDRAWAL,
    amount_usd=200.0,
    scheme_name="Content-Locking-CPA",
    network="CPAGrip",
    withdrawal_method="Payoneer",
    fee_usd=5.0,
    status="pending"
))

# Log withdrawal received (CLOSE THE LOOP)
fc.add_event(FinanceEvent(
    event_type=EventType.WITHDRAWAL_RECEIVED,
    amount_usd=195.0,
    scheme_name="Content-Locking-CPA",
    network="CPAGrip",
    withdrawal_method="Payoneer",
    fee_usd=5.0,
    status="confirmed"
))

# Get P&L for last 30 days
pnl = fc.get_pnl(30)
# {"revenue": {"total_usd": 235, "by_stream": {...}}, "spend": {...}, "net_usd": 235, "net_rub": 22325}

# Get scheme unit economics
schemes = fc.get_scheme_economics()
# [{"scheme_name": "Content-Locking-CPA", "total_spend_usd": 0, "total_revenue_usd": 235, "total_leads": 2, "total_conversions": 2, "roi_pct": 9999, "status": "scaling"}]

# Get tax liability
tax = fc.get_tax_liability()
# {"accrued_usd": 9.4, "paid_usd": 0, "pending_usd": 9.4, "pending_rub": 893}

# Get pending withdrawals
withdrawals = fc.get_pending_withdrawals()
# [{"network": "CPAGrip", "amount_usd": 200, "method": "Payoneer", "status": "pending"}, ...]

# Export to Excel
path = fc.export_excel()
# D:/Portable_Soft/hermes/outputs/finance/finance_report_20260705_020649.xlsx
```

## Convenience Functions (for autonomous_agent integration)

```python
from scripts.finance_core import log_spend, log_revenue, log_withdrawal_request, log_withdrawal_received, get_finance_summary

# Autonomous agent uses these:
log_spend(scheme="Content-Locking-CPA", amount_usd=100, cost_center="traffic", network="TikTok", notes="Ad spend")
log_revenue(scheme="Content-Locking-CPA", amount_usd=50, revenue_stream="cpa_network", network="CPAGrip", offer="Gaming cheats", utm={"source": "tiktok", "medium": "organic"})
log_withdrawal_request(scheme="Content-Locking-CPA", amount_usd=200, network="CPAGrip", method="Payoneer", fee_usd=5)
log_withdrawal_received(scheme="Content-Locking-CPA", amount_usd=195, network="CPAGrip", method="Payoneer", fee_usd=5)

# Full summary for autonomous agent state
summary = get_finance_summary()
# {"pnl_30d": {...}, "schemes": [...], "tax": {...}, "pending_withdrawals": [...], "usd_rate": 95.0}
```

## Integration with Autonomous Agent

In `autonomous_agent.py`:
- `collect_system_state()` calls `get_finance_summary()` → adds `"finance"` to state
- `evaluate_actions()` reads `state["finance"]` → generates finance-aware PRODUCE actions:
  - Scale profitable (ROI > 100%)
  - Kill unprofitable (ROI < 0 after $10 spend)
  - Deploy new if cash allows
  - Confirm pending withdrawals
  - Pay taxes if pending > $50

## Validation Gate (`scripts/validate-fix.sh`)

For arbitrage schemes, the checker runs:
```bash
bash scripts/validate-fix.sh Content-Locking-CPA
```
Checks:
1. Scheme exists in Workshop with ЦА template
2. ЦА template filled (all 4 sections)
3. Tracked in finance_core.db
3. Revenue ≥ $1
4. ≥1 confirmed withdrawal
5. Tax liability < $500
6. No critical errors in logs

Output: `PASS` or `FAIL` with metrics.

## Tax Handling (RF)
- Default: Samozanyatyy 4% (phys) / 6% (legal)
- Accrued automatically on REVENUE events (4%)
- Paid via `event_type=tax_paid` with withdrawal_method="Мой налог"
- Liability tracked in `tax_settings` and scheme_unit_economics

## Withdrawal Methods (RF Available)
| Method | Fee | Speed | Risk |
|--------|-----|-------|------|
| СБП/Карта РФ | 0% | Instant | Low |
| WebMoney | 0.8-1.5% | 1-3 days | Low |
| USDT TRC20 → P2P | 1-3% | 5-30 min | Medium |
| Payoneer | 2-5% | 2-5 days | High |
| Crypto (BTC/ETH) | $5-20 | 10-60 min | Medium |

## Anti-Patterns Prevented
| Anti-Pattern | How Finance Core Fixes |
|--------------|----------------------|
| "Deployed but never verified withdrawal" | withdrawal_received event required for PASS |
| "Forgot to pay taxes" | Tax liability tracked per scheme, auto-accrued on revenue |
| "Lost track of scheme ROI" | Unit economics auto-calculated per scheme |
| "Mixed personal/business expenses" | Cost centers enforce categorization |
| "No proof-of-payment" | withdrawal_received with status=confirmed + Excel export |
| "Faked revenue/withdrawal data (Rule 0 violation)" | Finance Core accepts ANY log_spend/log_revenue call without external verification. MUST cross-reference with external API (CPA network postback, bank API, blockchain explorer) before marking confirmed. See references/rule-0-compliance.md |

## Excel Export
`fc.export_excel()` creates multi-sheet workbook:
- P&L Summary (30d)
- Cash Flow (detailed)
- Unit Economics (per scheme)
- Tax Liability
- Pending Withdrawals

## Quick Start
```bash
# Test the module
python -c "
from scripts.finance_core import FinanceCore, get_finance_summary
fc = FinanceCore()
print(fc.get_pnl(30))
print(get_finance_summary())
```

## Rule 0 Compliance (MANDATORY)
**Rule 0:** "Сказал 'сделал X' → покажи артефакт. Артефакта нет → ты солгал → Остановись."

**Finance Core Rule 0 Compliance Checklist:**
- [ ] Every `log_revenue()` call MUST have external verification (CPA network postback, bank API, blockchain explorer) before `status=confirmed`
- [ ] Every `log_withdrawal_received()` call MUST have external verification (bank API, blockchain explorer, payment processor webhook) before `status=confirmed`
- [ ] `log_spend()` calls for ad spend MUST have ad platform API receipt (TikTok Ads API, FB Marketing API, etc.)
- [ ] `status=pending` is DEFAULT — `status=confirmed` ONLY after external verification
- [ ] Every financial claim in reports MUST reference external verification artifact (screenshot, API response, transaction hash, bank statement)

**Violation = Stop. Admit. Fix infrastructure first.**

## Helper Scripts
- `scripts/get_finance_summary.py` — Convenience wrapper to print full finance summary as JSON

## Files
- `scripts/finance_core.py` — main module
- `cache/finance_core.db` — SQLite database
- `outputs/finance/` — Excel exports
- `scripts/validate-fix.sh` — uses finance_core for validation
- `scripts/cost_tracker.py` — cost tracking + HITL gates
- `scripts/hitl_gates.py` — Human-in-the-Loop approval gates

## References
- `references/2026-07-05-cost-tracking-hitl.md` — session notes on cost tracking & HITL gates implementation
- `references/2026-07-24-revenue-breakthrough.md` — First sensor run with real positive P&L ($1,492 revenue, $1,292 net)
- `../arbitrage-sensors/references/2026-07-24-revenue-breakthrough.md` — First sensor run with real positive P&L ($1,492 revenue, $1,292 net)