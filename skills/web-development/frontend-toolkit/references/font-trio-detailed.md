# Font Trio — Font Pairing System

## How It Works
Font Trio provides curated 3-font pairings for shadcn/ui projects. Each pairing consists of:
- **Heading font** — for h1-h6, display text
- **Body font** — for paragraphs, descriptions
- **Mono font** — for code blocks, technical content

## Installation
```bash
# Single pairing
npx shadcn@latest add https://www.fonttrio.xyz/r/playfair-display.json

# CSS Variables (auto-generated)
--font-heading: var(--font-playfair-display);
--font-body: var(--font-source-serif-4);
--font-mono: var(--font-jetbrains-mono);
```

## Pairing Categories

### Serif Pairings
- **Editorial** — Playfair Display + Source Serif 4 + JetBrains Mono
- **Classic** — Lora + Crimson Text + Fira Code
- **Gazette** — Libre Baskerville + EB Garamond + IBM Plex Mono

### Sans-serif Pairings
- **Modern** — Inter + Inter + JetBrains Mono
- **Geometric** — Poppins + DM Sans + Space Mono
- **Humanist** — Nunito + Open Sans + Source Code Pro

### Display Pairings
- **Bold** — Space Grotesk + Space Grotesk + JetBrains Mono
- **Playful** — Fredoka + Quicksand + Fira Code
- **Tech** — JetBrains Mono + JetBrains Mono + JetBrains Mono

## Mood Tags
Each pairing has mood tags for matching:
- elegant, traditional, authoritative
- modern, clean, minimal
- playful, friendly, casual
- technical, precise, monospace

## Use Cases
- blog, editorial, magazine, documentation
- SaaS, dashboard, admin panel
- portfolio, agency, creative
- e-commerce, product, landing page
