---
name: anti-slop-design
description: Anti-slop design skill — Three Dials system, AI-tell detection, Pre-Flight Check, typography/color discipline. Load this BEFORE any design/landing page work to prevent templated AI output.
version: 1.0.0
author: Hermes (sourced from Taste Skill + Anthropic Frontend Design)
---

# Anti-Slop Design Skill

> Load this skill BEFORE generating any UI, landing page, or design artifact.
> It prevents the most common AI-tells and enforces intentional design decisions.

## 0. BRIEF INFERENCE — Read the Room

Before ANY code, state a one-line "Design Read":
```
Reading this as: <page kind> for <audience>, with a <vibe> language, leaning toward <design system or aesthetic>
```

Then set the **Three Dials** from the brief (not from memory):

### Three Dials

| Dial | Range | SaaS Landing | Agency Portfolio | Premium Consumer | Editorial | B2B/Trust |
|------|-------|-------------|-----------------|-----------------|-----------|-----------|
| DESIGN_VARIANCE | 1-10 | 7 | 9 | 7 | 6 | 3 |
| MOTION_INTENSITY | 1-10 | 6 | 8 | 6 | 4 | 2 |
| VISUAL_DENSITY | 1-10 | 4 | 3 | 3 | 3 | 5 |

**DESIGN_VARIANCE:** 1-3 (symmetry) → 4-7 (offset) → 8-10 (asymmetric)
**MOTION_INTENSITY:** 1-3 (static) → 4-7 (CSS transitions) → 8-10 (scroll hijack, physics)
**VISUAL_DENSITY:** 1-3 (airy) → 4-7 (standard) → 8-10 (packed)

## 1. TYPOGRAPHY DISCIPLINE

### Sans Display (DEFAULT for all non-editorial briefs)
- **BANNED as default:** Inter. Pick Geist, Outfit, Satoshi, Cabinet Grotesk first.
- **Acceptable pairings:** Geist+Mono, Satoshi+JetBrains Mono, Cabinet Grotesk+Inter Tight

### Serif (VERY DISCOURAGED as default)
- Only when brief explicitly names a serif, OR the aesthetic is genuinely editorial/luxury/heritage
- **BANNED as defaults:** Fraunces, Instrument_Serif, Playfair Display
- **If justified:** rotate from: GT Sectra, Reckless Neue, Tiempos Headline, Recoleta, Cormorant Garamond, Editorial Old, Saol Display, Domaine Display, Canela

### Italic Descender Clearance (mandatory)
- Italic words with `y g j p q` need `leading-[1.1]` + `pb-1` padding

## 2. COLOR CALIBRATION

### The LILA RULE (most violated AI-tell)
- **BANNED as default:** AI-purple/blue gradient glows, neon accents on everything
- Default: neutral bases (Zinc/Slate/Stone) + ONE high-contrast accent (Emerald, Rose, Burnt Orange, Electric Blue)

### PREMIUM-CONSUMER PALETTE BAN (second most violated)
- **BANNED families as default:** 
  - Backgrounds: #f5f1ea, #f7f5f1, #fbf8f1, #efeae0 (warm beige/cream/chalk)
  - Accents: #b08947, #b6553a, #9a2436, #9c6e2a (brass/clay/oxblood)
  - Text: #1a1714, #1a1814 (espresso near-black)
- **Rotate between these alternatives instead:**
  - Cold Luxury: silver-grey + chrome + smoke
  - Forest: deep green + bone + amber
  - Black + Tan: true off-black + warm tan
  - Cobalt + Cream: saturated blue against neutral
  - Terracotta + Slate: warm rust + cool grey
  - Monochrome + one saturated pop

## 3. LAYOUT DISCIPLINE (Hard Rules)

### Hero
- MUST fit viewport: headline ≤ 2 lines, subtext ≤ 20 words, CTA visible without scroll
- Max `pt-24` top padding
- Max 4 text elements (eyebrow OR brand strip + headline + subtext + CTAs)
- **NO** trust logos, feature bullets, taglines inside hero
- **NO** scroll cues ("Scroll", "↓", animated mouse wheel)

### Navigation
- ONE line at desktop, max 80px height
- No pills/labels overlaid on images

### Sections
- **Zigzag alternation cap:** max 2 consecutive image+text split sections
- **Section-Layout-Repetition ban:** each layout family at most ONCE per page (8 sections → 4+ different families)
- **Bento:** EXACTLY N cells for N items. No empty tiles. 2-3 cells need visual variation (image, gradient, pattern)
- **Eyebrow restraint:** max 1 eyebrow per 3 sections. Mechanical count check before ship
- **Split-header ban:** no "left big headline + right small paragraph" section headers. Stack vertically
- **No section-numbering eyebrows** (001·Capabilities, 00/INDEX, 06·how it works)

## 4. ANTI-AI TELLS — Check Every Output

### Hero tells
- ❌ Version labels (V0.6, BETA, EARLY ACCESS, ALPHA) — only for launch briefs
- ❌ "Brand · No. 01" sub-eyebrows
- ❌ Decoration text strip at bottom ("BRAND. MOTION. SPATIAL.")
- ❌ Floating top-right sub-text in section headings

### Content tells
- ❌ Em-dash (—) ANYWHERE. Zero tolerance. Use regular hyphen (-)
- ❌ Middle-dot (·) rationed. Max 1 per metadata line
- ❌ Colored decorative dots (on nav, on badges, on lists) — only for real semantic state
- ❌ "Jane Doe" / "Acme" / generic names and brand names
- ❌ Filler verbs: "Elevate", "Seamless", "Unleash", "Revolutionize"
- ❌ "Quietly in use at" / "Quietly trusted by" social-proof headers
- ❌ "From the field" / "On our desks" / "Loose plates" poetic labels
- ❌ Fake-perfect numbers (99.99%, 1234567)
- ❌ Generic step labels ("Stage 1 / Stage 2", "Phase 01 / 02")

### Visual tells (sourced from Impeccable 47k★ anti-slop design system)
- ❌ Three equal feature cards in a row
- ❌ Nested cards (card-inside-card)
- ❌ Div-based fake product screenshots
- ❌ Hand-rolled decorative SVG illustrations
- ❌ Glassmorphism by default
- ❌ Neon / outer glows / AI-tool glow
- ❌ Purple gradients, neon cyan fields, or editorial magenta as accent
- ❌ Italic serif display typography
- ❌ Vertical rotated text as decoration
- ❌ Photo-credit captions as decoration ("Field study no. 12")
- ❌ Version footers (v1.4.2, Build 0048)
- ❌ Locale/weather strips (LIS 14:23 · 18°C) — only for travel/distributed teams
- ❌ Em-dash as any typographic flourish

## 5. DESIGN SYSTEM MAPPING

| Brief reads as... | Use official package |
|------------------|-------------------|
| Microsoft/enterprise | @fluentui/react-components |
| Google-ish/Material | @material/web + M3 tokens |
| IBM B2B/analytics | @carbon/react |
| Shopify app | Polaris web components |
| Atlassian/Jira | @atlaskit |
| GitHub devtool | @primer/css |
| UK public sector | govuk-frontend |
| US public sector | uswds |
| Modern accessible React | @radix-ui/themes |
| Modern SaaS (own code) | shadcn/ui (never default state) |
| Indie SaaS MVP | Tailwind v4 utilities |

**One system per project.** Never mix Material + shadcn in same tree.

## 6. ARCHITECTURE DEFAULTS (Hermes Agent)

### Stack
- Plain HTML/CSS/JS for standalone artifacts (Hermes default)
- React/Next.js only when the project stack demands it
- Tailwind v4 for utility CSS (postcss.config.js: @tailwindcss/postcss plugin)
- Motion (motion/react) for JS animations — NOT framer-motion
- GSAP + ScrollTrigger ONLY for full-page scroll hijack (isolated leaf components)

### Viewport
- `min-h-[100dvh]`, NEVER `h-screen` (mobile Safari address bar)
- Grid over Flex-Math: CSS Grid, not `w-[calc(33%-1rem)]`
- Color lock: ONE accent used on WHOLE page. Warm-grey site doesn't get blue CTA in section 7
- Shape lock: ONE corner-radius system per page

### Images
- Priority: 1) real stock photos (Pexels > Unsplash > Pixabay) 2) generate via image tool 3) placehold.co with brand colors (last resort only)
- **RU audience:** Unsplash unreliably times out or is blocked by ISPs. Picsum gives random irrelevant content (nature, phones).
- **Pexels works reliably in Russia** — `https://images.pexels.com/photos/{ID}/pexels-photo-{ID}.jpeg?auto=compress&cs=tinysrgb&w={WIDTH}&h={HEIGHT}&fit=crop`
- **placehold.co is last-resort fallback** — real-business users reject it as "заглушки" (stub photos). Never default to it for production-facing pages.
- **Photos MUST match business context**: beauty salon gets beauty/hair/salon shots, not nature/phones/cars. Test relevance before committing — verify Pexels IDs return 200 with `curl -sI "https://images.pexels.com/photos/{ID}/pexels-photo-{ID}.jpeg?auto=compress&cs=tinysrgb&fit=crop" | grep HTTP/` (some IDs return 404, e.g., 5069606, 3912581).
- Never div-based fake screenshots
- Real SVG logos (simple-icons CDN) for trust walls. Never plain text wordmarks
- Logo wall = logos only. No industry labels below

## 7. PERFORMANCE & ACCESSIBILITY

- Animate ONLY `transform` + `opacity`. Never `top/left/width/height`
- `prefers-reduced-motion` mandatory for MOTION_INTENSITY > 3
- Dark mode tokens for any consumer-facing page
- WCAG AA for body text (4.5:1), AAA for hero
- No pure `#000000` or `#ffffff` — use off-black/off-white
- CTA buttons: text MUST fit one line at desktop
- No duplicate CTA intent (no "Get in touch" + "Contact us" + "Let's talk" on same page)
- Form contrast check: every input, placeholder, focus ring passes WCAG AA

## 7.5. CLIENT AUDIT PATTERN (use for paid design reviews)

**Do NOT present anti-slop violations as technical failures to paying clients.**
Every violation must be translated into a business consequence.

Pattern:
1. Find violations via Pre-Flight Check (Section 8)
2. Translate each violation into client language (see `references/client-audit-sales.md`)
3. Prioritize by business impact (P0/P1/P2)
4. Add time estimates per fix
5. Frame as upsell: "Your site is 6/10. I can make it 9/10 in 1.5 hours."

Key phrases: "Ваш сайт выглядит как все — давайте сделаем чтобы он выглядел как вы"

## 8. PRE-FLIGHT CHECK (run before delivering ANY design output)

Run this checklist mentally. If ANY box can't be ticked, the output is not done.

- [ ] Brief inference declared (Section 0 one-liner)?
- [ ] Three Dials set from brief, not default?
- [ ] Design system chosen from Section 5 or aesthetic labeled?
- [ ] ZERO em-dashes (—) anywhere?
- [ ] Page Theme Lock: ONE theme for entire page?
- [ ] Color Consistency Lock: one accent across all sections?
- [ ] Shape Consistency Lock: one corner-radius system?
- [ ] Button Contrast Check: all CTAs readable (no white-on-white)?
- [ ] CTA Button Wrap: no wrapped labels at desktop?
- [ ] Serif discipline: not Fraunces/Instrument_Serif without justification?
- [ ] Premium palette check: not AI-default beige+brass for consumer briefs?
- [ ] Hero fits viewport: ≤2 line headline, ≤20 word subtext, CTA visible?
- [ ] Hero top padding max pt-24?
- [ ] Hero stack discipline: max 4 text elements?
- [ ] Eyebrow mechanical count: ≤ ceil(sectionCount/3)?
- [ ] No split-header sections?
- [ ] Zigzag cap: no 3+ consecutive same-layout sections?
- [ ] No duplicate CTA intent?
- [ ] Logo wall = logos only?
- [ ] Bento diversity: 2-3 cells with visual variation?
- [ ] Copy self-audit: no AI-hallucinated phrases?
- [ ] Motion motivated: every animation has a reason?
- [ ] Marquee max ONE per page?
- [ ] Single-line nav at desktop, ≤80px?
- [ ] Section-Layout-Repetition: 8 sections → 4+ different layouts?
- [ ] Bento exact cell count: N items → N cells?
- [ ] Real images used (not placeholders for production pages)?
- [ ] Image source reliable for RU audience (Pexels > Unsplash)?
- [ ] Photos match business context (not just random nature/phones)?
- [ ] No pills/labels overlaid on images?
- [ ] No photo-credit captions as decoration?
- [ ] No version footers / locale strips / scroll cues?
- [ ] No AI Tells from Section 4?
- [ ] Reduced motion honors prefers-reduced-motion?
- [ ] Dark mode tokens defined?
- [ ] Mobile collapse explicit for every multi-column?
- [ ] Viewport stability: min-h-[100dvh]?
- [ ] One design system per project?

**FAIL ANY → FIX BEFORE DELIVERING.**

### Expected Violations Pattern (learned 2026-07-10)

**Do not trust your first pass.** Even with this skill loaded, the first generated draft will almost certainly fail multiple Pre-Flight items. This is normal — the skill's rules fight muscle memory from thousands of pre-skill training examples.

The most common first-pass violations:
1. **Em-dashes everywhere** — the #1 violation. Every `&mdash;` in your first draft must be replaced with `-`. Search the rendered content, not just the code.
2. **Eyebrow overcount** — by default you put a section label above every section. Max 2 on the whole page (hero counts as 1). Strip extras aggressively.
3. **Three equal cards** — service/feature sections default to 3 identical cards. Bento with varied cell sizes is the fix.
4. **AI-default palette** — if you didn't explicitly pick from Section 2 alternatives, you used beige+brass+espresso. Re-pick.
6. **Placehold as last resort** — users reject colored blocks as "заглушки". Prefer Pexels for Russian market; test image relevance before committing.
7. **Contextually wrong images** — Picsum gives random photos (nature, phones). Always verify stock photos match the business domain before embedding.

### Color Refactoring Technique (learned 2026-07-21)

When retrofitting an existing page that violates the Premium Palette Ban (Section 2):

1. Define new CSS variables in `:root{}` — e.g., `--forest:#2d4a3e`, `--bone:#f5f1eb`, `--amber:#c4954a`
2. `patch(mode='replace', replace_all=True)` to swap `var(--banned-color)` → `var(--new-color)` across the file — handles 30+ occurrences in one call
3. Replace inline RGB: `rgba(196,106,74,X)` → `rgba(45,74,62,X)` (terracotta → forest in this case)
4. Replace hardcoded hex: `#f7f4f0` → `var(--bone)` — likely visible in `body{background:...}` and `.header.scrolled{background:...}`
5. Verify with `grep -c 'old-hex\\|old-var' file.html` — should be 0
6. Then update accent elements (icons, price tags, stat numbers) to the warm accent (amber) rather than the base color (forest)

The key insight: forest becomes the background/promo color, amber becomes the accent/warm-hit color. Don't just swap one uniform color for another — split the roles.

### Header Visibility on Dark Hero (learned 2026-07-21)

**Critical: always check header nav contrast before delivering.** This is the #1 user complaint after a dark-hero redesign.

When hero section has a dark background (forest, charcoal, black) with a fixed/transparent header:
- Header nav text MUST be white (`rgba(255,255,255,0.85)` or similar) — `var(--slate-light)` is INVISIBLE on dark bg
- CTA button in header MUST contrast: amber/gold/warm accent on dark bg, NOT the body color (forest/green)
- When header scrolls to light background, nav should transition to dark text (scrolled class)
- Verify both states (hero top + scrolled) before showing the user

Pre-Flight addition: Before delivering any dark-theme page, mentally verify:
- [ ] Header nav text visible on hero (white/light, not `--slate-light`)
- [ ] Header CTA button contrasts with hero background
- [ ] Scrolled state nav text is dark/readable on light background
- [ ] If mix-blend-mode:difference is used, test on both dark and light hero sections

### Instagram Gallery for Real Businesses (learned 2026-07-21)

When building for a real business with Instagram presence:
1. Research their Instagram/TG handle first (from brief or web search)
2. Add a gallery section with a prominent link to their social: "Більше фото в Instagram: @handle"
3. If Instagram API blocks direct image download, use stock photos (Pexels) as fallback + strong Instagram link
4. Instagram CDN URLs with auth tokens expire within hours — do NOT use as permanent image sources
5. Download to local assets/ and reference locally for reliable deployment
6. Gallery labels (overlay text) should describe real services offered (Стрижки, Манікюр, Фарбування)

**Process correction:** Generate the first draft → immediately run the Pre-Flight Check (Section 8) on the CURRENT output → find violations → fix → re-check. Do NOT fix anything before checking. The checklist catches violations faster than manual review.

### Tonal Weight vs Business Context (learned 2026-07-27)

All-black or near-black layouts (charcoal, off-black) create a **luxury/funeral/tech** signal — wrong for beauty, health, family, and most local-service businesses.

**Before choosing a primary darkness, ask:**
- Would an actual client in this niche feel welcome on this page?
- Beauty/family/wellness → light or medium base (off-white, bone, warm grey), never dark
- Tech/portfolio/luxury → dark base is acceptable
- Law/finance/consulting → medium (slate, navy), never pure black or pure white

**Diagnostic:** If the page could sell coffins OR luxury watches, the tonal weight is wrong for a service business. Lighten the base and shift to warm neutrals.

This is NOT the same as "no pure #000000" (already banned). Even off-black `#292524` + forest green `#2d4a3e` can produce a funeral-home effect when used as THE dominant background. Fix: make the base background light/neutral and reserve dark for text and accents only.

### Structural Template Breakthrough (learned 2026-07-27)

When the user says "всё одно и то же, цвета разные" (same thing, different colors), it means the **page STRUCTURE** is slop, not just the colors/fonts.

The default template structure for service business landings:
```
hero → services (3 cards) → gallery → testimonials → prices → footer
```

**Break the template systematically** by mapping each section to a fundamentally different form:

| Template element | Replace with... |
|---|---|
| Navigation bar | Floating single button or none |
| Hero with image + text | Splash with outline text + stats, or manifesto, or just a title card |
| Service cards (3 identical) | Masters section — each person = their own section with photo/bio/specialty |
| Gallery grid | Color swatches / atmosphere palette / energy banner |
| Testimonial cards | Snap quotes with age/initials, or pull quotes across full bleed |
| Price table/chart | Price as poetry, or price chips in grid, or single column list |
| Footer with links | Closing spread — invitation, address, just a phone number |

**Diagnostic for structural slop:**
1. Cover the content — look at the layout shapes only
2. If all sections look like "[rectangular block] → 3 equal rectangles → grid → 3 rectangles → table → footer", the structure is slop
3. Each section should have a unique visual shape and rhythm

**How to find alternatives:** when stuck, load vibe-mode skill (self-improvement/vibe-mode) — it's designed for exactly this: identify the template, then replace each element with something that breaks the pattern entirely.

When a design direction keeps getting rejected after 2+ attempts:
1. **YouTube** — search "modern [niche] website design" for real examples and inspiration
2. **Knowledge Cube** — `recall_for_session("design [niche]")` to surface past lessons
3. **Awwwards / siteInspire** — browse layout innovation even if the niche differs
4. **Google Stitch** (stitch.withgoogle.com) — free AI UI design tool (~400 daily credits). Generate reference layouts from prompts to explore different approaches. See `references/stitch-mcp-design-resource.md` for MCP setup and tool list.

Do NOT keep iterating the same direction after two rejections. Pause, research, change approach fundamentally.

### Images: Real Photos for Local Service Businesses (learned 2026-07-27)

When the niche is a local service business (salon, clinic, repair shop):
1. Search for their actual Instagram/TG handle first
2. If social confirms real photos exist, use **Pexels** with niche-relevant search terms (not random picsum/unsplash)
3. Verify each Pexels photo ID returns 200 with `curl -sI "https://images.pexels.com/photos/{ID}/pexels-photo-{ID}.jpeg?auto=compress&cs=tinysrgb&fit=crop" | grep HTTP/`
4. Test image-to-niche match before embedding — a business owner will notice generic stock photos
5. placehold.co = last resort fallback only for staging. Real businesses reject "заглушки" (stub placeholders)

The case study in `references/case-study.md` documents one real session where this happened.
The multi-attempt case study in `references/three-attempt-case-study.md` documents a beauty salon design iteration from Drupal-look to anti-slop-compliant (v1→v2→v3 evolution).

## 9. REFERENCE VOCABULARY

| Pattern | When to use |
|---------|------------|
| Asymmetric Split Hero | SaaS/agency landing with strong asset + message |
| Editorial Manifesto Hero | Message IS the design (launch, manifesto) |
| Bento Grid | Feature grid with varied tile sizes |
| Sticky Scroll Stack | Scrolltelling with pinning cards |
| Horizontal Scroll Hijack | Portfolio/creative, single long scroll → horizontal pan |
| Kinetic Typography | Brand with motion identity |
| Marquee | ONE per page for logo wall or highlight strip |
| Glassmorphism | Premium consumer, Apple-adjacent, NOT default |

## 10. SOURCE SKILLS (installed at ~/.claude/skills/)

For Claude Code design work, these skill repos are installed:
- **frontend-design/** — Official Anthropic Frontend Design Skill (1M+ installs)
- **taste-skill/** — 13 anti-slop skills (brandkit, brutalist, minimalist, redesign, etc.)
- **designer-skills/** — 86 design skills across 9 categories (design-ops, research, systems, interaction, prototyping, UI, strategy, critique)
- **ux-ui-agent-skills/** — 17 skills (a11y-audit, design-tokens, figma-integration, governance, etc.)
- **awesome-design-md/** — 55+ brand design systems as DESIGN.md files
