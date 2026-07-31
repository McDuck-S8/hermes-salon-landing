# Voiceover Reference

Reference: https://www.remotion.dev/docs/voiceover

## Workflow
```
Script → ElevenLabs API → public/voiceover/ → <Audio> → calculateMetadata → duration
```

## ElevenLabs TTS (Recommended)
```ts
// scripts/generate-voiceover.ts
const ELEVENLABS_API_KEY = process.env.ELEVENLABS_API_KEY;
const VOICE_ID = "21m00Tcm4TlvDq8ikWAM"; // Rachel

async function generateVoiceover(text: string, outputPath: string) {
  const response = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}`, {
    method: "POST",
    headers: { "xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json" },
    body: JSON.stringify({ 
      text, 
      model_id: "eleven_multilingual_v2", 
      voice_settings: { stability: 0.5, similarity_boost: 0.75 } 
    }),
  });
  const buffer = await response.arrayBuffer();
  await fs.writeFile(outputPath, Buffer.from(buffer));
}
```

## Dynamic Duration with calculateMetadata
```tsx
import { calculateMetadata } from "remotion";

<Composition
  id="VoiceoverScene"
  component={VoiceoverScene}
  calculateMetadata={async ({ props }) => {
    const duration = await getAudioDuration(props.voiceoverPath);
    return { durationInFrames: Math.ceil(duration * 30) };
  }}
/>
```

## Free Alternatives
- **Edge TTS** (Microsoft): `edge-tts --text "text" --voice en-US-AriaNeural --write-media output.mp3`
- **Coqui TTS**: Local, open-source
- **Piper TTS**: Fast, lightweight, runs locally

## Audio in Composition
```tsx
import { Audio } from "remotion";

<Audio src={staticFile("voiceover/scene1.mp3")} />
// Props: volume, playbackRate, trimBefore, trimAfter, loop, muted, toneFrequency
```

## Lip Sync (Advanced)
- Use `useVideoConfig()` + `useCurrentFrame()` to sync mouth shapes
- Consider `@remotion/lipsync` (community) or manual frame-based approach