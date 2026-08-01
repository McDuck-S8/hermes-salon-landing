---
name: svelte-bits
description: "Svelte Bits (sveltebits.xyz) — 128+ animated Svelte 5 components. Use when building SvelteKit projects that need creative UI: text animations, backgrounds, interactive components, effects."
tags: [svelte, sveltekit, ui, components, animations, tailwind, typescript]
---

# Svelte Bits — Creative UI Components for Svelte

**Site:** https://sveltebits.xyz  
**GitHub:** https://github.com/DavidHDev/svelte-bits  
**Author:** David Haz (@davidhdev)  
**License:** MIT + Commons Clause  
**Stack:** Svelte 5 + TypeScript + Tailwind  
**Origin:** Port of React Bits (https://reactbits.dev)

## Installation

### jsrepo (recommended)
```bash
npx jsrepo init https://sveltebits.xyz/r
npx jsrepo add <component-name>
```

### shadcn CLI
```bash
npx shadcn@latest add https://sveltebits.xyz/r/<component-name>.json
```

### Manual
Each component is a standalone `.svelte` file — copy from GitHub into your project.

## Component Categories (128 total)

### Text Animations (23)
SplitText, BlurText, CircularText, TextType, Shuffle, ShinyText,
TextPressure, CurvedLoop, FuzzyText, GradientText, FallingText,
TextCursor, DecryptedText, TrueFocus, ScrollFloat, ScrollReveal,
ASCIIText, ScrambledText, RotatingText, GlitchText, ScrollVelocity,
VariableProximity, CountUp

### Animations (29)
AnimatedContent, FadeContent, ElectricBorder, OrbitImages,
PixelTransition, GlareHover, Antigravity, LogoLoop, TargetCursor,
MagicRings, LaserFlow, MagnetLines, GhostCursor, GradualBlur,
ClickSpark, Magnet, StickerPeel, PixelTrail, Cubes, MetallicPaint,
Noise, ShapeBlur, Crosshair, ImageTrail, Ribbons, SplashCursor,
MetaBalls, BlobCursor, StarBorder

### Components (34)
AnimatedList, ScrollStack, BubbleMenu, MagicBento, CircularGallery,
ReflectiveCard, CardNav, Stack, PillNav, TiltedCard, Masonry,
GlassSurface, DomeGallery, ChromaGrid, Folder, StaggeredMenu,
ModelViewer, ProfileCard, Dock, GooeyNav, PixelCard, Carousel,
SpotlightCard, BorderGlow, FlyingPosters, CardSwap, GlassIcons,
DecayCard, FlowingMenu, ElasticSlider, Counter, InfiniteMenu,
Stepper, BounceCards

### Backgrounds (42)
LiquidEther, Prism, DarkVeil, LightPillar, Silk, FloatingLines,
LightRays, PixelBlast, ColorBends, EvilEye, LineWaves, Radar,
SoftAurora, Aurora, Plasma, PlasmaWave, Particles, GradientBlinds,
Grainient, GridScan, Beams, PixelSnow, Lightning, PrismaticBurst,
Galaxy, Dither, FaultyTerminal, RippleGrid, DotField, DotGrid,
Threads, Hyperspeed, Iridescence, Waves, GridDistortion, Ballpit,
Orb, LetterGlitch, GridMotion, ShapeGrid, LiquidChrome, Balatro

## Usage Pattern

Components are imported from your project's component directory (after install):

```svelte
<script>
  import { Aurora } from '$lib/components/Aurora';
</script>

<Aurora color={['#FF3E00', '#4075a6']} speed={0.5} />
```

Each component page at sveltebits.xyz documents:
- Props API
- Dependencies
- Copy-ready install command
- Live demo with interactive prop editing

## Key Notes
- All components are Svelte 5 runes-based
- Many use WebGL shaders, Canvas, or physics engines
- Props are fully customizable; source is editable
- Works with Cursor, Copilot, v0 for AI-assisted development
- Site deploys on Cloudflare via adapter-cloudflare
- All 128 components are IMPLEMENTED (not placeholders)

## Pitfalls
- Some components require additional deps (three.js, gsap, etc.) — check each component's docs
- WebGL components may need SSR disabled (`client:only` in SvelteKit)
- Tailwind required for styling — components use Tailwind classes internally
