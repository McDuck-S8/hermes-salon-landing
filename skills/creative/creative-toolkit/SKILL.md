---
name: creative-toolkit
description: "Unified creative toolkit for Hermes: baoyu-article-illustrator + baoyu-comic + baoyu-infographic + architecture-diagram + ascii-art + ascii-video + excalidraw + manim-video + p5js + pixel-art + popular-web-designs + pretext + sketch + songwriting-and-ai-music + touchdesigner-mcp + design-md + creative-ideation. One skill to load, 17 engines at hand."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [creative, illustration, comic, infographic, diagram, ascii, video, manim, p5js, pixel-art, design, music, touchdesigner, ideation]
    related_skills: [baoyu-article-illustrator, baoyu-comic, baoyu-infographic, architecture-diagram, ascii-art, ascii-video, excalidraw, manim-video, p5js, pixel-art, popular-web-designs, pretext, sketch, songwriting-and-ai-music, touchdesigner-mcp, design-md, creative-ideation]
  skill_updated: "2026-07-24"
  created_by: "auto_patch_g007"
  component_skills:
    - baoyu-article-illustrator
    - baoyu-comic
    - baoyu-infographic
    - architecture-diagram
    - ascii-art
    - ascii-video
    - excalidraw
    - manim-video
    - p5js
    - pixel-art
    - popular-web-designs
    - pretext
    - sketch
    - songwriting-and-ai-music
    - touchdesigner-mcp
    - design-md
    - creative-ideation
---

# Creative Toolkit — Unified Interface

**One skill to load. 17 creative engines. Zero context switching.**

This meta-skill wraps all core creative skills into a single loadable unit with a unified workflow interface.

## Quick Start

```python
# Load once, get all 17 tools
from hermes_tools import skill_view
skill_view("creative/creative-toolkit")

# Now you have:
# - baoyu-article-illustrator (article illustrations: type × style × palette)
# - baoyu-comic (knowledge comics: educational, biography, tutorial)
# - baoyu-infographic (infographics: 21 layouts × 21 styles)
# - architecture-diagram (dark-themed SVG/HTML architecture diagrams)
# - ascii-art (pyfiglet, cowsay, boxes, image-to-ascii)
# - ascii-video (colored ASCII MP4/GIF from video/audio)
# - excalidraw (hand-drawn JSON diagrams: arch, flow, seq)
# - manim-video (3Blue1Brown math/algo animations)
# - p5js (gen art, shaders, interactive, 3D)
# - pixel-art (era palettes: NES, Game Boy, PICO-8)
# - popular-web-designs (54 real design systems: Stripe, Linear, Vercel)
# - pretext (browser demos with @chenglou/pretext)
# - sketch (throwaway HTML mockups: 2-3 variants to compare)
# - songwriting-and-ai-music (craft + Suno prompts)
# - touchdesigner-mcp (control running TouchDesigner via MCP)
# - design-md (Google DESIGN.md token spec authoring)
# - creative-ideation (constraint-based project ideas)
```

## Component Skills Map

| Skill | Output Type | Best For |
|-------|-------------|----------|
| **baoyu-article-illustrator** | HTML/CSS illustrations | Article headers, blog posts, social media |
| **baoyu-comic** | Multi-panel comics (JSON/HTML) | Educational content, biographies, tutorials |
| **baoyu-infographic** | 21 layouts × 21 styles | Data viz, process flows, comparisons |
| **architecture-diagram** | Dark-themed SVG/HTML | Cloud infra, system arch, network topology |
| **ascii-art** | Text/ANSI | Terminal UI, logs, README badges |
| **ascii-video** | Colored ASCII MP4/GIF | Terminal demos, retro aesthetics |
| **excalidraw** | Hand-drawn JSON | Architecture, flowcharts, sequence diagrams |
| **manim-video** | Math/algo animations (MP4) | Educational, 3Blue1Brown style |
| **p5js** | Interactive web sketches | Generative art, shaders, 3D, interactive |
| **pixel-art** | Era-palette sprites | Game assets, retro UI, NES/GB/PICO-8 |
| **popular-web-designs** | HTML/CSS (54 systems) | Reference, inspiration, component extraction |
| **pretext** | Browser demos | Live code presentations, interactive docs |
| **sketch** | Throwaway HTML mockups | Rapid comparison (2-3 variants) |
| **songwriting-and-ai-music** | Suno prompts + craft | Music generation, lyrics, structure |
| **touchdesigner-mcp** | Live TD control | Real-time visuals, installations, performance |
| **design-md** | DESIGN.md token specs | Design system documentation |
| **creative-ideation** | Project ideas + constraints | Breaking creative blocks |

## Unified Creative Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. IDEATE (creative-ideation)                                   │
│    • Constraint-based generation                                │
│    • "Landing page for X with Y constraint"                     │
│    • Output: 3-5 concrete concepts with specs                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. SKETCH (sketch) — RAPID COMPARISON                           │
│    • 2-3 HTML mockups, same content, different approaches       │
│    • Compare side-by-side, pick direction                       │
│    • Time-box: 15-30 min per variant                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. EXECUTE (pick engine by output type)                         │
│                                                                  │
│    Article illustration?  → baoyu-article-illustrator           │
│    Educational comic?     → baoyu-comic                         │
│    Data infographic?      → baoyu-infographic                   │
│    System diagram?        → architecture-diagram                │
│    Hand-drawn feel?       → excalidraw                          │
│    Math animation?        → manim-video                         │
│    Generative/interactive? → p5js                              │
│    Retro pixel art?       → pixel-art                           │
│    Reference/inspiration? → popular-web-designs                 │
│    Live demo?             → pretext                             │
│    Music/Suno?            → songwriting-and-ai-music            │
│    Real-time visuals?     → touchdesigner-mcp                   │
│    Design tokens?         → design-md                           │
│    ASCII/terminal?        → ascii-art / ascii-video             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. ITERATE & POLISH                                             │
│    • Refine chosen variant                                      │
│    • Consistency check: type × style × palette (baoyu)          │
│    • Export: HTML/SVG/MP4/JSON as needed                        │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Commands Reference

### Baoyu Suite (consistent style system)
```python
# Article illustration: type × style × palette
# Types: hero, concept, process, comparison, data, quote
# Styles: flat, line, gradient, 3d, hand-drawn, minimal
# Palettes: brand, mono, pastel, dark, vibrant, earth

# Comic: educational / biography / tutorial
# Panels: 4-12, consistent character style

# Infographic: 21 layouts × 21 styles
# Layouts: timeline, process, comparison, hierarchy, geo, etc.
# Styles: corporate, editorial, technical, minimal, vibrant, etc.
```

### Architecture Diagrams
```bash
# Dark-themed SVG/HTML output
# Components: cloud, k8s, database, queue, cache, api, client
# Connections: sync, async, streaming, batch
# Auto-layout with manual override
```

### ASCII / Video
```bash
# ASCII art
python -m ascii_art "HERMES" --font=big --color=cyan

# Image to ASCII
python -m ascii_art image.png --width=120 --color

# ASCII video
python -m ascii_video input.mp4 --output=ascii.mp4 --color --fps=10
```

### p5js (Generative/Interactive)
```javascript
// sketch.js
function setup() { createCanvas(800, 600); }
function draw() { /* generative art / shader / 3D */ }
```
```bash
npx p5 serve sketch.js  # Live reload
npx p5 build sketch.js  # Static export
```

### Pixel Art (Era Palettes)
```bash
# Palettes: NES, Game Boy, Game Boy Color, PICO-8, Commodore 64, ZX Spectrum
# Output: PNG spritesheets, CSS variables, aseprite files
```

### Popular Web Designs (54 Systems)
```bash
# Stripe, Linear, Vercel, Notion, GitHub, Figma, Discord, etc.
# Each: HTML + CSS + design tokens extracted
# Use for: reference, component extraction, token analysis
```

### Excalidraw (Hand-drawn)
```json
// Elements: rectangle, ellipse, diamond, arrow, line, text, image
// Style: strokeWidth, roughness, opacity, background, strokeColor
// Export: .excalidraw JSON, SVG, PNG
```

### Manim (Math Animations)
```python
# manim scene.py SceneName -pqh
# 3Blue1Brown style: Transform, ReplacementTransform, Write, Create
# Math: Tex, MathTex, NumberLine, Axes, GraphScene
```

### TouchDesigner MCP
```python
# Connect to running TD instance
# Control: OPs, parameters, DATs, TOPs, CHOPs
# Real-time: perform mode, projection mapping, installations
```

### Design.md (Token Specs)
```yaml
# Google DESIGN.md format
# Tokens: color, spacing, typography, shadow, radius, motion
# Semantic tokens
# Export: CSS custom properties, Figma tokens, iOS/Android
```

## Anti-Patterns (from 168 creative entries, 34 failures)

| Anti-Pattern | Countermeasure |
|--------------|----------------|
| Inconsistent style across assets | **baoyu**: type × style × palette system |
| Over-polishing first variant | **sketch**: 2-3 throwaway variants first |
| Wrong tool for output type | **Workflow map**: pick engine by output |
| No design token system | **design-md**: DESIGN.md + CSS variables |
| Manual diagram maintenance | **architecture-diagram** / **excalidraw**: code-driven |
| Music without structure | **songwriting**: craft first, Suno prompts second |
| ASCII without color/width control | **ascii-art**: --width, --color, --font flags |

## Integration with Knowledge Cube

After ANY creative session:

```python
from scripts.event_evolution import on_task_complete

on_task_complete(
    content="Created X: used baoyu-article-illustrator (type=hero, style=flat, palette=brand) + excalidraw for diagram. Consistent style achieved.",
    tags=["creative", "illustration", "diagram", "consistency", "success"],
    source="agent"
)
```

## Verification Checklist

After using this toolkit:
- [ ] Ideation generated 3+ constrained concepts
- [ ] Sketch produced 2-3 variants for comparison
- [ ] Correct engine selected for output type
- [ ] Style consistency verified (baoyu type×style×palette)
- [ ] Exports in required formats (HTML/SVG/MP4/JSON)
- [ ] KC entry created with tags

---

**Origin:** g-007 Unlock: creative (168 entries, 34 failures, 23 successes)
**Created:** 2026-07-24 via auto_patch_g007
**Source:** Knowledge Cube domain `creative` + all 17 component skills