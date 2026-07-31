# Transparent Video Export Reference

Reference: https://www.remotion.dev/docs/transparent-video

## ProRes 4444 (for editing software: Premiere, DaVinci, After Effects)
```bash
npx remotion render \
  --image-format=png \
  --pixel-format=yuva444p10le \
  --codec=prores \
  --prores-profile=4444 \
  MyComp out.mov
```

## WebM VP9 (for web overlay)
```bash
npx remotion render \
  --image-format=png \
  --pixel-format=yuva420p \
  --codec=vp9 \
  MyComp out.webm
```

## HEVC with Alpha (H.265)
```bash
npx remotion render \
  --image-format=png \
  --pixel-format=yuva420p10le \
  --codec=hevc \
  MyComp out.mov
```

## Composition Requirements
```tsx
<Composition
  id="TransparentComp"
  component={MyComp}
  durationInFrames={180}
  fps={30}
  width={1920}
  height={1080}
  backgroundColor="transparent"  // REQUIRED
/>
```

## Background Requirements
- Component MUST NOT render full-screen background color
- Use transparent backgrounds in all components
- Use `<AbsoluteFill style={{ background: "transparent" }}>` if needed

## Verify Transparency
```bash
npx remotion still MyComp --frame=30 --scale=0.5 --format=png
# Check output has transparency
```

## Common Issues
| Issue | Fix |
|-------|-----|
| Black background | Add `backgroundColor="transparent"` to Composition |
| Green tint | Use yuva444p10le, not yuva420p |
| Large file size | Use VP9 for web, ProRes for editing |
| No alpha in browser | Use WebM VP9, not MP4 |