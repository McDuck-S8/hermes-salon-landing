# Impeccable Design Workflow

> Install: `npx impeccable install` (one-time per project)
> Commands: `detect`, `document`, `craft`, `shape`, `polish`, `audit`, `live`

## PROJECT FILES

### PRODUCT.md — Strategic design context (who/what/why)

```markdown
# Product

## Register
brand          # brand=marketing/landing, product=app/tool

## Platform
web            # web, ios, android, adaptive

## Users
[Who they are, context, job to be done]

## Product Purpose
[What this does, why it exists, success = ?]

## Brand Personality
[3 words + tone]

## Anti-references
[What this should NOT look like]

## Design Principles
[3-5 strategic principles — NOT visual rules]

## Accessibility & Inclusion
[WCAG level, reduced motion, etc.]
```

### DESIGN.md — Visual tokens (Google spec)

```markdown
---
name: Project Name
description: One-liner.
colors:
  primary: "oklch(55% 0.145 40)"
  secondary: "oklch(70% 0.09 42)"
  surface: "oklch(96% 0.008 75)"
  text: "oklch(12% 0.01 75)"
typography:
  display:
    fontFamily: "'Playfair Display', Georgia, serif"
    fontSize: "clamp(2.2rem, 5.5vw, 4.5rem)"
    fontWeight: 500
    letterSpacing: "-0.01em"
    lineHeight: 1.08
  body:
    fontFamily: "'Inter', system-ui, sans-serif"
    fontSize: "1rem"
    lineHeight: 1.65
spacing:
  sm: "16px"
  md: "24px"
  lg: "40px"
  xl: "64px"
rounded:
  sm: "6px"
  md: "10px"
  lg: "16px"
  pill: "999px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "oklch(98% 0 0)"
    rounded: "{rounded.pill}"
    padding: "16px 48px"
  button-primary-hover:
    backgroundColor: "{colors.secondary}"
---
```

### Validate
```bash
npx -y @google/design.md lint DESIGN.md
```

## DETECT (anti-pattern scanner)

```bash
npx impeccable detect --file index.html
```

### Anti-patterns & fixes

| Anti-pattern | Fix |
|---|---|
| `low-contrast` — text below WCAG AA | Use OKLCH colors. Check ratios: 4.5:1 body, 3:1 large text |
| `all-caps-body` — uppercase on body text | Only short labels, never paragraphs |
| `wide-tracking` — >0.05em on body | Reserve for short uppercase labels |
| `tight-leading` — <1.3x line-height | Body: 1.5-1.7 |
| `dark-glow` — colored shadow on dark bg | AI tell. Use subtle shadows or skip dark theme |
| `em-dash-overuse` — >2 em-dashes in body | AI cadence tell. Use commas, colons |
| `cream-bg` — warm cream backgrounds | AI tell. Use OKLCH neutrals like `oklch(96% 0.008 75)` |

## KEY PRINCIPLES

- **OKLCH over hex**: Perceptually uniform. WCAG checks meaningful. Base neutrals toward anchor hue.
- **Font pairing**: Serif display + sans body. Never two similar sans-serifs.
- **Brand register** uses "brand" → design IS the product. Landing pages are brand.
- **Product register** uses "product" → design SERVES the product. Apps/tools.
- **One anchor color** at ~20% of surfaces. Everything else tinted neutrals.
- **Write complete files** in one `write_file` call. Never stop mid-stream.
- **Scroll-triggered reveal**: `IntersectionObserver` with `opacity + translateY(24px)`.
- **prefers-reduced-motion**: Disable all animations for accessibility.
