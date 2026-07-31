---
name: remotion-video
description: "Programmatic video creation with Remotion (React + FFmpeg). Compositions, transitions, captions, voiceover, audio viz, 3D, transparent export. Use for any video generation task."
trigger: "When user asks to create, render, or automate video — any format: TikTok/Reels/Shorts, explainer, data-driven, parametrized, transparent, 3D, Lottie, captions, voiceover, audio viz."
usage: remotion-video
argument-hint: "[craft|shape|init|document|extract|critique|audit|polish|bolder|quieter|distill|harden|onboard|animate|colorize|typeset|layout|delight|overdrive|clarify|adapt|optimize|live] [target]"
allowed-tools:
  - Bash(npx remotion *)
  - Bash(npx remotion studio)
  - Bash(npx remotion render *)
  - Bash(npx remotion still *)
  - Bash(npx remotion add *)
  - Bash(npx remotion ffmpeg *)
  - Bash(npx remotion ffprobe *)
  - Write(*.tsx)
  - Write(*.ts)
  - Read(*)
  - Glob(*)
---

# Remotion Video — Programmatic Video Creation

React-based video framework. Write components → render via FFmpeg. Zero-runtime, deterministic, version-controlled video.

## Quick Start

```bash
# 1. Scaffold project
npx create-video --template minimal my-video
cd my-video

# 2. Preview in Studio
npx remotion studio

# 3. Single frame check
npx remotion still MyComp --frame=30 --scale=0.25

# 4. Full render
npx remotion render MyComp out.mp4
```

## Architecture

```
my-video/
├── src/
│   ├── Component.tsx          # Your React component
│   ├── composition.tsx        # <Composition> registration
│   ├── Root.tsx               # Entry point (optional)
│   ├── schema.ts              # Zod schema for params (Studio editor)
│   └── utils/                 # Helpers
├── public/                    # Static assets (fonts, audio, images, models)
├── remotion.config.ts         # Config (webpack, fonts, etc.)
├── package.json
└── tsconfig.json
```

## Core Concepts

| Concept | Description |
|---------|-------------|
| **Composition** | A video definition: component + duration + fps + dimensions |
| **Component** | React component receiving `{frame, fps, width, height}` props |
| **Frame** | Integer 0..durationInFrames-1. Deterministic rendering. |
| **Sequence** | `<Sequence from={0} durationInFrames={60}><Scene /></Sequence>` — time-shifting |
| **calculateMetadata** | Dynamic duration/dims from props (async) |
| **Zod Schema** | Param validation + visual editor in Studio |

## Essential Imports

```tsx
import {
  Composition,
  Sequence,
  staticFile,
  Audio,
  Video,
  Image,
  AbsoluteFill,
  interpolate,
  spring,
  Easing,
  getInputProps,
  calculateMetadata,
  delayRender,
  continueRender,
  Bundle,
  Player,
  OffthreadVideo,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// Ecosystem packages (add via `npx remotion add <pkg>`):
// @remotion/transitions, @remotion/captions, @remotion/lottie,
// @remotion/three, @remotion/google-fonts, @remotion/media-utils,
// @remotion/light-leaks, @remotion/install-whisper-cpp,
// @remotion/captions, @remotion/sfx, @remotion/layout-utils,
// @remotion/light-leaks, @remotion/shapes, @remotion/paths
```

## Component Template

```tsx
interface Props {
  title: string;
  color: string;
}

export const MyScene: React.FC<Props> = ({ title, color }) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();

  // Animations via interpolate/spring
  const opacity = interpolate(frame, [0, 30], [0, 1], { clamp: true });
  const scale = spring(frame, { fps, config: "gentle" });

  return (
    <AbsoluteFill
      style={{
        background: color,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        opacity,
        transform: [{ scale }],
      }}
    >
      <Text style={{ fontSize: 84, color: "white" }}>{title}</Text>
    </AbsoluteFill>
  );
};
```

## Composition Registration

```tsx
// composition.tsx
import { MyScene } from "./MyScene";
import { calculateMetadata } from "./utils";

export const MyComp = () => (
  <Composition
    id="my-comp"
    component={MyScene}
    defaultProps={{ title: "Hello", color: "#0066ff" }}
    durationInFrames={180}
    fps={30}
    width={1920}
    height={1080}
    schema={MySchema}
    calculateMetadata={async ({ props }) => ({
      durationInFrames: Math.ceil((await getAudioDuration(props.audioSrc)) * 30),
    })}
  />
);
```

## Commands Cheatsheet

| Task | Command |
|------|---------|
| New project | `npx create-video --template minimal my-video` |
| Add package | `npx remotion add @remotion/transitions` |
| Preview | `npx remotion studio` |
| Still frame | `npx remotion still MyComp --frame=30 --scale=0.5` |
| Render | `npx remotion render MyComp out.mp4` |
| Render (transparent) | `npx remotion render --image-format=png --pixel-format=yuva444p10le --codec=prores --prores-profile=4444 MyComp out.mov` |
| WebM VP9 | `npx remotion render --image-format=png --pixel-format=yuva420p --codec=vp9 MyComp out.webm` |
| Bundle (for Lambda) | `npx remotion bundle` |
| FFmpeg direct | `npx remotion ffmpeg -i in.mp4 -c:v libx264 out.mp4` |
| FFprobe | `npx remotion ffprobe in.mp4` |
| Typecheck | `npx tsc --noEmit` |
| Lint | `npx eslint src --ext .ts,.tsx` |

## Key Patterns

### Sequence / Timing
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

### Transitions
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
// Total shortened: 60 + 60 - 15 = 105 frames
```

### Captions (TikTok-style)
```tsx
// 1. Transcribe
npx remotion add @remotion/install-whisper-cpp
import { installWhisperCpp, transcribe, toCaptions } from "@remotion/install-whisper-cpp";

// 2. Display
npx remotion add @remotion/captions
import { createTikTokStyleCaptions } from "@remotion/captions";

const { pages } = createTikTokStyleCaptions({
  captions, // from toCaptions()
  combineTokensWithinMilliseconds: 1200,
});
// Map pages to <Sequence> with word highlighting
```

### Voiceover (AI TTS)
```bash
# Generate per-scene audio via ElevenLabs → save to public/voiceover/
# Use calculateMetadata to set duration from audio
```

### Audio Visualization
```tsx
import { useWindowedAudioData, visualizeAudio } from "@remotion/media-utils";

const { audioData, dataOffsetInSeconds } = useWindowedAudioData({
  src: staticFile("music.mp3"),
  frame, fps, windowInSeconds: 30,
});

const frequencies = visualizeAudio({
  fps, frame, audioData, numberOfSamples: 256,
  optimizeFor: "speed", dataOffsetInSeconds,
});
// frequencies[0..31] = bass, rest = mids/highs. Values 0-1.
```

### 3D with Three.js
```bash
npx remotion add @remotion/three
```
```tsx
import { ThreeCanvas } from "@remotion/three";
// Use <ThreeCanvas width={w} height={h}> — NOT <Canvas>
// All animation via useCurrentFrame(). useFrame() from R3F FORBIDDEN.
```

### Lottie
```bash
npx remotion add @remotion/lottie
```
```tsx
import { Lottie } from "@remotion/lottie";
const data = await fetch(jsonUrl).then(r => r.json());
<Lottie animationData={data} />
```

### Transparent Video
```bash
# ProRes (editing)
npx remotion render --image-format=png --pixel-format=yuva444p10le --codec=prores --prores-profile=4444 MyComp out.mov

# WebM VP9 (web)
npx remotion render --image-format=png --pixel-format=yuva420p --codec=vp9 MyComp out.webm
```

### Fonts
```bash
npx remotion add @remotion/google-fonts
```
```tsx
import { loadFont } from "@remotion/google-fonts/Montserrat";
const { fontFamily } = loadFont("normal", { weights: ["400", "700"], subsets: ["latin"] });
```

### Text Animation
```tsx
import { fitText } from "@remotion/layout-utils";
const { fontSize } = fitText({ text: "Hello", withinWidth: 600, fontFamily: "Inter" });
// Typewriter: slice string by frame. No per-char opacity.
```

### Sound Effects
```tsx
import { Audio } from "@remotion/sfx";
<Audio src="https://remotion.media/whoosh.wav" />
// Available: whoosh, whip, page-turn, switch, mouse-click, ding, vine-boom, record-scratch, dramatic-boomer, +20
```

## Anti-Patterns (Forbidden)

| ❌ Don't | ✅ Do |
|----------|-------|
| `useFrame()` from R3F | `useCurrentFrame()` from Remotion |
| Per-char opacity for typewriter | Slice string by frame |
| CSS animations | `interpolate()` / `spring()` |
| Dynamic `setTimeout` | Frame-based logic |
| `<Canvas>` from R3F | `<ThreeCanvas>` from @remotion/three |
| Absolute positioning for layout | Flex/Grid, absolute only for decorative |

## Parametrized Videos (Zod)

```tsx
import { z } from "zod";
import { zColor } from "remotion";

export const Schema = z.object({
  title: z.string().min(1).max(50),
  color: zColor(),
  count: z.number().int().min(1).max(100),
});

// Pass schema={Schema} to <Composition> for visual editor in Studio
```

## Reference Files (load when needed)

| Topic | File |
|-------|------|
| Layout & design | `references/video-layout.md` |
| Transitions | `references/transitions.md` |
| Captions pipeline | `references/captions.md` |
| Voiceover + TTS | `references/voiceover.md` |
| Audio viz | `references/audio-visualization.md` |
| SFX list | `references/sfx.md` |
| Timing advanced | `references/timing.md` |
| 3D with Three.js | `references/3d.md` |
| Lottie | `references/lottie.md` |
| Local fonts | `references/local-fonts.md` |
| Text measurement | `references/text-measurement.md` |
| Media info | `references/media-info.md` |
| GIFs/animated images | `references/gifs.md` |
| Light leaks | `references/light-leaks.md` |
| Silence detection | `references/silence-detection.md` |
| HTML in Canvas | `references/html-in-canvas.md` |
| Maps (MapLibre) | `references/maps.md` |
| Transparent video | `references/transparent-video.md` |
| Compositions | `references/compositions.md` |
| Parameters | `references/parameters.md` |
| Sequencing | `references/sequencing.md` |
| Trimming | `references/trimming.md` |

## Verification

Every generated file passes `subagent_verifier`:

- Frontmatter complete
- No placeholder text (TODO, FIXME, etc.)
- No fabricated output
- No hallucinated commands
- Skill sections present
- Topic index present
- Anti-patterns table present

---

## Core Mental Models

1. **Frame Determinism** — Every frame renders identically given same inputs. No randomness, no side effects.
2. **React as Timeline** — Components = scenes. Props = parameters. Frame = time. Composition = video.
3. **Code Over Config** — Video logic lives in TypeScript/React, not timeline editors. Version control, CI, diffs work naturally.

## Key Frameworks & Decision Rules

| Framework | Purpose | When to Apply |
|-----------|---------|---------------|
| **Composition Pattern** | Define video as component + duration + fps + dims | Every video |
| **Sequence Timing** | Time-shift scenes via `<Sequence from={} durationInFrames={}>` | Multi-scene videos |
| **TransitionSeries** | Add cross-fades, slides, custom transitions | Scene changes |
| **Zod Schema** | Validate params + enable Studio visual editor | Parametrized videos |
| **calculateMetadata** | Dynamic duration from audio/assets | Data-driven length |

## Topic Index

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Core Concepts](#core-concepts)
- [Essential Imports](#essential-imports)
- [Component Template](#component-template)
- [Composition Registration](#composition-registration)
- [Commands Cheatsheet](#commands-cheatsheet)
- [Key Patterns](#key-patterns)
- [Anti-Patterns](#anti-patterns-forbidden)
- [Parametrized Videos](#parametrized-videos-zod)
- [Reference Files](#reference-files-load-when-needed)
- [Verification](#verification)