---
name: landscape-transparency-layers
description: "Military-style multi-layered knowledge map: Landscape (fundamental keys) + Transparency layers (Situation, Plans, Logistics). Implements the architecture from user discussion: base map that never changes + overlay sheets that get replaced."
version: "1.0.0"
---

# Landscape + Transparency Layers Knowledge Architecture

## Core Concept

Military maps use a base map (terrain) + transparent overlay sheets (situation, plans, logistics). Same for knowledge:

- **Landscape (Layer 0)**: Fundamental keys — traffic sources, monetization models, payment systems, human needs. High confidence (0.9+), years expiration.
- **Situation (Layer 1)**: Current services, their status, risks. Medium confidence (0.6-0.8), weeks-months expiration.
- **Plans (Layer 2)**: Connection arrows with ROI/probability. Lower confidence (0.4-0.7), days-weeks expiration.
- **Logistics (Layer 3)**: Resources needed for plans. Variable confidence, short expiration.

When situation changes -> replace only Situation layer. Landscape stays.

## Database Schema

Tables use existing `kc_entries` and `experiences` with new fields:

### kc_entries additions:
- `layer_type`: 'landscape' | 'situation' | 'plans' | 'logistics'
- `overlay_on`: JSON array of landscape keys this layer overlays
- `geometry`: For plans — from->to connections with metadata

### experiences additions:
- Same layer_type field for session learnings

## Implementation

### 1. Landscape Keys (Fundamental)

```yaml
type: landscape
name: "Источник трафика: короткие видео"
essence: "Люди потребляют короткие вертикальные видео. Алгоритмы продвигают удерживающий контент."
confidence: 0.95
expiration_date: "2028-01-01"
tags: [traffic, video, short-form, algorithm]
verification_method: "historical_pattern"
```

### 2. Situation Keys (Current State)

```yaml
type: situation
name: "TikTok доступность в РФ"
overlay_on: ["Источник трафика: короткие видео"]
current_state: "works_with_vpn"
risk_level: "high"
confidence: 0.7
expiration_date: "2026-08-01"
tags: [platform, tiktok, geo, ru, risk]
```

### 3. Plan Keys (Connections)

```yaml
type: plans
name: "YouTube Shorts -> GitHub Pages -> 1win (RU)"
overlay_on: ["Источник трафика: короткие видео", "Монетизация: CPA беттинг"]
arrows:
  - from: "YouTube Shorts"
    to: "GitHub Pages"
    to: "1win"
    geo: "RU"
    expected_roi: 2.4
    probability: 0.85
    blocking_factors: []
confidence: 0.6
expiration_date: "2026-07-23"
tags: [plan, connection, roi, probability]
```

### 4. Logistics Keys (Resources)

```yaml
type: logistics
name: "Креативы для беттинга"
overlay_on: ["Планы: YouTube Shorts -> 1win"]
status: "critical_gap"
required_for: ["YouTube Shorts -> GitHub Pages -> 1win"]
confidence: 0.9
expiration_date: "2026-07-30"
tags: [resource, creative, bottleneck]
```

## API

```python
from landscape_layers import LandscapeMap

# Build landscape map
landscape = LandscapeMap(cube_path="knowledge_cube.db")

# Add landscape key (permanent)
landscape.add_landscape(
    name="Источник трафика: короткие видео",
    essence="...",
    confidence=0.95
)

# Add situation (replaceable)
landscape.add_situation(
    name="TikTok статус",
    overlay_on=["Источник трафика: короткие видео"],
    current_state="works_with_vpn",
    confidence=0.7
)

# Add plan (arrow)
landscape.add_plan(
    name="Shorts -> 1win",
    overlay_on=["traffic:shorts", "monetization:cpa_betting"],
    arrows=[{"from": "YouTube Shorts", "to": "1win", "prob": 0.85}],
    confidence=0.6
)

# Query: compose full picture
full_map = landscape.compose(
    landscape_filter={"tag": "traffic"},
    situation_filter={"risk": "high"},
    plans_filter={"probability": ">0.5"}
)
```

## Benefits

1. **Knowledge persistence**: Landscape never lost when situation changes
2. **Fast updates**: Replace only affected transparency layer
3. **Composable queries**: Overlay any combination of layers
4. **Expiration management**: Auto-cleanup of stale situation/plans
5. **Agent-native**: Each layer has confidence -> agent can reason about uncertainty

## Integration Points

- **Fractal Wheel Mode 1** (Analysis) -> reads Landscape for fundamental aspects
- **Fractal Wheel Mode 2** (Synthesis) -> reads Situation + Landscape to propose Plans
- **Fractal Wheel Mode 3** (Euler) -> uses Plans + Situation to find Golden Sections
- **Key Strength Estimator** -> uses all layers for Viability/Cohesion/Growth
- **Ghost-Surfer** -> Situation layer: live service status (TikTok working/blocked), Plans layer: connection arrows with ROI/probability from real platform data, Logistics layer: creative/account gaps from actual registration attempts