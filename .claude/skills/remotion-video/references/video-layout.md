# Video Layout & Design Reference

Reference: https://www.remotion.dev/docs/video-layout

## Safe Areas (1080px wide)
```
┌─────────────────────────────────────────────────────────────┐
│ 100px top safe area                                          │
├─────────────────────────────────────────────────────────────┤
│ 80px side safe  │                                          │ 80px side safe  │
│                 │                                          │                 │
│                 │       CONTENT AREA (920px wide)         │                 │
│                 │                                          │                 │
│                 │                                          │                 │
├─────────────────────────────────────────────────────────────┤
│ 100px bottom safe area                                       │
└─────────────────────────────────────────────────────────────┘
```

## Minimum Text Sizes (1080px wide)
| Element | Min Size | Weight |
|---------|----------|--------|
| Headline | 84px | 700-900 |
| Sub-headline | 44px | 500-600 |
| Body / Labels | 32px | 400-500 |
| Captions | 28px | 500-700 |

## Layout Principles

### 1. Flex/Grid Over Absolute
```tsx
// ✅ Good
<div style={{ display: "flex", flexDirection: "column", gap: 40, alignItems: "center" }}>
  <Text>Line 1</Text>
  <Text>Line 2</Text>
</div>

// ❌ Avoid
<div style={{ position: "absolute", top: 200, left: 400 }}>
  <Text>Fixed position</Text>
</div>
```

### 2. One Focal Point Per Scene
- Single visual hierarchy
- Use TIME (sequential reveal) not SIZE to solve crowding
- 60-75ch max line length

### 3. Responsive Grids
```tsx
<div style={{
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
  gap: 40,
}}>
  {items.map(item => <Card key={item.id} {...item} />)}
</div>
```

### 4. Visual Rhythm
```tsx
// Vary spacing - don't use uniform gaps
const spacings = [20, 40, 80, 40, 20]; // rhythm
```

## Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Uniform card grids | Vary card sizes, use asymmetry |
| Tiny text on colored bg | Min 4.5:1 contrast, larger text |
| Per-char opacity for typewriter | Slice string by frame |
| CSS animations | `interpolate()` / `spring()` |
| Border-left accent stripes | Full borders, bg tints, leading numbers |
| Gradient text | Single solid color |
| Glassmorphism default | Rare, purposeful only |
| Hero metric template | Custom data visualization |
| Numbered section markers (01/02/03) | Only for real sequences |
| Tiny uppercase eyebrows on every section | One named kicker as brand system |

## Color Strategy (pick one)
1. **Restrained** - Tinted neutrals + 1 accent ≤10%
2. **Committed** - 1 saturated color 30-60% surface
3. **Full Palette** - 3-4 named roles, deliberate
4. **Drenched** - Surface IS the color

## Dark vs Light
Never default. Write physical scene sentence first:
> "User views this at 10pm in dim room, tired, needs clarity" → Dark
> "User views this on phone outdoors, noon, glancing" → Light