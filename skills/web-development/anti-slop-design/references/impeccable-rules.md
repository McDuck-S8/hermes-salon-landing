# Impeccable Design Rules (sourced from pbakaus/impeccable, 47k★)

Source: https://github.com/pbakaus/impeccable

## Core anti-AI-slop don'ts

| # | Rule | Why |
|---|------|-----|
| 1 | No editorial magenta as brand accent | AI default |
| 2 | No italic serif display typography | AI tell |
| 3 | No purple gradients or neon cyan fields | AI default |
| 4 | No glassmorphism by default | AI tell |
| 5 | No AI-tool glow effects | AI tell |
| 6 | No gold texture under long text | AI default |
| 7 | No beige/paper/cream as page background | AI default |
| 8 | No wide rounded cards or nested cards | AI tell |
| 9 | No pure black (#000) or pure white (#fff) | readability |
| 10 | No nested cards (card-inside-card) | structural anti-pattern |

## Color system (OKLCH)

Impeccable uses OKLCH color space instead of hex/rgb for perceptually uniform colors.

```css
/* Instead of #3b82f6 (tailwind blue-500) */
color: oklch(0.62 0.19 260);
```

## Design system structure

design.json contains: colors, typography, elevation, components, and a list of "Dos" and "Don'ts" targeting AI slop detection.

## Usage

Reference these rules when:
- Reviewing AI-generated UI for telltale slop patterns
- Building anti-slop-design audit checks
- Evaluating landing page quality
