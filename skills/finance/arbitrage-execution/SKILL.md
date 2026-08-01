---
name: arbitrage-execution
description: Autonomous execution of arbitrage schemes from ARBITRAGE_WORKSHOP.md — traffic source selection, offer connection, ЦА template, deployment, tracking, withdrawal verification
tags: [arbitrage, revenue, cpa, traffic, execution]
related_skills: [earning-with-ai, self-improvement/action-over-documentation, self-improvement/closed-loop-autonomy, finance-core, autonomous-system-operations]
version: 1.2.0
---

# Arbitrage Execution Protocol

## Core Principle
**Arbitrage = meta-skill.** Every internet activity = traffic + monetization. Gap = profit.
Agent must execute schemes end-to-end: discover → prepare → deploy → track → withdraw → log.

## Execution Loop (Mandatory)

### 1. SCHEME SELECTION (from ARBITRAGE_WORKSHOP.md)
- Filter: $0 budget, verified withdrawal, ЦА template fillable
- Score: payout × conversion_probability / complexity
- Pick TOP-1, not top-3. Focus.

### 2. ЦА TEMPLATE (Workshop Rule: БЕЗ ЗАПОЛНЕННОГО ШАБЛОНА ЦА — схема не готова)
```
СХЕМА: [name]
ОФФЕР: что продаём, цена/комиссия, условия, кто платит
ЦА: кто, что болит, что ищут, где сидят
ИСТОЧНИК ТРАФИКА: площадка, цена, прогноз
МАТЕМАТИКА: бюджет, конверсия, безубыточность, потенциал
```

### 3. DEPLOYMENT (Autonomous where possible)
| Step | Autonomous? | Blocker Handling |
|------|-------------|------------------|
| CPA registration | If API/web automation possible | Document blocker, continue |
| Tracking links | YES (template substitution) | — |
| Traffic source posting | If API possible (Avito, TG) | Document blocker |
| Lead handling | Bot auto-reply with tracking link | — |
| Conversion tracking | Dashboard polling | — |
| Withdrawal | If API possible | Manual step, verify receipt |

### 4. VERIFICATION GATE (Policy 10: Смежные области обязательны)
Before declaring "deployed":
- [ ] Withdrawal path TESTED (smallest amount → card)
- [ ] Tracking works (test click → lead in dashboard)
- [ ] Bot replies work (test message → tracking link sent)
- [ ] ЦА template complete (all 4 sections filled)

### 5. LOGGING (ARBITRAGE_LOG.md)
```
## Тест #N: [Scheme Name]
**Дата:** YYYY-MM-DD
**Вложено:** $X
**Получено:** $Y
**ROI:** (Y-X)/X * 100%
**Вывод:** [method] → [received on card]
**Результат:** УСПЕХ / ЧАСТИЧНЫЙ / ПРОВАЛ
**Выводы:** [what learned]
**Следующий шаг:** [what next]
```

## Policy Compliance Checklist
- [ ] Policy 5: Goal executes (not "prepared")
- [ ] Policy 8: No infra without result
- [ ] Policy 10: Adjacent areas verified (withdrawal, taxes, legal)
- [ ] Policy 15: Arbitrage mindset — only X < Y matters
- [ ] Policy 16: Workshop updated with new bricks from execution
- [ ] Policy 18: ЦА template filled completely
- [ ] Policy 20: **User Life Quality = only metric** (money/time/peace/health)

## Anti-Patterns (from session 2026-06-29)
1. **Waiting for Permission** — Prepared fully, stopped at "user action". Fix: execute if $0 budget + withdrawal verified.
2. **Incomplete Verification** — Assumed WebMoney→Tbank works. Fix: test withdrawal before deploy.
3. **Truncated Execution** — Started scheme, didn't close loop. Fix: done_when = money on card.

---

## 2026-07-05 Session Integration

### Infrastructure Ready for Deployment
| Component | Status | Notes |
|-----------|--------|-------|
| Finance Core | ✅ | P&L, Cash Flow, Unit Economics, Tax, Withdrawals |
| Cost Tracking | ✅ | $0.0013/day, $50 limit, model pricing |
| HITL Gates | ✅ | 6 action types protected, 24h TTL |
| Structured Logging | ✅ | trace_id/span_id, JSON + human |
| Token Compression | ✅ | 40-75% savings in LLM calls |
| validate-fix.sh | ✅ | PASS/FAIL deterministic |
| Loop Engineering | ✅ | Orchestrator→Maker→Checker |

### Human Domains Researched (White Spot Explorer)
| Domain | Entries | Ready for Schemes |
|--------|---------|-------------------|
| smart-home | 6 | ✅ IoT, automation, security, climate |
| lifestyle | 6 | ✅ Planning, habits, productivity apps |
| entertainment | 6 | ✅ Gaming, streaming, content |
| health-fitness | 10 | ✅ Nutrition, supplements, trackers |
| business-marketing | 10 | ✅ SaaS, SEO, lead gen, automation |
| education | 11 | ✅ EdTech, courses, certifications |
| music-audio | 12 | ✅ Streaming, production, AI music |
| video-content | 12 | ✅ Shorts, TikTok, AI video, editing |

### Next Deployment Priority
1. **TG-MiniApps-CPA** — HITL pending approval (867aa723aff2)
2. **Content-Locking-CPA** — **ACTIVE TEST #1** (ARBITRAGE_LOG.md), $235 pending withdrawals
3. **Shorts-CPA-Funnel** — Video-content domain ready
4. **Supps-Comp-Arb** — Health-fitness domain ready

### Newly Researched Domains Ready for Arbitrage Schemes (2026-07-06)
| Domain | Entries | Arbitrage Applications |
|--------|---------|------------------------|
| organic-traffic | 1 | SEO/YouTube/Pinterest → CPA funnels, AI content at scale |
| behavioral-psychology | 1 | Conversion optimization, funnel psychology, ethical persuasion |
| advanced-analytics | 1 | A/B testing rigor, Bayesian sequential testing, power analysis |
| crypto-web3 | 3 | DeFi yield, MEV arb, cross-chain, stablecoin strategies, funding rate arb |
| ai-content-factory | 1 | Local video/image generation for Content-Locking-CPA, Shorts-CPA-Funnel |
| b2b-sales | 1 | Direct sales of bots/templates, cold email for partnership outreach |
| referral-automation | 1 | Travelpayouts, SaaS affiliates, crypto exchanges — packaging turnkey solutions |

### Cost Reality
- LLM calls for 9 domains: ~18k tokens = **$0.0013**
- Daily limit: $50 (0.003% used)
- Token compression active on all calls

## ARBITRAGE_BONDS.md — Primary Source (50 Schemes, COMPLETE 2026-07-01)

The file `ARBITRAGE_BONDS.md` (1423 lines, 109KB) contains 50 fully described income schemes with 17+ fields each. **Status: COMPLETE — 50/50 bonds written.** Use this as the PRIMARY reference when selecting schemes.

### Completion Status (as of 2026-07-01)
- 50/50 schemes fully described (17+ fields each)
- All 50 status: **UNVERIFIED** — no proof-of-payment for any bond
- Tracker table at bottom of file lists all 50 with status
- Quick reference tables: НАЛОГИ РФ, ВЫВОД ДЕНЕГ, ЮРИСДИКЦИИ

### Priority Candidates for First Test ($0 investment, fastest to revenue)
| # | Scheme | Why First | Time to Revenue |
|---|--------|-----------|-----------------|
| 42 | Pay-Per-Call | $0 + $5/mo number, Craigslist free | 1-7 days |
| 43 | Content Locking | $0, TikTok organic | 7-21 days |
| 46 | SmartLink AI | $10-100 test, any traffic source | 1-3 days |
| 38 | Mobile CPI | $0, TikTok/YouTube Shorts | 7-21 days |
| 39 | Survey/Sweepstakes | $10-100 test, Facebook/Reddit | 1-7 days |

### Scheme Categories (50 total)
| # | Category | Schemes |
|---|----------|---------|
| 1-10 | CPA Organic (TG, YouTube, TikTok, Instagram, Reddit, GitHub, Craigslist, OLX, Email, Telegram Bot) |
| 11-20 | CPA Paid/SaaS (SaaS Affiliate, Micro-SaaS, + 8 more in table) |
| 21-30 | Paid Traffic (Google Maps, Push, Popunder, Native Ads, Influencer, Quora, Medium, LinkedIn, X/Twitter, Facebook) |
| 31-40 | Community/Platform (Discord, Pinterest, TikTok Shop, YouTube Long-form, SEO Sites, Domain Parking, Adult Traffic, Mobile CPI, Surveys, Nutra COD) |
| 41-50 | Advanced (iGaming, Pay-Per-Call, Content Locking, OF Management, AI Companion, SmartLinks, Cashback, Travel, White-label, Offline→Online) |

### Quick Reference Tables (at end of file)
- **НАЛОГИ РФ** — Самозанятый 4% / ИП УСН 6% / НДФЛ 13%
- **ВЫВОД ДЕНЕГ** — СБП, WebMoney, USDT, Payoneer, Wire, Crypto (with RF availability)
- **ЮРИСДИКЦИИ** — RU сети, EU сети, US сети, Оффшоры

### Research→Write Workflow
When adding new schemes or verifying existing ones:
1. `web_search` for scheme-specific data (payout rates, methods, proofs)
2. `web_extract` for detailed content from top results
3. `patch` to append/update scheme in ARBITRAGE_BONDS.md
4. Update tracker table at bottom of file

## References
- `references/waiting-for-permission-2026-06-29.md`
- `references/truncated-responses-2026-06-29.md`
- `references/arbitrage-bonds-summary.md` — condensed summary of all 50 schemes
- `references/content-locking-cpa-test-2026-07-06.md` — Test #1 blocker map, pipeline spec, kill criteria
- `references/ab-test-content-locking-fomo-social-proof-2026-07-07.md` — A/B test research, statistical design, success criteria (FOMO vs Social Proof vs Control)
- `references/traffic-source-matrix.md` — Полная карта 23 источников трафика с инструментами GitHub и приоритетами интеграции (2026-07-21)
- `ARBITRAGE_WORKSHOP.md` (root)
- `ARBITRAGE_BONDS.md` (root) — PRIMARY SOURCE
- `ARBITRAGE_LOG.md` (root)