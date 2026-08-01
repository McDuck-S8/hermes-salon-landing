# Review Worker Checklist Templates

Landing page quality checklist used by `review_worker.py`. Each item has a weight (1-2) for scoring.

## Landing Page Checklist (12 items, max score 18)

| ID | Name | Weight | Description |
|----|------|--------|-------------|
| headline | Strong Headline | 2 | H1 tag present with compelling headline |
| hook | Hook in First 3 Seconds | 2 | Attention-grabbing word in first paragraph |
| benefits | Clear Benefits (not features) | 2 | Benefit-oriented language present |
| social_proof | Social Proof / Testimonials | 1 | Reviews, ratings, "trusted by" signals |
| cta | Clear CTA Above Fold | 2 | Button/link with action text visible early |
| urgency | Urgency/Scarcity Element | 1 | Limited spots, countdown, "only X left" |
| mobile | Mobile Responsive | 2 | Viewport meta, media queries, fluid layout |
| load_speed | Fast Load (no heavy scripts) | 1 | <10 script tags, no jQuery 3.x |
| trust | Trust Signals | 1 | Guarantee, secure badges, privacy links |
| offer_clarity | Offer Clearly Stated | 2 | Price, discount, what's included visible |
| no_leaks | No Navigation Leaks | 1 | No external links except tracking/CTA |
| tracking | Tracking Pixels Installed | 1 | GTM, GA4, FB Pixel, TikTok Pixel present |

## Scoring Formula

```
percentage = (sum of passed item weights / 18) * 100
passed = percentage >= 70
```

## Code Quality Checklist

| ID | Name | Check |
|----|------|-------|
| syntax | No Syntax Errors | `compile()` succeeds |
| tests | Has Tests | `def test_` or pytest present |
| types | Type Hints | `:` and `->` annotations |
| docstrings | Docstrings Present | `"""` or `'''` in file |
| secrets | No Hardcoded Secrets | `os.environ.get` for keys |
| errors | Error Handling | `try/except` blocks present |

## Content Quality Checklist

| ID | Name | Check |
|----|------|-------|
| hook | Strong Hook (First 3s) | Attention word in first 50 chars |
| structure | Clear Structure | >3 sentences, logical flow |
| cta | Clear CTA | "link in bio", "follow", "comment", "click" |
| value | Delivers Value | Content > 200 chars |
| engagement | Engagement Triggers | Questions, "comment", "save", "duet" |