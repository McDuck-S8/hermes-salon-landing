# Captions Reference

Reference: https://www.remotion.dev/docs/captions

## Install
```bash
npx remotion add @remotion/captions
npx remotion add @remotion/install-whisper-cpp
```

## Pipeline
```
Audio/Video → Whisper.cpp → JSON → @remotion/captions → TikTok-style captions
```

## Step 1: Transcribe with Whisper.cpp
```bash
npx remotion add @remotion/install-whisper-cpp
```

```ts
// scripts/transcribe.ts
import { installWhisperCpp, downloadWhisperModel, transcribe, toCaptions } from "@remotion/install-whisper-cpp";

await installWhisperCpp();
await downloadWhisperModel("base");

const result = await transcribe({
  input: "public/audio.mp3",
  model: "base",
  output: "public/captions.json",
});

const captions = toCaptions(result);
```

## Step 2: Display Captions (TikTok-style)
```tsx
import { createTikTokStyleCaptions } from "@remotion/captions";

const { pages } = createTikTokStyleCaptions({
  captions, // from toCaptions()
  combineTokensWithinMilliseconds: 1200,
});

// Map pages to Sequence components
pages.map((page, i) => (
  <Sequence key={i} from={page.from} durationInFrames={page.duration}>
    {page.tokens.map((token, j) => (
      <Text key={j} style={token.isActive ? activeStyle : inactiveStyle}>
        {token.text}
      </Text>
    ))}
  </Sequence>
))
```

## Import from SRT
```tsx
import { parseSrt } from "@remotion/captions";

const captions = parseSrt({ input: srtText });
```

## Styling Tips
- Word-by-word highlighting: use `token.isActive`
- Color active word differently
- Add bounce/scale animation on word activation
- Safe area: keep captions within 80% width, 85% height