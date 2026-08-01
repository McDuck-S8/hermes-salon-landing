---
name: content-pipeline
description: Content Pipeline for Arbitrage — Research → Create → Publish → Repurpose → Analyze. End-to-end content factory for traffic assets.
tags: []
related_skills: []
---

# Content Pipeline — Arbitrage Asset Factory

Implements the AI-First Business Playbook Content Pipeline pattern for building owned traffic assets (sites, channels, bots) that generate revenue.

## Architecture

```
content-pipeline/
├── SKILL.md                    # This file
├── references/
│   ├── TARGET_AUDIENCE_TEMPLATE.md    # Mandatory CPA template
│   ├── REPURPOSING_MATRIX.md          # 1 piece → 10+ formats
│   ├── SEO_KEYWORD_STRATEGY.md        # Keyword research → content map
│   ├── MONETIZATION_MODELS.md         # CPA, ads, own products, leads
│   └── video-generation-content-locking-cpa.md  # Video pipeline for CPA
├── scripts/
│   ├── research.py               # Signal → topic → keyword validation
│   ├── create.py                 # Write/design asset (article, video, post)
│   ├── publish.py                # Multi-platform deploy
│   ├── repurpose.py              # Transform: long → short, thread, carousel
│   ├── analyze.py                # Performance → iterate/kill/scale
│   └── pipeline_orchestrator.py  # Run full cycle
├── templates/
│   ├── ARTICLE_TEMPLATE.md
│   ├── VIDEO_SCRIPT_TEMPLATE.md
│   ├── THREAD_TEMPLATE.md
│   └── CAROUSEL_TEMPLATE.md
└── examples/
    └── salon_lumiere_case.md
```

## The 5-Stage Cycle

### 1. RESEARCH (Signal → Topic)
- Input: War Room signals, HN/GitHub trends, keyword gaps, competitor gaps
- Output: Validated topic + keyword cluster + search intent + CPA offer match
- Gate: **Test Harness** — SPEC (topic, angle, KW, offer) + TESTS (search volume > X, KD < Y, offer exists)

### 2. CREATE (Asset Production)
- Input: SPEC from Research
- Output: Primary asset (article/video) + meta (title, desc, tags, schema)
- Gate: **Test Harness** — TESTS (readability, keyword density, CTA placement, schema valid)

### 3. PUBLISH (Distribution)
- Input: Primary asset + meta
- Output: Live URLs on owned properties (site, Telegram, YouTube, etc.)
- Gate: Indexed, no errors, tracking pixels fired

### 4. REPURPOSE (Leverage)
- Input: Primary asset
- Output: 10+ derivative assets auto-generated
- Matrix:
  - Article → Twitter thread, LinkedIn post, 5 TikTok/Reels scripts, carousel, newsletter, podcast outline
  - Video → Shorts, clips, blog post, thread, quotes, audiogram
- Gate: Each derivative passes platform-specific TESTS

### 5. ANALYZE (Feedback Loop)
- Input: Analytics (GA4, Search Console, platform insights, CPA postbacks)
- Output: Decision per asset — KILL / ITERATE / SCALE
- Metrics: CTR, dwell time, conversion rate, EPC, ROI
- Gate: **Test Harness** — TESTS (conversion > threshold) → SCALE budget, else KILL

## Arbitrage Integration

Each content piece = traffic asset. Monetization layer:

| Traffic Source | Monetization | Test Metric |
|----------------|--------------|-------------|
| SEO article | CPA offer (lead/sale) | EPC > $0.50 |
| YouTube | AdSense + CPA in desc | RPM > $2 |
| Telegram channel | CPA posts + own products | Revenue/subscriber > $0.10 |
| Shorts/Reels | Funnel to channel/site | CTR > 3% |

## Knowledge Cube Integration (Added 2026-07-04)

Pipeline now queries human domains for richer context at each stage:

```python
# RESEARCH: What traffic sources work?
kc.query_cube(domain='social-media', category='traffic')
# → "CPA Traffic Arbitrage via Telegram Mini-Apps"
# → "Cross-Platform Trend Arbitrage (TikTok -> YouTube -> Telegram)"

kc.query_cube(domain='video-content', category='traffic_source')
# → "Multi-Platform Shorts Syndication (TikTok -> YT Shorts -> Instagram Reels)"

# CREATE: What formats work?
kc.query_cube(domain='video-content', category='content_format')
# → "Transcript-to-Video Repurposing Pipeline"
# → "ASCII Video Wall for Ad Breaks"

# MONETIZATION: What monetization models?
kc.query_cube(domain='social-media', category='monetization')
# → "Telegram In-Channel Monetization Stack"
# → "Telegram Bot as a Service Funnel"

kc.query_cube(domain='finance', category='strategy')
# → "Latency Arbitrage via WebSocket Feed Aggregation"
# → "Statistical Arbitrage with Cointegration Pairs"

kc.query_cube(domain='finance', category='platform')
# → "Polymarket Event-Contract Mispricing Scanner"
```

### Pipeline Enhancement
1. **Research stage** → auto-query social-media + video-content for traffic sources
2. **Create stage** → auto-query video-content for formats, music-audio for audio assets
3. **Monetization stage** → auto-query finance for arbitrage strategies, social-media for monetization stacks
4. **Repurpose stage** → cross-platform syndication from video-content domain

## Target Audience Algorithm (MANDATORY)

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

## A/B Testing Integration (Added 2026-07-07)

**Per arbitrage-execution/references/ab-test-content-locking-fomo-social-proof-2026-07-07.md**, the CREATE stage now supports multi-variant generation for statistical A/B testing:

| Stage | A/B Test Integration |
|-------|---------------------|
| RESEARCH | Define test hypothesis: FOMO vs Social Proof vs Control |
| CREATE | Generate 3 variant assets per topic (Control/FOMO/Social Proof) |
| PUBLISH | Deploy with variant-specific UTM tags |
| REPURPOSE | Each variant repurposed independently |
| ANALYZE | Two-proportion z-test (Bonferroni α=0.025), MDE=15% lift |

**Video pipeline updated**: `references/video-generation-content-locking-cpa.md` now includes variant-aware script generation, metadata, and UTM tagging.

## Kill Switches

```env
HERMES_CONTENT_RESEARCH_ENABLED=true
HERMES_CONTENT_CREATE_ENABLED=true
HERMES_CONTENT_PUBLISH_ENABLED=true
HERMES_CONTENT_REPURPOSE_ENABLED=true
HERMES_CONTENT_ANALYZE_ENABLED=true
HERMES_CONTENT_PIPELINE_ENABLED=true  # Master
```

## Cron Schedule

```env
HERMES_CONTENT_RESEARCH_CRON="0 */6 * * *"      # Every 6h
HERMES_CONTENT_CREATE_CRON="0 2 * * *"          # Daily 2AM
HERMES_CONTENT_PUBLISH_CRON="0 4 * * *"         # Daily 4AM
HERMES_CONTENT_REPURPOSE_CRON="0 6 * * *"       # Daily 6AM
HERMES_CONTENT_ANALYZE_CRON="0 8 * * 1"         # Weekly Mon 8AM
```