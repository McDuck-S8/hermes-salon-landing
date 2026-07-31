# Trimming Patterns Reference

Reference: https://www.remotion.dev/docs/trimming

## Trim Video/Audio Start/End
```tsx
<Video
  src={staticFile("video.mp4")}
  trimBefore={2 * fps}   // Skip first 2 seconds
  trimAfter={10 * fps}   // Skip last 10 seconds
/>
<Audio
  src={staticFile("audio.mp3")}
  trimBefore={1 * fps}
  trimAfter={5 * fps}
/>
```

## Trim Animation (Sequence)
```tsx
// Start animation 15 frames early (off-screen)
<Sequence from={-15}><MyAnimation /></Sequence>

// End animation 15 frames early
<Sequence durationInFrames={45}><MyAnimation /></Sequence>
```

## Trim Composition (Dynamic)
```tsx
<Composition
  id="TrimmedVideo"
  component={MyComp}
  calculateMetadata={async ({ props }) => {
    const totalDuration = await getVideoDuration(props.videoSrc);
    const start = props.trimStart || 0;
    const end = props.trimEnd || totalDuration;
    return { durationInFrames: Math.ceil((end - start) * 30) };
  }}
/>
```

## Trim in Sequence (Relative)
```tsx
<Sequence from={0} durationInFrames={60}>
  <Video src={staticFile("clip.mp4")} trimBefore={15} trimAfter={10} />
</Sequence>
// Video plays frames 15-55 of the 60-frame sequence
```

## Key Points
- `trimBefore` / `trimAfter` on Video/Audio components
- `from={-N}` on Sequence to start animation early
- `durationInFrames` on Sequence to cut early
- All trim values in FRAMES, not seconds