# pretext — Skill

## Purpose
Use when building creative browser demos with @chenglou/pretext — DOM-free text layout for ASCII art, typographic flow around obstacles, text-as-geometry games, kinetic typography, and text-powered generative art. Produces single-file HTML demos by default.

## Ownership
Hermes Agent

## Local Contracts
- **Triggers**: User asks for "pretext demo" / "cool pretext thing" / "text-as-X"; text flowing around a moving shape; ASCII-art effects using real words/prose; games where playfield/obstacles/bricks are made of text; kinetic typography with per-glyph physics; typographic generative art with non-Latin/mixed scripts; multiline "shrink-wrap" UI
- **Required tools**: Standard Hermes tools (browser, terminal, file operations)
- **Config**: config.yaml in skill dir (optional)
- **Required templates**: `templates/hello-orb-flow.html`, `templates/donut-orbit.html`

## Work Guidance
**When to use**: When user requests pretext demos, text-as-geometry, kinetic typography, text flowing around obstacles, ASCII obstacle typography, text-as-geometry games, editorial multi-column layouts, or multiline shrink-wrap UI.

**Common patterns**:
1. **Pick a pattern** from the reference table (reflow around obstacle, text-as-geometry game, shatter/particles, ASCII obstacle typography, editorial multi-column, kinetic type, multiline shrink-wrap)
2. **Start from a template**: `templates/hello-orb-flow.html` (text reflowing around moving orb) or `templates/donut-orbit.html` (advanced: ASCII logo obstacles, draggable wire sphere/cube, morphing shape fields, selectable DOM text, dev controls)
3. **Swap the corpus** for something intentional to the brief — real prose, 10-100 sentences, no lorem ipsum
4. **Tune the aesthetic** — font, palette, composition, interaction. This is the work; don't skip it.
5. **Verify locally**: `python3 -m http.server 8765` in the HTML directory, then open `http://localhost:8765/<file>.html`
6. **Check the console** — pretext throws if `prepareWithSegments` called with bad font string; `Intl.Segmenter` available in every modern browser
7. **Show the user the file path**, not just the code — they want to open it

**Creative Standard**: This is visual art rendered in a browser. Pretext returns numbers; **you** draw the thing.
- Don't ship a "hello world" demo. The `hello-orb-flow.html` template is the *starting* point. Every delivered demo must add intentional color, motion, composition, and one visual detail the user didn't ask for but will appreciate.
- Dark backgrounds, warm cores, considered palette. Classic amber-on-black (CRT/terminal) works, but so do cold-white-on-charcoal (editorial) and desaturated pastels (risograph). Pick one and commit.
- Proportional fonts are the point. Pretext's whole vibe is "not monospaced" — lean into it. Use Iowan Old Style, Inter, JetBrains Mono, Helvetica Neue, or a variable font. Never default sans.
- Real source text, not lorem ipsum. The corpus should mean something. Short manifestos, poetry, real source code, a found text, the library's own README — never `lorem ipsum`.
- First-paint excellence. No loading states, no blank frames. The demo must look shippable the instant it opens.

**Key APIs to master**:
- Use-case 1: `prepare()` + `layout()` — measure then render with CSS/DOM
- Use-case 2: `prepareWithSegments()` + `layoutWithLines()` — measure and render yourself on canvas/SVG/WebGL
- Variable-width-per-line: `layoutNextLineRange()` + `materializeLineRange()` — text around a shape, text in a donut band, text in non-rectangular column

**Related skills**: p5js, claude-design, excalidraw, architecture-diagram

## Verification
- Load SKILL.md and validate frontmatter
- Verify `templates/hello-orb-flow.html` and `templates/donut-orbit.html` exist and open in browser
- Verify `references/patterns.md` exists
- Run local server and open templates to confirm they render without console errors
- Check that `@chenglou/pretext@0.0.6` loads from esm.sh CDN in templates

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (1 file: patterns.md - community demo corpus patterns) |
| `templates/` | Template files (2 files: hello-orb-flow.html - text reflowing around moving orb; donut-orbit.html - advanced example with ASCII logo obstacles, draggable wire sphere/cube, morphing shape fields) |