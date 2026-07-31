# SFX (Sound Effects) Reference

Reference: https://www.remotion.dev/docs/sfx

## Install
```bash
npx remotion add @remotion/sfx
```

## Usage
```tsx
import { Audio } from "@remotion/sfx";

<Audio src="https://remotion.media/whoosh.wav" />
```

## Available Effects
| Effect | Description |
|--------|-------------|
| `whoosh.wav` | Fast movement |
| `whip.wav` | Sharp crack |
| `page-turn.wav` | Page flip |
| `switch.wav` | Toggle/switch |
| `mouse-click.wav` | Click |
| `ding.wav` | Notification |
| `vine-boom.wav` | Vine boom meme |
| `record-scratch.wav` | Record scratch |
| `dramatic-boomer.wav` | Dramatic boom |
| `pop.wav` | Pop |
| `swoosh.wav` | Smooth movement |
| `thud.wav` | Heavy impact |
| `bell.wav` | Bell |
| `chime.wav` | Chime |
| `magic.wav` | Magic sparkle |
| `error.wav` | Error |
| `success.wav` | Success |
| `warning.wav` | Warning |
| `notification.wav` | Notification |
| `typewriter.wav` | Typewriter |

## Usage with Timing
```tsx
import { useCurrentFrame, interpolate } from "remotion";

const SFX = ({ triggerFrame, src }) => {
  const frame = useCurrentFrame();
  const shouldPlay = frame >= triggerFrame && frame < triggerFrame + 1;
  
  return shouldPlay ? <Audio src={src} /> : null;
};

// Usage
<SFX triggerFrame={30} src="https://remotion.media/whoosh.wav" />
```

## Props
| Prop | Type | Description |
|------|------|-------------|
| `src` | `string` | URL or staticFile path |
| `volume` | `number` | 0-1 |
| `playbackRate` | `number` | Speed |
| `muted` | `boolean` | Mute |
| `loop` | `boolean` | Loop |
| `toneFrequency` | `number` | Pitch (render only) |
| `trimBefore` | `number` | Frames to trim start |
| `trimAfter` | `number` | Frames to trim end |