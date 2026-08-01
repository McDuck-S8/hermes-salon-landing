---
name: arbitrage-router
description: "Arbitrage route calculator — Spider web router for CPA/arbitrage. Calculates optimal traffic → landing → CPA → P2P → bank routes with ROI, fees, time. CLI tool for instant route analysis."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [arbitrage, cpa, routing, roi, traffic, p2p, crypto, finance]
    related_skills: [arbitrage-execution, finance-core, arbitrage-sensors, cpa-income-pipeline]
    trigger: when analyzing arbitrage opportunities or calculating ROI for traffic sources
  skill_updated: "2026-07-24"
  created_by: "auto_patch_g007"
---

# Arbitrage Router — Spider Web Route Calculator

**One CLI tool. 6 traffic sources. 21 nodes. Instant ROI analysis.**

## Quick Start

```bash
# Show all best routes for $100 budget
python scripts/arbitrage_router.py --all --budget 100

# Show all routes from specific source
python scripts/arbitrage_router.py --from telegram --budget 100

# Simulate specific route
python scripts/arbitrage_router.py --route telegram carrd cpagrip kucoin-p2p tbank profit
```

## Graph Structure (21 Nodes, 5 Layers)

```
Z0: TRAFFIC SOURCES          Z1: LANDING PADS        Z2: CPA NETWORKS
├── tiktok (organic)         ├── carrd (5% CTR)      ├── cpagrip ($3.5, 30%)
├── youtube (organic)        ├── tgbot (3% CTR)      ├── mylead ($2.5, 25%)
├── telegram ($5/post)       ├── ghpages               ├── fincpa ($15, 15%)
├── reddit (organic)         ├── seosite               ├── travel ($10, 3%)
├── pinterest (organic)      └── ...                   └── maxbounty ($8, 5%)
└── seo (organic)

Z3: REFERRALS                Z4: P2P ARBITRAGE        Z5: WITHDRAWAL
├── kucoin-ref (30%)         ├── kucoin-p2p (1.5%)    ├── tbank (0.5%)
├── okx-ref (30%)            ├── okx-p2p (0.5%)       ├── crypto
└──                          ├── p2p-cycle (0.5%)     └── profit
```

## CLI Commands

| Command | Purpose |
|---|---|
| `--all --budget 100` | All best routes for $100 |
| `--from telegram` | All routes from Telegram |
| `--route A B C D` | Simulate specific path |
| `--budget 500` | Change budget |

## Route Output Fields

| Field | Meaning |
|---|---|
| **ROI** | Net profit / spend × 100% |
| **Конв.акц** | CPA actions count |
| **Доход** | Total revenue USD |
| **Комис** | Total fees USD |
| **Чист** | Net profit USD |
| **Время** | Minutes to withdrawal |
| **Маршрут** | Node path (A → B → C → Profit) |

## Example Output

```
Источник    ROI      Конв.    Доход    Комис    Чист    Время  Маршрут
TGканалы   +1303%     450     $7050    $35      $6515   15мин  telegram→fincpa→kucoin-ref→kucoin-p2p→tbank→profit
TikTok     +165%      225     $832     $4       $828    15мин  tiktok→carrd→cpagrip→kucoin-ref→kucoin-p2p→tbank→profit
```

## Integration with Finance Core

```python
from scripts.finance_core import log_spend, log_revenue

# After route execution, log real spend/revenue
log_spend(scheme="TG-FinCPA", amount_usd=100, cost_center="traffic", network="Telegram")
log_revenue(scheme="TG-FinCPA", amount_usd=1350, revenue_stream="cpa_network", network="FinCPA")
```

## Anti-Patterns (from 71 browser entries, 57 failures)

| Anti-Pattern | Guard |
|---|---|
| Route assumes organic traffic = free | Router treats organic as "10000 views per $100" proxy cost |
| Ignores P2P fees | Every P2P hop has fee_pct (0.3-2%) |
| Ignores withdrawal time | Route includes time_min per hop |
| Single route assumption | Router enumerates ALL paths, sorts by ROI |

## Verification

```bash
# Verify router works
python scripts/arbitrage_router.py --all --budget 100
# Should show 6 sources with ROI > 0
```

---

**Origin:** g-007 Unlock: browser (71 entries, 29 failures)  
**Created:** 2026-07-24 via auto_patch_g007  
**Source:** `scripts/arbitrage_router.py` (441 lines, 21 nodes, 5 layers)