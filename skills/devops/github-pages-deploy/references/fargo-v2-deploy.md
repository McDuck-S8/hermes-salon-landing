# Fargo v2 Dark Luxury Deploy Notes

## Source
`D:\Portable_Soft\hermes\demos\fargo\index.html` (commit cb6d309ed)

## Target
`/tmp/hermes-salon-landing/docs/fargo-v2/index.html` → GitHub Pages at `https://mcduck-s8.github.io/hermes-salon-landing/fargo-v2/`

## OG URL Fix Required
The demo's og:url points to `/fargo/` — must rewrite to `/fargo-v2/`:
```bash
sed -i 's|https://mcduck-s8.github.io/hermes-salon-landing/fargo/|https://mcduck-s8.github.io/hermes-salon-landing/fargo-v2/|g' docs/fargo-v2/index.html
```

## Deployment Steps
```bash
cd /tmp/hermes-salon-landing
git add docs/fargo-v2/index.html
git commit -m "feat(fargo): add v2 dark luxury to /fargo-v2/"
git push origin user/hermes-session-2026-06-09
# Wait for Pages rebuild (~30-60s)
# Verify: curl -I https://mcduck-s8.github.io/hermes-salon-landing/fargo-v2/
```

## Design Notes (from anti-slop-design skill)
- **Three Dials:** DESIGN_VARIANCE=8, MOTION_INTENSITY=9, VISUAL_DENSITY=3
- **Typography:** Playfair Display (serif) + Inter (sans) — editorial/luxury justified
- **Color:** Dark luxury (#0A0A0A bg, #C9A96E gold accent) — NOT default beige/brass
- **Motion:** Particle system, kinetic typography, scroll animations — motion intensity 9
- **Anti-AI tells checked:** No em-dashes, no 3-equal-cards, no split-header sections, premium palette rotated