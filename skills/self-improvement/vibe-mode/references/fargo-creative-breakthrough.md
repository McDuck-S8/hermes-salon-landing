# Fargo Creative Transformation (v1→v8 portfolio)

## Context
Beauty salon in Darnytskyi district, Kyiv. User rejected 4 iterations saying "всё одно и то же, цвета разные". Trigger for vibe-mode. 8 iterations total, final portfolio at `cache/nicheforge_demo/fargo-portfolio.html` with 12 local photos.

## Template being repeated (v1–v4)
```
nav → hero (h1 + image + CTA) → services (3-4 cards) → gallery → testimonials (3 cards) → prices (table) → footer
```
Each version just changed colors and fonts. Structure was identical.

## Breakthrough: people-first structure (v5)
Instead of services → show the masters. Each section is a person.

```
title card → manifesto → Katerina → Olena → atmosphere (color swatches) → price (as poetry lines) → closing invitation
```

No nav. No cards. No gallery. No testimonials.

## Youth/drive/beauty iteration (v6)
Feedback on v5: too serious, literary, dark. Need energy and youth.

```
splash with outline text + stats → masters as color-coded rows → energy banner (skew) → price chips grid → snap testimonials → closing tension
```

Vibrant palette: coral #ff4777, teal #0a6e6e, gold #ffbe3f, charcoal #1a1a2e.

## "Glow" refinement (v7)
Feedback on v6: "почему без фото? внутренняя уверенность и широкая улыбка".

Changes:
- **Sourced real images** from Unsplash: 12 photos (hero, 3 masters, 4 gallery, 3 testimonials, 1 wide)
- **Shifted palette** from aggressive coral to warm glow: #e0755a + #d4a05a
- **Changed tone** from "твій салон" to "сяйво" — radiant confidence
- **Added fallbacks** for broken images (onerror handlers)

## Homey/cozy final (v8 portfolio)
Feedback on v7: "вариант по домашнему, все свои. подскажут и помогут. два варианта на ПК и мобиле".

Final design direction:
- **Terracotta + olive palette**: #b86b4a + #5a6b4a + cream #f0e7dd
- **"Заходь, як до подруги"** — warm, familiar, personal
- **Playfair Display** — serif with italic, like a personal letter
- **Responsive**: mobile single-col, desktop multi-col
- **Local photos downloaded** via curl (12 files, 472 KB, `fargo-img/`)
- **Anti-slop clean**: no #000/#fff, no em-dash, no numbered sections

## Portfolio deliverables
- `cache/nicheforge_demo/fargo-portfolio.html` — standalone HTML
- `cache/nicheforge_demo/fargo-img/` — 12 local images
- All paths relative, copy-paste ready

## Lessons for future vibe-mode sessions

1. **Identify the template explicitly.** Write out the section sequence. Then change each one.
2. **Ask "what is this REALLY?"** — Services section is really "who does the work". Gallery is really "what does it feel like". Prices are really "is it affordable?".
3. **Inject the energy early.** User said "молодость, энергичность, красота, драйв" — this shaped EVERYTHING: palette (coral), typography (Advent Pro 900 weight), layout (skew, pulse animation), tone (short punchy bios).
4. **One weird trick per prototype.** v5 had "color swatches instead of gallery". v6 had "outline text + pulsing button". Each prototype needs one memorable WTF that breaks the template.
5. **Works in reverse too.** If 3+ iterations rejected, don't iterate. Break. Change the CONTENT MODEL (services → people), then the STRUCTURE follows.
