# Timing Advanced Reference

Reference: https://www.remotion.dev/docs/timing

## useVideoConfig
```tsx
const { fps, width, height, durationInFrames } = useVideoConfig();
```

## Interpolation
```tsx
import { interpolate, spring } from "remotion";

const frame = useCurrentFrame();
const { fps } = useVideoConfig();

// Linear interpolation
const opacity = interpolate(frame, [0, 30], [0, 1], { clamp: true });
const position = interpolate(frame, [0, 60], [0, 500], { easing: Easing.bezier(0.16, 1, 0.3, 1) });

// Spring
const scale = spring(frame, { fps, config: "gentle" });

// Delayed start
const delayed = interpolate(frame, [30, 90], [0, 1], { extrapolateLeft: "clamp" });
```

## Easing Functions
```tsx
import { Easing } from "remotion";

Easing.linear
Easing.in(Easing.cubic)
Easing.out(Easing.cubic)
Easing.inOut(Easing.cubic)
Easing.bezier(0.16, 1, 0.3, 1)  // Crisp entrance
Easing.bezier(0.45, 0, 0.55, 1) // Editorial
Easing.bezier(0.34, 1.56, 0.64, 1) // Playful pop
```

## Delayed Animations
```tsx
const delayFrames = 60;
const startFrame = useCurrentFrame() - delayFrames;
const progress = interpolate(startFrame, [0, 60], [0, 1], { clamp: true });
```

## Looping
```tsx
const frame = useCurrentFrame();
const { durationInFrames } = useVideoConfig();

// Loop every 60 frames
const loopFrame = frame % 60;
const progress = interpolate(loopFrame, [0, 60], [0, 1]);
```

## Time Conversions
```tsx
const { fps } = useVideoConfig();
const seconds = frame / fps;
const milliseconds = (frame / fps) * 1000;
const minutes = Math.floor(seconds / 60);
const remainingSeconds = seconds % 60;
```

## Best Practices
- All animations driven by `useCurrentFrame()` - deterministic
- Use `interpolate` for all animated values
- Clamp by default: `{ clamp: true }` or `{ extrapolateLeft: "clamp", extrapolateRight: "clamp" }`
- Prefer spring for organic, interpolate for precise