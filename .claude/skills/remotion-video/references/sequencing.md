# Sequencing Patterns Reference

Reference: https://www.remotion.dev/docs/sequencing

## Basic Sequence
```tsx
<Sequence from={0} durationInFrames={60}>
  <SceneA />
</Sequence>
<Sequence from={60} durationInFrames={60}>
  <SceneB />
</Sequence>
<Sequence from={120} durationInFrames={60}>
  <SceneC />
</Sequence>
// Total: 180 frames
```

## Series (Sequential, No Overlap)
```tsx
import { Series } from "remotion";

<Series>
  <Series.Sequence durationInFrames={45}><Intro /></Series.Sequence>
  <Series.Sequence durationInFrames={90}><Main /></Series.Sequence>
  <Series.Sequence durationInFrames={45}><Outro /></Series.Sequence>
</Series>
```

## AbsoluteFill (Full Screen)
```tsx
import { AbsoluteFill } from "remotion";

<AbsoluteFill style={{ background: "#000" }}>
  <Content />
</AbsoluteFill>
```

## Premounting (for Smooth Transitions)
```tsx
// Pre-mount 30 frames before sequence starts
<Sequence from={60} durationInFrames={60} premountFor={30} layout="none">
  <SceneB />
</Sequence>
```

## Delay Without Duration
```tsx
<Sequence from={30} layout="none">
  <DelayedComponent />
</Sequence>
// Renders at frame 30+, no fixed duration
```

## Random/Loop Sequences
```tsx
// Loop a scene
<Sequence from={0} durationInFrames={180}>
  <Loop durationInFrames={60}><AnimatedBg /></Loop>
</Sequence>

// Conditional sequence
<Sequence from={condition ? 0 : 60} durationInFrames={60}>
  <ConditionalScene />
</Sequence>
```

## Layout Modes
| Mode | Description |
|------|-------------|
| `absolute` (default) | Position absolutely, stacked |
| `relative` | Flow in normal document flow |
| `none` | No wrapper div, direct children |

## Nested Sequences
```tsx
<Sequence from={0} durationInFrames={180}>
  <Sequence from={0} durationInFrames={60}><PartA /></Sequence>
  <Sequence from={60} durationInFrames={60}><PartB /></Sequence>
  <Sequence from={120} durationInFrames={60}><PartC /></Sequence>
</Sequence>
```

## Best Practices
- Use `Series` for strictly sequential scenes
- Use `Sequence` for overlapping/timed scenes
- Always `premountFor` for heavy scenes
- Keep total duration in sync with Composition