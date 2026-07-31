# Audio Visualization Reference

Reference: https://www.remotion.dev/docs/audio-visualization

## Install
```bash
npx remotion add @remotion/media-utils
```

## Basic Visualization
```tsx
import { useWindowedAudioData, visualizeAudio } from "@remotion/media-utils";

const MyVisualizer = ({ audioSrc }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const { audioData, dataOffsetInSeconds } = useWindowedAudioData({
    src: staticFile("music.mp3"),
    frame,
    fps,
    windowInSeconds: 30,
  });

  const frequencies = visualizeAudio({
    fps,
    frame,
    audioData,
    numberOfSamples: 256,
    optimizeFor: "speed",
    dataOffsetInSeconds,
  });

  // frequencies[0..31] = bass (0-250Hz)
  // frequencies[32..127] = mids (250-2000Hz)
  // frequencies[128..255] = highs (2000-20000Hz)
  // Values: 0 to 1

  return (
    <div style={{ display: "flex", gap: 2, height: 200 }}>
      {frequencies.map((value, i) => (
        <div
          key={i}
          style={{
            flex: 1,
            background: `hsl(${i * 1.5}, 100%, 50%)`,
            height: `${value * 100}%`,
            minHeight: 2,
          }}
        />
      ))}
    </div>
  );
};
```

## Frequency Ranges
| Index Range | Frequency | Use Case |
|-------------|-----------|----------|
| 0-7 | 0-43 Hz | Sub-bass (felt, not heard) |
| 8-31 | 44-250 Hz | Bass (kick, bassline) |
| 32-63 | 250-500 Hz | Low-mid (body) |
| 64-127 | 500-2000 Hz | Mid (vocals, leads) |
| 128-255 | 2000-20000 Hz | High-mid to high (brilliance) |

## Beat Detection (Simple)
```tsx
const bass = frequencies.slice(0, 32).reduce((a, b) => a + b, 0) / 32;
const isBeat = bass > 0.6 && prevBass < 0.6; // Simple threshold crossing
```

## Bar Visualizer
```tsx
const Bar = ({ value, color }) => (
  <div
    style={{
      width: 4,
      height: `${value * 100}%`,
      background: color,
      borderRadius: 2,
      transition: "height 0.05s",
    }}
  />
);

<flex gap={2} alignItems="flex-end" height={200}>
  {frequencies.map((v, i) => (
    <Bar key={i} value={v} color={`hsl(${i * 1.5}, 80%, 50%)`} />
  ))}
</flex>
```

## Circular Visualizer
```tsx
const radius = 150;
const barCount = 128;

<svg width={300} height={300}>
  {frequencies.slice(0, barCount).map((value, i) => {
    const angle = (i / barCount) * Math.PI * 2 - Math.PI / 2;
    const length = value * 80;
    const x1 = 150 + Math.cos(angle) * radius;
    const y1 = 150 + Math.sin(angle) * radius;
    const x2 = 150 + Math.cos(angle) * (radius + length);
    const y2 = 150 + Math.sin(angle) * (radius + length);
    return (
      <line
        key={i}
        x1={x1} y1={y1} x2={x2} y2={y2}
        stroke={`hsl(${i * 2.8}, 80%, 50%)`}
        strokeWidth={2}
        strokeLinecap="round"
      />
    )
  })}
</svg>
```