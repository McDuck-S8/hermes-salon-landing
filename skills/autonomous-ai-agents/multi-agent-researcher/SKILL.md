---
name: multi-agent-researcher
description: >-
  Parallel research agent for CPA offers, affiliate networks, competitors, and 
  market intelligence. Uses Hermes delegate_task to fan out independent research 
  subtasks across workers, then synthesizes findings.
license: Apache-2.0
metadata:
  author: "Hermes"
  version: "1.0.0"
  source: "Adapted from awesome-llm-apps multi_agent_researcher"
self_improving: true
eval_schedule: "0 3 * * *"
eval_threshold: 0.85
gemini_model: "gemini-1.5-pro"
---

# Multi-Agent Researcher

Parallel research across multiple independent topics. Each worker gets a 
self-contained brief and returns structured findings.

## Use When

- Researching 5+ CPA offers / affiliate networks / competitors
- Need market intelligence on a niche (geo, vertical, traffic source)
- Comparing landing pages, creatives, funnels
- Gathering data from multiple sources in parallel

## Architecture

```
Orchestrator (you)
    │
    ├─→ Worker 1: Offer A research (payout, geo, restrictions, creatives)
    ├─→ Worker 2: Offer B research
    ├─→ Worker 3: Network C terms & reputation
    ├─→ Worker 4: Competitor D landing analysis
    └─→ Worker 5: Traffic source E costs & rules
    │
    └─→ Synthesize → Actionable report with scores
```

## Research Domains (Templates)

### CPA Offer Research Brief
```
GOAL: Full intelligence on [offer name / ID]
CONTEXT:
  - Network: [CPA network name]
  - Geo: [target country]
  - Vertical: [nutra/gaming/dating/finance/etc]
  - Traffic: [fb/tiktok/google/native/push]
ACCEPTANCE:
  - Payout & conversion flow confirmed
  - Restrictions (age, gender, creatives) documented
  - Landing page URLs captured
  - Creative angles identified
  - Approval requirements (pre-landers, cloaking)
  - EPC/CR benchmarks if available
FORMAT: JSON with fields: offer_id, network, payout, flow, restrictions, landers, creatives, risks, score
```

### Competitor Landing Analysis Brief
```
GOAL: Deconstruct competitor funnel
CONTEXT:
  - URL: [landing page]
  - Traffic source: [where they buy]
  - Geo: [target]
ACCEPTANCE:
  - Hook/angle identified
  - Structure mapped (pre-lander → lander → offer)
  - Creative styles catalogued
  - Tech stack detected (tracker, LP builder)
  - Estimated spend signals
FORMAT: JSON with fields: url, hook, structure, creatives, tech, spend_signals
```

### Network Reconnaissance Brief
```
GOAL: Profile CPA network
CONTEXT:
  - Network name
  - Verticals of interest
ACCEPTANCE:
  - Offer count by vertical
  - Payment terms (net-X, min payout)
  - Reputation (shaves, bans, support quality)
  - Exclusive offers list
  - Account manager responsiveness
FORMAT: JSON with fields: network, verticals, terms, reputation, exclusives, am_quality
```

## Dispatch Pattern

```python
# In your code, use delegate_task:
results = delegate_task(
    tasks=[
        {"goal": "Research offer X", "context": brief_1, "role": "leaf"},
        {"goal": "Research offer Y", "context": brief_2, "role": "leaf"},
        {"goal": "Analyze competitor Z", "context": brief_3, "role": "leaf"},
    ],
    timeout=300  # 5 min per worker — prevents stuck calls
)
# Workers run in parallel, return summaries
```

**Timeout handling**: If a worker times out, treat as FIX — redispatch with:
- Simplified brief (fewer sources, single focus)
- Explicit "skip slow sources" instruction
- Shorter timeout (180s)

## Synthesis Rules

- Score each offer 1-10 on: payout stability, conversion ease, creative freedom, geo fit
- Flag red flags: shady network, cloaking required, unstable payouts
- Rank by expected ROI = (payout * estimated_CR) / traffic_cost
- Output: ranked table + top 3 recommendations + risks

## Integration with Browser Automation

For JS-heavy sources (FB Ad Library, TikTok Creative Center, CPA network dashboards), workers **MUST** use `browser-automation` skill with BrowserOS MCP.

### Worker Brief — Browser Tools Required

```json
{
  "tools_required": ["browser-automation", "mcp-browseros"],
  "mcp_servers": ["browseros"],
  "browser_patterns": ["cpa-network-scraping", "creative-intel-scraping"]
}
```

### Orchestrator Pre-Dispatch Checklist

Before dispatching workers that need browser tools:
- [ ] BrowserOS MCP running: `curl http://localhost:9003/mcp` → 200 OK
- [ ] `browser-automation` skill available
- [ ] Worker brief includes `tools_required: ["browser-automation"]`
- [ ] Timeout set to 300s (not default 600s)
- [ ] Acceptance criteria include visual verification (screenshots)

### Browser Patterns Reference

See `browser-automation/references/creative-intel-patterns.md` for:
- CPA network scraping (AdCombo, CPAlead, Alfaleads)
- FB Ad Library creative extraction
- TikTok Creative Center scraping
- Rate limiting & delays

### Timeout Handling

If worker times out (600s default → reduce to 300s):
1. Treat as **FIX** (not ESCALATE)
2. Redispatch with:
   - `browser-automation` skill explicitly required
   - Simplified brief (single network, single vertical)
   - Explicit instruction: "Use browser automation for all JS-heavy sites"
   - Timeout: 180s

## Cronjob Template

Run daily/weekly:
```bash
hermes cron create --schedule "0 8 * * *" \
  --prompt "Research top 10 new offers on [networks] for [geo], rank by ROI potential" \
  --skills "multi-agent-researcher,arbitrage-sensors"
```

## Weekly Network Reconnaissance Template (NEW 2026-07-26)

Run every Sunday as part of portfolio review:
```bash
hermes cron create --schedule "0 9 * * 0" \
  --prompt "Weekly portfolio review. Dispatch multi-agent researcher for 3 CPA network reconnaissance briefs: AdCombo (IN/BR/RU), CPAlead (RU), MaxBounty (US/CA). Synthesize results into top 3 offers to test next week with $200 budget reserve." \
  --skills "multi-agent-researcher,ai-financial-coach,finance-core"
```

**Reference:** `references/2026-07-26-network-reconnaissance.md` — Full dispatch brief templates, acceptance criteria, and synthesis rules for the weekly 3-network reconnaissance pattern.

## Weekly Network Reconnaissance Dispatch Pattern (NEW 2026-07-26)

Used in weekly portfolio review to find 3 new offers to test across target networks:

```python
# Dispatch 3 parallel workers for network reconnaissance
tasks = [
    {
        "goal": "Research CPA network AdCombo: active offers, verticals, geo coverage, payment terms, reputation, exclusives, AM quality. Focus: IN, BR, RU geos for gambling/sports, nutra, sweepstakes, gaming.",
        "context": "Weekly portfolio review - need 3 new offers to test next week",
        "role": "leaf"
    },
    {
        "goal": "Research CPA network CPAlead: active offers, verticals, geo coverage, payment terms, reputation. Focus: RU geo for gaming, utility, survey.",
        "context": "Weekly portfolio review - need 3 new offers to test next week",
        "role": "leaf"
    },
    {
        "goal": "Research CPA network MaxBounty: active offers, verticals, geo coverage, payment terms, reputation, exclusives. Focus: US, CA geos for finance, nutra.",
        "context": "Weekly portfolio review - need 3 new offers to test next week",
        "role": "leaf"
    }
]
results = delegate_task(tasks=tasks, timeout=300)

# Timeout = 5 min per worker. If worker times out:
# 1. Redispatch with simplified brief: single network, single vertical
# 2. Explicit "skip slow sources" instruction
# 3. Shorter timeout (180s)
```

### Network Reconnaissance Brief Template

```
GOAL: Profile CPA network [NETWORK NAME]
CONTEXT:
  - Target geos: [IN, BR, RU / US, CA / etc]
  - Target verticals: [gambling/sports, nutra, sweepstakes, gaming / finance, nutra / etc]
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