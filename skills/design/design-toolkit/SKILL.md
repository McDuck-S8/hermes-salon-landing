---
name: design-toolkit
description: "Unified design toolkit for Hermes: hallmark (anti-AI-slop) + claude-design + design-md + popular-web-designs + anti-slop-design. One skill to load, all design engines at hand."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, hallmark, anti-slop, ui, ux, design-system, tokens, html, prototype]
    related_skills: [hallmark, claude-design, design-md, popular-web-designs, anti-slop-design, creative-toolkit, architecture-diagram, excalidraw, dashboard-design, sketch, pretext]
  skill_updated: "2026-07-24"
  created_by: "auto_patch_g007"
  component_skills:
    - hallmark
    - claude-design
    - design-md
    - popular-web-designs
    - anti-slop-design
---

# Design Toolkit — Unified Interface

**One skill to load. All design engines. Zero context switching.**

This meta-skill wraps all core design skills into a single loadable unit with a unified workflow interface.

## Quick Start

```python
# Load once, get all 5 engines
from hermes_tools import skill_view
skill_view("design/design-toolkit")

# Now you have:
# - hallmark (anti-AI-slop design skill for greenfield pages, audits, redesigns)
# - claude-design (design one-off HTML artifacts: landing, deck, prototype)
# - design-md (Google's DESIGN.md token spec: author/validate/export)
# - popular-web-designs (54 real design systems: Stripe, Linear, Vercel, etc.)
# - anti-slop-design (Three Dials system, AI-tell detection)
```

## Component Skills Map

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| **hallmark** | Anti-AI-slop design for greenfield pages, audits, redesigns, studies | Default for any design work — enforces structural variety, honest copy, locked tokens, mobile responsiveness, typography purity |
| **claude-design** | Design one-off HTML artifacts (landing, deck, prototype) | When user wants a rendered artifact, not a design system |
| **design-md** | Google's DESIGN.md token spec: author/validate/diff/export | When deliverable is a token spec file, not a rendered artifact |
| **popular-web-designs** | 54 ready-to-paste design systems (Stripe, Linear, Vercel, etc.) | "Make it look like Stripe/Linear/Vercel" |
| **anti-slop-design** | Three Dials system (Structure/Detail/Tone), AI-tell detection | Quality gate for any design output |

## Unified Design Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. CHOOSE ENGINE (by deliverable)                               │
│                                                                   │
│   Rendered page/artifact?     → hallmark (default)              │
│   "Make it look like X"?      → popular-web-designs + hallmark  │
│   Token spec file (DESIGN.md)? → design-md                       │
│   One-off HTML artifact?       → claude-design                   │
│   Quality gate on output?      → anti-slop-design                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. HALLMARK DESIGN FLOW (default)                               │
│                                                                  │
│   0. Pre-flight scan → read design.md, tokens, fonts, motion,  │
│      spacing, framework                                         │
│   1. Design-context gate → Audience + Use case + Tone (ask!)    │
│   2. Pick macrostructure FIRST (21 named)                       │
│      → Diversification: different from last run                 │
│   2.5. Genre detect (editorial/modern-minimal/atmospheric/playful)│
│   2.6. Theme route: catalog (20 themes) vs custom (brand anchor)│
│   3. Nav (N1a-N13) + Footer (Ft1-Ft8) — diversify!             │
│   4. Enrichment archetype (E1-E15)                              │
│   5. Preview block → Slop test (58 gates)                       │
│   6. Build → Stamp → tokens.css → log.json                      │
│   7. Slop test: 58 gates, all must pass                         │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Commands Reference

### Hallmark (default design flow)
```python
# Full page design
# → hallmark picks macrostructure, theme, nav, footer, enrichment
# → runs 58-gate slop test
# → emits HTML + CSS + tokens.css + log.json

# Audit
hallmark audit <target>  # scores against anti-patterns, no edits

# Redesign
hallmark redesign <target> [--mood <name>]  # keeps content/IA, redesigns visual

# Study
hallmark study <screenshot|URL>  # extracts DNA → diagnosis → rebuild with DNA
```

### Popular Web Designs (brand match)
```python
# 54 systems: Stripe, Linear, Vercel, Notion, Airbnb, Figma, GitHub, Discord, etc.
# Each: HTML + CSS + design tokens + components
# Use with hallmark for process + popular-web-designs for visual vocabulary
```

### Design.md (token spec)
```yaml
# Google's DESIGN.md format
# Author/validate/diff/export
# Export: CSS custom properties, Tailwind v4 @theme, DTCG tokens.json, shadcn/ui CSS variables
# WCAG 2.1 AA contrast checking built-in
```

### Anti-Slop Design (quality gate)
```python
# Three Dials: Structure × Detail × Tone
# AI-tell detection: "utilize" → "use", "leverage" → "use", "delve" → "explore"
# Slop-test: 100+ gates
```

## Integration with Knowledge Cube

```python
from scripts.event_evolution import on_task_complete

on_task_complete(
    content="Design complete: hallmark Marquee Hero + Bloom theme + N5 nav + Ft5 footer. 58/58 slop gates passed. tokens.css exported.",
    tags=["design", "hallmark", "marquee-hero", "bloom", "slop-test-passed", "success"],
    source="agent"
)
```

## Frontend Design Methodology (Anthropic)

См. `references/frontend-design-methodology.md`

**Мои шаблоны (обходить):**
- ❌ Тёмный фон + фиолетовый градиент + Inter (мой дефолт)
- ❌ Hero: stats grid + gradient button + центрированный текст
- ❌ Три одинаковые карточки в ряд
- ❌ Gradient-blob / bg-glow

**Процесс:** Определи нишу → выбери визуальный язык (см. NicheForge) → token system → self-critique → build

**visual language NOT in use = template. Template = rejection.**

**На нишу — свой визуальный язык.** До 5–7 вариантов на нишу. Отличаются layout, иерархией, типом, плотностью — не только цветом.

## NicheForge — дизайн под нишу

См. `references/niche-forge.md`

**Вместо шаблона — визуальный язык под конкретную нишу.**
- 10 языков: laboratory, editorial, terminal, dashboard, journal, nature, luxury, brutalist, playlist, cinema
- Каждый язык: своя метафора, палитра, шрифты, layout, signature
- Теоретически: 60,000+ уникальных комбинаций

**Процесс:**
1. Определи нишу
2. Выбери визуальный язык (nearest match)
3. Палитра (4 цвета) + Шрифты (2 роли) + Layout + Signature
4. Signature-элемент — единственная смелость, остальное сдержанно

**Инструмент:** `python tools/niche_designer.py --niche "..." --out page.html`

## Anti-Patterns (from 16 design failures)

| Anti-Pattern | Guard |
|--------------|-------|
| Specimen macrostructure default | Diversification rule: different macrostructure every run |
| Invented metrics/testimonials | Honest copy discipline: no fabricated numbers |
| Mid-render token improvisation | Locked tokens: all colors/fonts via named tokens |
| Re-drawn UI chrome (fake browser bars) | Real screenshots or no chrome |
| Italic headers | Typography purity: headers always roman |
| Mobile overflow | Mobile non-negotiables: 4 widths, no horizontal scroll |
| Two-column hanging tags | Vertical tag stacking only (gate 54) |
| Template repetition (same nav/footer) | Nav/footer diversification mandatory |

## Verification Checklist

After using this toolkit:
- [ ] Correct engine chosen for deliverable
- [ ] Hallmark pre-flight scan completed
- [ ] Audience + Use case + Tone asked/answered
- [ ] Macrostructure picked (different from last run)
- [ ] Theme route chosen (catalog vs custom)
- [ ] Nav + Footer archetypes picked (diversified)
- [ ] Preview block emitted with all 7 rows
- [ ] Slop test: 58/58 gates passed
- [ ] Stamp emitted in CSS
- [ ] tokens.css written
- [ ] log.json updated
- [ ] KC entry created with tags

---

**Origin:** g-007 Unlock: design (39 entries, 16 failures, 3 successes)
**Created:** 2026-07-24 via auto_patch_g007
**Source:** Knowledge Cube domain `design` + all 5 component skills