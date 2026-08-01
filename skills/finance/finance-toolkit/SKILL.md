---
name: finance-toolkit
description: "Unified finance toolkit for Hermes: finance-core + cpa-income-pipeline + cpa-landing-generator + cpa-telegram-bot-generator + cpa-video-pipeline + cpa-video-script-generator + arbitrage-execution + arbitrage-sensors + ai-ofm-tribute + crypto-fiat-offramp + excel-author + pptx-author + earning-with-ai + microsite-revenue-test + no-doc-income + partner-business-plan + stocks. One skill to load, all finance engines at hand."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [finance, arbitrage, cpa, pnl, tax, withdrawal, excel, pptx, landing, video, bot, stocks, income, offramp]
    related_skills: [finance-core, cpa-income-pipeline, cpa-landing-generator, cpa-telegram-bot-generator, cpa-video-pipeline, cpa-video-script-generator, arbitrage-execution, arbitrage-sensors, ai-ofm-tribute, crypto-fiat-offramp, excel-author, pptx-author, earning-with-ai, microsite-revenue-test, no-doc-income, partner-business-plan, stocks]
  skill_updated: "2026-07-24"
  created_by: "auto_patch_g007"
  component_skills:
    - finance-core
    - cpa-income-pipeline
    - cpa-landing-generator
    - cpa-telegram-bot-generator
    - cpa-video-pipeline
    - cpa-video-script-generator
    - arbitrage-execution
    - arbitrage-sensors
    - ai-ofm-tribute
    - crypto-fiat-offramp
    - excel-author
    - pptx-author
    - earning-with-ai
    - microsite-revenue-test
    - no-doc-income
    - partner-business-plan
    - stocks
---

# Finance Toolkit — Unified Interface

**One skill to load. 16 finance engines. Zero context switching.**

This meta-skill wraps all core finance/arbitrage skills into a single loadable unit with a unified workflow interface.

## Quick Start

```python
# Load once, get all 16 tools
from hermes_tools import skill_view
skill_view("finance/finance-toolkit")

# Now you have:
# - finance-core (P&L, tax, withdrawal tracking, scheme unit economics)
# - cpa-income-pipeline (end-to-end CPA/arbitrage: offer scan → lander → traffic → conversion → withdrawal)
# - cpa-landing-generator (deploy CPA landing pages to GitHub Pages — 6 templates)
# - cpa-telegram-bot-generator (Telegram bots for CPA traffic — 3 templates)
# - cpa-video-pipeline (full video generation for CPA: script → avatar → voice → edit → deploy)
# - cpa-video-script-generator (Shorts/Reels/TikTok scripts for CPA)
# - arbitrage-execution (autonomous arbitrage schemes: gap find → launch → monitor)
# - arbitrage-sensors (CPA offer scanner, traffic cost monitor, network health)
# - ai-ofm-tribute (AI model image generation for OFM channels)
# - crypto-fiat-offramp (USDT → RUB/card — separate skill, hooks here)
# - excel-author (auditable Excel workbooks headless with openpyxl)
# - pptx-author (PowerPoint decks headless with python-pptx)
# - earning-with-ai (comprehensive guide: free AI sites, skills, monetization)
# - microsite-revenue-test (zero-budget microsite generation + deployment)
# - no-doc-income (income schemes without documents/KYC/IP)
# - partner-business-plan (business plans for potential partners)
# - stocks (Yahoo Finance: quotes, history, search, compare, crypto)
```

## Component Skills Map

| Skill | Purpose | Best For |
|-------|---------|----------|
| **finance-core** | P&L, tax, withdrawal tracking, scheme unit economics | ALL finance ops — central ledger |
| **cpa-income-pipeline** | End-to-end CPA/arbitrage conveyor | Offer scan → lander → traffic → conversion → withdrawal |
| **cpa-landing-generator** | Deploy CPA landing pages to GitHub Pages | 6 templates, auto-deploy |
| **cpa-telegram-bot-generator** | Telegram bots for CPA traffic | 3 templates, inline buttons |
| **cpa-video-pipeline** | Full video generation for CPA | Script → avatar → voice → edit → deploy |
| **cpa-video-script-generator** | Shorts/Reels/TikTok scripts for CPA | Hook → body → CTA structure |
| **arbitrage-execution** | Autonomous arbitrage schemes | Gap find → launch → monitor |
| **arbitrage-sensors** | CPA offer scanner, traffic cost, network health | Fast/medium/deep surveillance |
| **ai-ofm-tribute** | AI model image generation for OFM | Automated channel content |
| **crypto-fiat-offramp** | USDT → RUB/card (separate, hooks here) | Cash out crypto to fiat |
| **excel-author** | Auditable Excel workbooks headless | Reports, P&L, unit economics |
| **pptx-author** | PowerPoint decks headless | Partner presentations, pitch decks |
| **earning-with-ai** | Free AI sites, skills, monetization | Zero-budget income research |
| **microsite-revenue-test** | Zero-budget microsite gen + deploy | Fast validation |
| **no-doc-income** | Income without docs/KYC/IP | Zero-bureaucracy schemes |
| **partner-business-plan** | Business plans for partners | Partnership proposals |
| **stocks** | Yahoo Finance quotes/history/search | Market data, crypto |

## Unified Finance Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. SENSE (arbitrage-sensors)                                    │
│    • Fast (30m): CPA offer changes, arbitrage gaps              │
│    • Medium (1h): Traffic costs, CPA network health             │
│    • Deep (6h): Competitive intel, market shifts                │
│    • Signal scored → Telegram if threshold met                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. SCORE (finance-core + cpa-income-pipeline)                   │
│    • P&L by scheme (finance-core.get_pnl)                       │
│    • Unit economics: CPC, CTR, CR, EPC, ROI, payback_days       │
│    • Tax liability accrued on revenue (4% default)              │
│    • Pending withdrawals tracked                                 │
│    • Kill/scale decision from autonomous_agent                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. EXECUTE (parallel)                                           │
│                                                                  │
│  OFFER SCAN → cpa-income-pipeline                              │
│    cpa-landing-generator → GitHub Pages (6 templates)          │
│    cpa-telegram-bot-generator → inline buttons (3 templates)   │
│    cpa-video-pipeline → script→avatar→voice→edit→deploy        │
│    cpa-video-script-generator → hooks→body→CTA                 │
│                                                                  │
│  ARBITRAGE → arbitrage-execution                               │
│    Gap find → launch → monitor → scale/kill                    │
│                                                                  │
│  CASH OUT → crypto-fiat-offramp                                │
│    USDT → RUB/card (separate skill, hooks here)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. TRACK & REPORT (finance-core)                                │
│    • log_spend / log_revenue / log_withdrawal_request          │
│    • log_withdrawal_received (CLOSE THE LOOP)                  │
│    • get_pnl(30d) → P&L by stream/cost_center/scheme           │
│    • get_scheme_economics() → unit economics per scheme        │
│    • get_tax_liability() → accrued/paid/pending                │
│    • get_pending_withdrawals() → track cashout                 │
│    • export_excel() → multi-sheet workbook                     │
│    • validate-fix.sh → PASS/FAIL on scheme                     │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Commands Reference

### Finance Core (Central Ledger)
```python
from scripts.finance_core import FinanceCore, FinanceEvent, EventType

fc = FinanceCore()

# Spend (traffic, tools, infra)
fc.add_event(FinanceEvent(
    event_type=EventType.SPEND,
    amount_usd=50.0,
    cost_center="traffic",
    scheme_name="Content-Locking-CPA",
    network="CPAGrip",
    click_id="abc123",
    notes="TikTok ads test"
))

# Revenue (CPA conversion)
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

# Withdrawal request
fc.add_event(FinanceEvent(
    event_type=EventType.WITHDRAWAL,
    amount_usd=200.0,
    scheme_name="Content-Locking-CPA",
    network="CPAGrip",
    withdrawal_method="Payoneer",
    fee_usd=5.0,
    status="pending"
))

# Withdrawal RECEIVED (close the loop!)
fc.add_event(FinanceEvent(
    event_type=EventType.WITHDRAWAL_RECEIVED,
    amount_usd=195.0,
    scheme_name="Content-Locking-CPA",
    network="CPAGrip",
    withdrawal_method="Payoneer",
    fee_usd=5.0,
    status="confirmed"
))

# P&L 30 days
pnl = fc.get_pnl(30)
# {"revenue": {"total_usd": 235, "by_stream": {...}}, "spend": {...}, "net_usd": 235, "net_rub": 22325}

# Scheme unit economics
schemes = fc.get_scheme_economics()
# [{"scheme_name": "Content-Locking-CPA", "total_spend_usd": 0, "total_revenue_usd": 235, "roi_pct": 9999, "status": "scaling"}]

# Tax liability
tax = fc.get_tax_liability()
# {"accrued_usd": 9.4, "paid_usd": 0, "pending_usd": 9.4, "pending_rub": 893}

# Pending withdrawals
withdrawals = fc.get_pending_withdrawals()
# [{"network": "CPAGrip", "amount_usd": 200, "method": "Payoneer", "status": "pending"}, ...]

# Export Excel
path = fc.export_excel()
# D:/Portable_Soft/hermes/outputs/finance/finance_report_20260705_020649.xlsx
```

### Arbitrage Sensors (Background Surveillance)
```bash
# Cron jobs deployed:
# Fast (30m): 0/30 * * * * → arbitrage-sensors fast
# Medium (1h): 0 * * * * → arbitrage-sensors medium
# Deep (6h): 0 */6 * * * → arbitrage-sensors deep
```

### CPA Landing Generator
```bash
# Deploy landing to GitHub Pages
hermes cpa-landing deploy --template content-locking --offer "Free V-Bucks" --network CPAGrip
```

### CPA Telegram Bot Generator
```bash
# Generate bot code
hermes cpa-bot generate --template cpa-organic --offer "Free V-Bucks" --token $TELEGRAM_TOKEN
```

### Crypto Fiat Offramp (hooks in)
```bash
# Separate skill, called from finance-core
python -m skills.finance.crypto-fiat-offramp cashout --amount 200 --method sberpay
```

### Excel / PPTX Author
```python
from scripts.excel_author import ExcelAuthor
from scripts.pptx_author import PPTXAuthor

# Excel: auditable workbook
ea = ExcelAuthor()
ea.add_sheet("P&L", pnl_data)
ea.add_sheet("Unit Economics", schemes_data)
ea.save("outputs/finance/partner_report.xlsx")

# PPTX: partner pitch deck
pa = PPTXAuthor()
pa.add_title("Arbitrage Partnership Proposal")
pa.add_metrics(pnl_data)
pa.add_scheme_table(schemes_data)
pa.save("outputs/finance/partner_pitch.pptx")
```

### Stocks / Market Data
```python
from skills.finance.stocks import get_quote, get_history, search, compare, get_crypto

get_quote("AAPL")           # Current quote
get_history("BTC-USD", "1mo")  # 1 month history
search("tesla")             # Search symbols
compare(["AAPL", "MSFT", "GOOGL"])  # Compare
get_crypto("BTC-USD")       # Crypto quote
```

## Anti-Patterns (from 26 finance entries)

| Anti-Pattern | Guard |
|--------------|-------|
| Deployed but never verified withdrawal | **withdrawal_received** event required for PASS |
| Forgot to pay taxes | Tax liability auto-accrued on REVENUE (4% default) |
| Lost track of scheme ROI | Unit economics auto-calculated per scheme |
| Mixed personal/business expenses | Cost centers enforce categorization |
| No proof-of-payment | withdrawal_received + Excel export |
| USDT → RUB not tracked | crypto-fiat-offramp hooks into finance-core |

## Integration with Knowledge Cube

```python
from scripts.event_evolution import on_task_complete

on_task_complete(
    content="Finance cycle complete: scanned 12 offers, deployed 3 landers, launched 1 bot, generated 5 videos. P&L: +$235 net, ROI 142%. Tax accrued: $9.40. Withdrawal $195 confirmed.",
    tags=["finance", "cpa", "arbitrage", "pnl", "tax", "withdrawal", "success"],
    source="agent"
)
```

## Verification Checklist

After using this toolkit:
- [ ] finance-core: P&L current, unit economics calculated, tax accrued
- [ ] cpa-income-pipeline: offer scanned, lander deployed, traffic launched, conversion tracked
- [ ] cpa-landing-generator: 6 templates available, GitHub Pages auto-deploy
- [ ] cpa-telegram-bot-generator: 3 templates, inline buttons, commands registered
- [ ] cpa-video-pipeline: script→avatar→voice→edit→deploy
- [ ] cpa-video-script-generator: hook/body/CTA structure
- [ ] arbitrage-execution: gap found → launched → monitored
- [ ] arbitrage-sensors: fast/medium/deep cron running
- [ ] crypto-fiat-offramp: USDT → RUB/card working
- [ ] excel-author / pptx-author: reports generated
- [ ] crypto-fiat-offramp: withdrawal tracked in finance-core
- [ ] validate-fix.sh: PASS on scheme
- [ ] KC entry created with all tags

---

**Origin:** g-007 Unlock: finance (26 entries, 15 neutral, 9 success, 2 none)
**Created:** 2026-07-24 via auto_patch_g007
**Source:** Knowledge Cube domain `finance` + all 16 component skills