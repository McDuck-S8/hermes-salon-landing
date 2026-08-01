---
name: cpa-landing-generator
description: Use when deploying CPA landing pages to GitHub Pages — 6 vertical templates, deploy CLI command, auto-generates docs/cpa/{niche}/index.html
---

# CPA Landing Generator

Generates production-ready CPA landing pages and deploys to GitHub Pages via `docs/cpa/` folder.

## When to Use

- Need CPA landing page for gaming (V-Bucks, Robux), crypto, dating, surveys, VPN, coupons
- Zero-cost hosting via GitHub Pages
- Must track conversions via UTM parameters
- Template must be responsive, fast-loading, single-file HTML

## Templates (6 niches)

| Niche | File | CTA Example |
|-------|------|-------------|
| `fintech` | `docs/cpa/fintech/index.html` | "Claim $50 Bonus" |
| `vpn` | `docs/cpa/vpn/index.html` | "Get 60% Off VPN" |
| `coupons` | `docs/cpa/coupons/index.html` | "Claim $100 Gift Card" |
| `dating` | `docs/cpa/dating/index.html` | "Find Verified Matches" |
| `survey` | `docs/cpa/survey/index.html` | "Start Earning $50/Survey" |
| `gaming` | `docs/cpa/gaming/index.html` | "Get Free V-Bucks Now" |

## Usage

```bash
# List templates
python scripts/landing_generator.py list

# Generate single landing (reports/)
python scripts/landing_generator.py generate gaming "https://your-cpa-link.com"

# DEPLOY MODE: generates all 6 to docs/cpa/{niche}/index.html
python scripts/landing_generator.py deploy "https://your-cpa-link.com"

# Then commit and push:
git add docs/cpa/
git commit -m "feat: deploy CPA landing pages"
git push origin <branch>
# → LIVE at https://mcduck-s8.github.io/hermes-salon-landing/cpa/gaming/
```

## GitHub Pages Requirements

- Repo must have Pages enabled on tracked branch + `/docs` folder
- Current config: `user/hermes-session-2026-06-09` branch, `/docs` path
- Multi-client: each niche in `docs/cpa/{niche}/index.html`
- Root `docs/index.html` can be directory listing or main offer

## Template Structure

- Single HTML file, inline CSS/JS (no external deps)
- Dark gradient background, white card, checkmark bullets
- CTA button with gradient, hover scale animation
- Footer disclaimer
- Meta viewport for mobile
- UTF-8, Russian locale

## Customization

Edit `TEMPLATES` dict in `scripts/landing_generator.py`:
- `title`: page title
- `h1`: headline
- `subtitle`: sub-headline
- `bullet1-4`: benefit bullets
- `cta`: button text
- `footer`: disclaimer text

## Verification

```bash
# After deploy, check all 6:
for n in fintech vpn coupons dating survey gaming; do
  curl -s -o /dev/null -w "%{http_code} " "https://mcduck-s8.github.io/hermes-salon-landing/cpa/$n/"
done
# All should return 200
```

## Integration

- **Upstream:** `cpa-income-pipeline` (umbrella), `superpowers:brainstorming` (niche selection)
- **Downstream:** `cpa-video-script-generator` (matching niches), `cpa-telegram-bot-generator` (matching offer), `cpa-video-pipeline` (content for traffic)
- **Tracking:** UTM template in `cpa-income-pipeline` skill