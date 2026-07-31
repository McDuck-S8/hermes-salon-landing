# Transitions Reference

Reference: https://www.remotion.dev/docs/transitions

## Install
```bash
npx remotion add @remotion/transitions
```

## Core Concept
Transitions SHORTEN total duration: `sceneA + sceneB - transition = total`

## Basic TransitionSeries
```tsx
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";

<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={60}><SceneA /></TransitionSeries.Sequence>
  <TransitionSeries.Transition
    presentation={fade()}
    timing={linearTiming({ durationInFrames: 15 })}
  />
  <TransitionSeries.Sequence durationInFrames={60}><SceneB /></TransitionSeries.Sequence>
</TransitionSeries>
// Total: 60 + 60 - 15 = 105 frames
```

## Available Transitions

| Transition | Import | Parameters |
|------------|--------|------------|
| fade | `@remotion/transitions/fade` | `color?: string` |
| slide | `@remotion/transitions/slide` | `direction: "from-left" \| "from-right" \| "from-top" \| "from-bottom"` |
| wipe | `@remotion/transitions/wipe` | `direction: "from-left" \| "from-right" \| "from-top" \| "from-bottom"` |
| flip | `@remotion/transitions/flip` | `axis: "x" \| "y"` |
| clockWipe | `@remotion/transitions/clock-wipe` | - |
| iris | `@remotion/transitions/iris` | `shape: "circle" \| "rect"` |

## Timing Functions
```tsx
import { linearTiming, springTiming, easingTiming } from "@remotion/transitions";

linearTiming({ durationInFrames: 15 })
springTiming({ durationInFrames: 30, stiffness: 170, damping: 26 })
easingTiming({ durationInFrames: 15, easing: Easing.bezier(0.16, 1, 0.3, 1) })
```

## Overlay Transitions
```tsx
<TransitionSeries.Overlay
  presentation={fade()}
  timing={linearTiming({ durationInFrames: 15 })}
/>
```

## Custom Presentation
```tsx
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { interpolate } from "remotion";

const customFade = () => ({
  getPresentationFrame: (frame) => (
    <AbsoluteFill style={{ opacity: interpolate(frame, [0, 15], [1, 0]) }} />
  ),
});

<TransitionSeries.Transition presentation={customFade()} timing={linearTiming({ durationInFrames: 15 })} />
```