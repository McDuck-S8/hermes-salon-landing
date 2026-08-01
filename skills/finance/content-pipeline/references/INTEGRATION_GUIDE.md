# Content Pipeline Integration Guide

## Integration Points (Planned)

- **Signal Daemon** → Research stage (HN, GitHub trends, keyword gaps)
- **Auto-Assign** → routes content tasks to Content agent
- **War Room** → /standup reviews pipeline health
- **Cron** → scheduled runs for each stage
- **Analytics** → Analyze stage feeds Suggestions Engine

## Architecture

```
RESEARCH (every 6h)          CREATE (daily 2AM)          PUBLISH (daily 4AM)
      │                              │                           │
      ▼                              ▼                           ▼
┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
│ signal → topic  │          │ Write asset     │          │ Deploy to       │
│ keyword validate│          │ + meta          │          │ owned props     │
│ CPA offer match │          │ TESTS: readability,   │          │ Indexed, pixels │
└─────────────────┘          │ kw density, CTA     │          └─────────────────┘
                             └─────────────────┘
                                    │
                                    ▼
                         REPURPOSE (daily 6AM)
                                    │
                         ┌─────────────────┐
                         │ 10+ derivatives │
                         │ thread, carousel│
                         │ shorts, audiogram│
                         └─────────────────┘
                                    │
                                    ▼
                         ANALYZE (weekly Mon 8AM)
                                    │
                         ┌─────────────────┐
                         │ GA4, GSC, CPA   │
                         │ Decide: KILL/   │
                         │ ITERATE/SCALE   │
                         └─────────────────┘
```

## Mandatory: Target Audience Template

**Before ANY content creation, fill Template:**

```markdown
## TARGET AUDIENCE TEMPLATE
### WHO
- Demographics: 
- Psychographics: 
- Pain points (3+): 
- Desired outcome: 

### WHERE
- Primary platform: 
- Search intent: [informational/commercial/transactional/navigational]
- Keywords (cluster): 

### WHAT
- Content format: 
- Angle/hook: 
- CTA → Offer: [specific CPA network + offer ID]

### WHY (Arbitrage Math)
- Traffic cost (time/$): 
- Expected conversion: 
- Payout: 
- Target ROI: >200%
- Break-even: X conversions
```

**Без заполненного шаблона ЦА — контент не создается.**

## Arbitrage Integration

| Traffic Source | Monetization | Test Metric |
|----------------|--------------|-------------|
| SEO article | CPA offer (lead/sale) | EPC > $0.50 |
| YouTube | AdSense + CPA in desc | RPM > $2 |
| Telegram channel | CPA posts + own products | Revenue/subscriber > $0.10 |
| Shorts/Reels | Funnel to channel/site | CTR > 3% |

## Stage Gates (Test Harness)

Each stage passes SPEC→TESTS→GENERATE→VALIDATE→LOOP→DELIVER:

1. **Research** → TESTS: search volume > X, KD < Y, offer exists
2. **Create** → TESTS: readability, keyword density, CTA placement, schema valid
3. **Publish** → TESTS: indexed, no errors, tracking pixels fired
4. **Repurpose** → TESTS: each derivative passes platform-specific tests
5. **Analyze** → TESTS: conversion > threshold → SCALE budget, else KILL

## Cron Schedule
```env
HERMES_CONTENT_RESEARCH_CRON="0 */6 * * *"      # Every 6h
HERMES_CONTENT_CREATE_CRON="0 2 * * *"          # Daily 2AM
HERMES_CONTENT_PUBLISH_CRON="0 4 * * *"         # Daily 4AM
HERMES_CONTENT_REPURPOSE_CRON="0 6 * * *"       # Daily 6AM
HERMES_CONTENT_ANALYZE_CRON="0 8 * * 1"         # Weekly Mon 8AM
```

## Kill Switches
```env
HERMES_CONTENT_RESEARCH_ENABLED=true
HERMES_CONTENT_CREATE_ENABLED=true
HERMES_CONTENT_PUBLISH_ENABLED=true
HERMES_CONTENT_REPURPOSE_ENABLED=true
HERMES_CONTENT_ANALYZE_ENABLED=true
HERMES_CONTENT_PIPELINE_ENABLED=true  # Master
```