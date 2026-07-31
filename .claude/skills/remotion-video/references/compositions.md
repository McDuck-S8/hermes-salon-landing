# Compositions & Stills Reference

Reference: https://www.remotion.dev/docs/compositions

## Composition Registration
```tsx
// src/compositions.tsx
import { MyComp } from "./MyComp";

export const MyComposition = (
  <Composition
    id="my-video"
    component={MyComp}
    durationInFrames={180}
    fps={30}
    width={1920}
    height={1080}
    schema={MySchema}
    defaultProps={{ title: "Hello" }}
  />
);
```

## calculateMetadata (Dynamic Duration)
```tsx
import { calculateMetadata } from "remotion";

<Composition
  id="dynamic-video"
  component={MyComp}
  calculateMetadata={async ({ props }) => {
    const audioDuration = await getAudioDuration(props.audioSrc);
    return { durationInFrames: Math.ceil(audioDuration * 30) };
  }}
/>
```

## Still Frames
```bash
# Single frame
npx remotion still MyComp --frame=30 --scale=0.5

# Multiple frames
npx remotion still MyComp --frames=0,30,60,90 --scale=0.25

# Output format
npx remotion still MyComp --frame=30 --format=png --scale=1
```

## Series (All Frames)
```bash
npx remotion still MyComp --frames=0-179 --scale=0.25 --format=png
```

## Bundle (for Lambda/Cloud)
```bash
npx remotion bundle
# Creates .remotion bundle for serverless rendering
```

## Multiple Compositions
```tsx
export default [
  <Composition id="short" component={Video} durationInFrames={90} fps={30} width={1080} height={1920} />,
  <Composition id="long" component={Video} durationInFrames={540} fps={30} width={1920} height={1080} />,
];
```

## Composition Props
```tsx
<Composition
  id="my-video"
  component={MyComp}
  durationInFrames={180}
  fps={30}
  width={1920}
  height={1080}
  schema={MySchema}
  defaultProps={{ title: "Default" }}
  backgroundColor="#ffffff"
  outName="my-video"  // custom output name
/>
```