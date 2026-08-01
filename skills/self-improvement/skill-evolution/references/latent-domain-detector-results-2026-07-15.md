# Latent Domain Detector Results (2026-07-15)

## Run Summary
- **Script**: `scripts/_deprecated/latent_domain_detector.py --seed`
- **Cube entries**: 3,588
- **Existing domains**: 39
- **Seeds generated**: 48 new white-spot entries

## Logical Gaps Discovered (3 clusters)

### 1. Telegram-боты (151 mentions)
**Missing sub-domains:**
- payment
- hosting
- deployment
- monetization
- analytics

### 2. Контент/каналы (90 mentions)
**Missing sub-domains:**
- marketing
- analytics
- seo
- audience

### 3. Разработка/инфраструктура (446 mentions)
**Missing sub-domains:**
- cicd
- monitoring
- backup

## Top Bridge Candidates (co-occurrence)

| Bridge | Co-freq | Suggested Domain |
|--------|---------|------------------|
| bugfix ↔ test | 1,379 | knowledge |
| communication ↔ test | 220 | knowledge |
| skill ↔ test | 57 | knowledge |
| creative ↔ skill | 44 | improvement |
| research ↔ skill | 44 | improvement |
| data ↔ skill | 37 | self-improvement-runtime |
| skill ↔ system | 36 | агента |
| devops ↔ skill | 30 | log unknown |
| skill ↔ terminal | 29 | comment |
| devops ↔ test | 26 | knowledge |

## Seeds Generated
48 white-spot entries inserted into Knowledge Cube with `is_white_spot=1`. These will be picked up by:
- `knowledge_gap_filler.py` — auto-research
- `white-spot-explorer` — deep investigation via opencode.ai/zen

## Next Actions
1. Monitor `knowledge_gap_filler` cron output for auto-research on these seeds
2. Consider creating skills for high-priority gaps: `telegram-bot-payment`, `telegram-bot-deployment`, `devops-cicd`, `content-marketing`
3. Update `latent_domain_detector.py` semantic clusters if domain focus shifts