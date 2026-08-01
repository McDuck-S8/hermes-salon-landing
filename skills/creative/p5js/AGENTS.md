# p5js — Skill

## Purpose
p5.js sketches: gen art, shaders, interactive, 3D. Production pipeline for interactive and generative visual art using p5.js. Creates browser-based sketches, generative art, data visualizations, interactive experiences, 3D scenes, audio-reactive visuals, and motion graphics — exported as HTML, PNG, GIF, MP4, or SVG.

## Ownership
Hermes Agent

## Local Contracts
- **Triggers**: User requests p5.js sketches, creative coding, generative art, interactive visualizations, canvas animations, browser-based visual art, data viz, shader effects, or any p5.js project
- **Required tools**: Standard Hermes tools (browser, terminal, file operations)
- **Config**: config.yaml in skill dir (optional)
- **Required scripts**: `scripts/export-frames.js`, `scripts/render.sh`, `scripts/serve.sh`, `scripts/setup.sh`

## Work Guidance
**When to use**: Auto-detected from context when user requests p5.js sketches, creative coding, generative art, interactive visualizations, canvas animations, browser-based visual art, data viz, shader effects, or any p5.js project.

**Common patterns**:
1. **Creative Vision** — Articulate mood, color world, motion vocabulary, what makes this unique
2. **Technical Design** — Choose mode, canvas size, renderer (P2D/WEBGL), frame rate, export target, interaction model
3. **Code the Sketch** — Single HTML file with inline p5.js. Structure: globals → `preload()` → `setup()` → `draw()` → helpers → classes → event handlers
4. **Preview & Iterate** — Open in browser, verify visual quality at target resolution, check performance
5. **Export** — PNG (saveCanvas), GIF (saveGif), frame sequence + ffmpeg for MP4, Puppeteer for headless batch
6. **Quality Verification** — Match vision? Sharp at target size? 60fps (30 min)? Colors work on light/dark? Edge cases handled?

**Creative Standard**: This is visual art rendered in the browser. The canvas is the medium; the algorithm is the brush. Before writing code, articulate the creative concept. First-render excellence is non-negotiable. Go beyond the reference vocabulary. Be proactively creative. Dense, layered, considered — every frame should reward viewing.

**Key Implementation Patterns**:
- Always disable FES: `p5.disableFriendlyErrors = true` + `pixelDensity(1)`
- Seeded randomness: always `randomSeed()` + `noiseSeed()` for reproducibility
- Color mode: HSB (360, 100, 100, 100) for intuitive color control
- Use `createGraphics()` offscreen buffers for layered composition
- Performance: vectorize with `beginShape(POINTS)` or pixel buffer for massive particle counts
- WebGL gotchas: origin at center, Y inverted, `push()`/`pop()` around transforms
- Export keybindings: 's'=PNG, 'g'=GIF, 'r'=reseed, ' '=pause
- Headless export requires `noLoop()` + `window._p5Ready = true` in setup

**Related skills**: ascii-video, manim-video, excalidraw

## Verification
- Load SKILL.md and validate frontmatter
- Run `scripts/setup.sh` to verify setup
- Run `scripts/serve.sh` to verify local server works
- Test export: open `templates/viewer.html` in browser, press 's' to save PNG
- Run `node scripts/export-frames.js templates/viewer.html --frames 10` for headless export test
- Verify `references/` directory has 10 reference files

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (10 files: animation.md, color-systems.md, core-api.md, export-pipeline.md, interaction.md, shapes-and-geometry.md, troubleshooting.md, typography.md, visual-effects.md, webgl-and-3d.md) |
| `templates/` | Template files (1 file: viewer.html for interactive generative art with seed navigation, parameter sliders, PNG download) |
| `scripts/` | Executable helpers (4 files: export-frames.js, render.sh, serve.sh, setup.sh) |