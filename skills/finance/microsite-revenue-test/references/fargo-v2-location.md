# Fargo v2 Dark Luxury Location

## The Real v2
The actual "2026 redesign - kinetic typography, dark luxury theme, scroll animations" (commit `cb6d309ed`) is at:
- **Source**: `cb6d309ed:docs/fargo/index.html` (git history)
- **Local copy**: `demos/fargo/index.html` — BUT this has been overwritten with v1 content during the `/fargo/` fix

## How to Recover v2
```bash
# Get true v2 from git history
git show cb6d309ed:docs/fargo/index.html > /tmp/fargo_v2_real.html

# Update OG URL for /fargo-v2/
sed -i 's|https://mcduck-s8.github.io/hermes-salon-landing/fargo/|https://mcduck-s8.github.io/hermes-salon-landing/fargo-v2/|g' /tmp/fargo_v2_real.html

# Deploy to /fargo-v2/
cp /tmp/fargo_v2_real.html docs/fargo-v2/index.html
git add docs/fargo-v2/index.html && git commit -m "feat(fargo): deploy true v2 dark luxury to /fargo-v2/" && git push
```

## v2 Characteristics (Dark Luxury)
- **Colors**: `--bg: #0A0A0A`, `--gold: #C9A96E`, `--gold-light: #DFC28A`
- **Typography**: Playfair Display (serif) + Inter (sans)
- **Effects**: Preloader, kinetic char-by-char title reveal, particle system, scroll animations, glassmorphism cards, grain overlay
- **Sections**: Hero, About, Services, Price accordion, Gallery, Testimonials, Contact, Slots, Booking form
- **Background**: Dark with gold radial gradients, particle float animation

## Files
- `cb6d309ed:docs/fargo/index.html` — true v2 in git history
- `docs/fargo-v2/index.html` — deployed copy (after running recovery)
- `demos/fargo/WEB_DESIGN_ANALYSIS_2026.md` — reference analysis doc