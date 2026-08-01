---
name: cpa-video-script-generator
description: Use when generating Shorts/Reels/TikTok scripts for CPA content-locking campaigns — 7 niches, A/B/C variants (Control/FOMO/Social Proof), hooks, body, CTA, tags, UTM-ready
---

# CPA Video Script Generator

Generates vertical video scripts (9:16, 15-30s) for content-locking CPA campaigns across TikTok, YouTube Shorts, Instagram Reels.

## When to Use

- Need video scripts for CPA traffic (CPAGrip, OGAds, CPAlead, MyLead)
- Want A/B/C testing: Control (neutral) vs FOMO (urgency) vs Social Proof (validation)
- Need niche-specific hooks: gaming (V-Bucks, Robux), crypto, surveys, VPN, dating
- Need UTM-ready metadata for tracking per variant/platform/account

## Niches (7)

| Niche | Topics | Duration | Target Platform |
|-------|--------|----------|-----------------|
| `gaming-free` | Free V-Bucks, Free Robux | 20-25s | TikTok, Shorts, Reels |
| `crypto-free` | Free crypto, faucets | 25-30s | TikTok, Shorts |
| `survey-money` | Paid surveys, side hustle | 20-25s | Shorts, Reels |
| `vpn-promo` | VPN discounts, privacy | 15-20s | TikTok, Shorts |
| `dating-promo` | Verified dating, free trial | 15-20s | TikTok, Reels |
| `content-locking` | Unlock exclusive content | 15s | TikTok, Shorts |
| `amazon-gift` | Amazon gift cards | 20s | Shorts, Reels |

## Variant Matrix (A/B/C)

| Variant | Psychology | Hook Style | UTM Suffix |
|---------|------------|------------|------------|
| **A (Control)** | Neutral, curiosity | "Want free X?" | `control_neutral` |
| **B (FOMO)** | Urgency, scarcity | "ONLY 3 SPOTS LEFT!" | `fomo_timer` |
| **C (Social)** | Social proof, validation | "1,247 people got X today!" | `social_live` |

## Usage

```bash
# List all scripts
python scripts/video_scripts.py list

# Generate single script (reports/)
python scripts/video_scripts.py generate gaming-free

# Generate all 7 niches (reports/)
python scripts/video_scripts.py batch

# Generate for specific scheme (links to ARBITRAGE_BONDS.md)
python scripts/video_scripts.py scheme "СВЯЗКА #5" gaming-free
```

## Output Format (Markdown)

```markdown
# Video Script — Gaming
# Generated: 2026-07-19T16:40:28
# Duration: ~25s
# Tags: fortnite, free v-bucks, gaming hacks, fyp

## HOOK (0-3s)
ONLY 3 SPOTS LEFT for free V-Bucks!

## BODY (3-20s)
1. Fortnite patched the browser exploits last week.
2. But the API endpoint for item resale is still open.
3. Here's how to exploit it before they fix it.
4. Takes 2 minutes — works on mobile and desktop.

## CTA (20-25s)
Tap here — free V-Bucks generator (fast!)

## VISUAL NOTES
- Fast cuts (2-3s per scene)
- Text overlays for every line
- Background: gameplay footage
- End screen: pointing to link in bio
```

## Integration

- **Upstream:** `cpa-income-pipeline`, `cpa-landing-generator` (matching niches)
- **Downstream:** `cpa-video-pipeline` (stock footage + voiceover + ffmpeg compose)
- **Tracking:** UTM template in `cpa-income-pipeline` skill
- **Platform CTAs:** Auto-adjusted per platform (TikTok="Link in bio", Shorts="Link in description", Reels="Link in bio")

## A/B/C Testing Protocol

1. Generate all 3 variants per niche: `batch` creates 21 scripts
2. For each variant, produce 3-5 videos (different stock footage/voiceover)
3. Deploy to 3 accounts per platform per variant
4. Track: views, CTR (bio link clicks), conversion (offer completions)
5. Statistical significance: 95% CI, minimum 1000 views per variant
6. Winner → scale budget, loser → iterate hook

## Customization

Edit `VIDEO_SCRIPTS` dict in `scripts/video_scripts.py`:
- Add niches with hooks/body/CTA/tags/duration
- Hook variants per psychology type
- Platform-specific CTA mapping