---
name: taste-skill-curation
description: Integrates Jaytel0/taste and senlindesign/taste-skill for comprehensive design taste extraction and skill generation.
---

# Taste Skill Curation — Visual + Design DNA Integration

> Combines image-based taste extraction (Jaytel0/taste) with website design analysis (senlindesign/taste-skill) for complete design-to-skill workflow.

## When to Load

- Building landing pages with specific visual reference needs
- Redesigning based on competitor or inspiration sites
- Need both visual extraction AND anti-slop design rules
- Want systematic catalog of design systems + taste principles

## 0. PARALLEL APPROACHES

### A. Image-Based Taste Extraction (Jaytel0/taste)
**Goal:** Convert reference images into reusable SKILL.md
**Use when:** You have visual references (screenshots, mood boards, competitor sites) but no URL to analyze

**Workflow:**
1. Put JPG/PNG/WebP into `reference-images/`
2. Run local pipeline: `npm run taste` or `python scripts/taste.py`
3. Output: `.taste/runs/<runId>/04-skill/SKILL.md`
4. Use anti-slop-design rules for final curation

**Strengths:**
- Pure visual focus, no URL needed
- Can extract from any image source (screenshots, physical mockups)
- Produces detailed design tokens and rules
- Good for when you have specific visual targets

**Limitations:**
- Requires image uploads
- Less systematic than site-wide analysis

### B. Website Design DNA Extraction (senlindesign/taste-skill)
**Goal:** Extract design system + taste DNA from any public URL
**Use when:** You need to analyze competitor sites or understand design patterns

**Workflow:**
1. Analyze any URL: `/taste https://competitor-site.com`
2. Output: `{domain}.md` + `{domain}.json`
3. Contains Design Map + Taste DNA sections
4. Leverages Playwright MCP for screenshots + DOM analysis

**Strengths:**
- Systematic cross-page analysis (2-3 linked pages)
- Captures both visual evidence + DOM constraints
- Produces machine-readable JSON + markdown
- Includes anti-slop audit in export formats

**Limitations:**
- Limited to public URLs
- Cannot analyze private/protected sites

## 1. SELECTION MATRIX

| Project Type | Primary Tool | Secondary Tool | Why |
|--------------|-------------|---------------|-----|
| Visual reference available | Jaytel0/taste | anti-slop-design | You have specific mockups/screenshot targets |
| Want site analysis | senlindesign/taste-skill | anti-slop-design | Need systematic competitor/website analysis |
| Both approaches | Use both | anti-slop-design | Combine images + URL analysis |
| Production landing page | Jaytel0/taste + anti-slop-design | senlindesign/taste-skill | Control visuals precisely + anti-slop rules |
| SEO/content site | senlindesign/taste-skill + anti-slop-design | Jaytel0/taste | Extract layout patterns + design DNA |

## 2. WORKFLOW PIPELINES

### Pipeline A: Image Reference → Anti-Slop Design
```
reference-image.jpg → Jaytel0/taste → SKILL.md (tokens/constraints) → anti-slop-design → final SKILL.md (production-ready) → deploy
```

**When to use:** You have visual references but no URL targets

**Example:**
- Screenshot from competitor's landing page
- Figma export (PNG)
- Physical mockup photo
- Mood board collage

### Pipeline B: Website Analysis → Design DNA → Anti-Slop Design
```
https://competitor-site.com → senlindesign/taste-skill → {domain}.md + .json → anti-slop-design → final SKILL.md
```

**When to use:** You want systematic extraction of a working design

**Example:**
- Competitor's marketing site
- Industry benchmark site
- Design inspiration pages

### Pipeline C: Hybrid Approach
```
Analyze competitor: https://site.com → taste-skill → extract patterns
Add visual references: extract specific UI patterns from screenshots
Combine both into final curated SKILL.md
```

## 3. ANTI-SLOP DESIGN INTEGRATION

### Pre-Flight Checks
After any taste extraction, run anti-slop design pre-flight:

1. **Brief Inference:** State single design read before any code
2. **Three Dials:** Set DESIGN_VARIANCE/MOTION_INTENSITY/VISUAL_DENSITY
3. **Design System:** Choose from Section 2 (Fluent, Material, Carbon, etc.)
4. **Color Compliance:** Not using beige+brass premium default
5. **Hero Discipline:** Fits viewport, ≤2 line headline, ≤20 word subtext
6. **Typography Rules:** Not Inter/serif without justification
7. **Zero Em-Dashes:** Replace all &mdash; with normal hyphen

### Taste Extraction + Anti-Slop Process
```
1. Extract tokens from reference/images
2. Generate initial rules
3. Run anti-slop pre-flight on extracted rules
4. Identify violations (em-dashes, eyebrow overcount, etc.)
5. Fix violations based on guidelines
6. Final SKILL.md passes all checks
```

## 4. PROJECT WORKFLOWS

### Project A: Landing Page (Image Reference)

**Goal:** Create landing page matching brand aesthetic
**Approach:**
1. Gather visual references (screenshots, brand fonts/colors)
2. Run Jaytel0/taste to extract design tokens
3. Apply anti-slop-design filters to remove AI-tells
4. Generate final SKILL.md with production-ready rules

**Skills used:** Jaytel0/taste → anti-slop-design

### Project B: Redesign Competitor Site (URL Analysis)

**Goal:** Extract working design patterns + create new solution
**Approach:**
1. Run `/taste https://competitor-site.com`
2. Analyze Design Map + Taste DNA
3. Use anti-slop-design to curate and improve
4. Generate new SKILL.md for replacement site

**Skills used:** senlindesign/taste-skill → anti-slop-design

### Project C: Portfolio Site (Combined)

**Goal:** Extract layout patterns + add brand-specific touches
**Approach:**
1. Analyze competitor: `senlindesign/taste-skill https://portfolio-site.com`
2. Add visual references: extract UI patterns from specific screenshots
3. Combine both sources using anti-slop rules
4. Final curated SKILL.md for production

**Skills used:** Both → anti-slop-design

## 5. GOOD USE CASES

| Use Case | Primary Tool | Secondary Tool | Result |
|----------|-------------|---------------|--------|
| Landing page matching brand colors | Jaytel0/taste | anti-slop-design | Precise color mapping, no AI-purple |
| Competitor analysis | senlindesign/taste-skill | anti-slop-design | Full design system, taste principles |
| Feature request with mockups | Jaytel0/taste | anti-slop-design | Extract tokens from images |
| Website audit | senlindesign/taste-skill | anti-slop-design | Identify design DNA, anti-slop improvements |

## 6. COMMON PIPELINES

### Taste-Only Pipeline (Jaytel0)
```bash
# 1. Setup
npm install
cp .env.example .env.local

# 2. Add images
# Put JPG/PNG/WebP into reference-images/

# 3. Run
npm run taste

# 4. Output
.taste/runs/<runId>/04-skill/SKILL.md
```

### Design Extraction Pipeline (senlindesign)
```bash
# 1. Local setup
npm install

# 2. Analyze any URL
/taste https://example.com

# 3. Output
example.md + example.json
# Also writes CLAUDE.md (for Claude Code users)
```

### Anti-Slop Curation Pipeline
```bash
# 1. Extract tokens/rules
python scripts/extract_taste.py

# 2. Run anti-slop pre-flight check
python scripts/anti-slop-audit.py

# 3. If violations found -> fix
# Edit generated SKILL.md to fix em-dashes, eyebrow counts, etc.

# 4. Final validation
python scripts/validate_skill.py
```

## 7. SOURCES & INTEGRATION

### Jaytel0/taste Integration
- **GitHub:** https://github.com/jaytel0/taste
- **Purpose:** Convert visual references into reusable skills
- **Strength:** Pure visual token extraction
- **Weakness:** Less systematic than site analysis

### senlindesign/taste-skill Integration
- **GitHub:** https://github.com/senlindesign/taste-skill
- **Purpose:** Extract design system + taste DNA from URLs
- **Strength:** Systematic cross-page analysis + anti-slop audit
- **Weakness:** Limited to public URLs

### Anti-Slop Design Integration
- **Source:** Derived from Leonxlnx/taste-skill + Anthropic Frontend Design
- **Purpose:** Prevent templated AI output via strict design rules
- **Strength:** 47k★+ followers, comprehensive rules
- **Weakness:** Requires manual application to extracted tokens

## 8. NEXT STEPS

1. **Choose approach:** Image reference vs URL analysis
2. **Setup pipeline:** Choose Jaytel0/taste or senlindesign/taste-skill
3. **Extract tokens:** Run appropriate tool
4. **Apply anti-slop rules:** Filter AI-tells, enforce design discipline
5. **Validate:** Ensure final SKILL.md passes all pre-flight checks
6. **Deploy:** Use final SKILL.md for production

## 9. VALIDATION CHECKLIST

After taste extraction + anti-slop curation:

- [ ] Single design read stated?
- [ ] Three Dials set correctly?
- [ ] One design system chosen? (from Section 2)
- [ ] Zero em-dashes in entire content?
- [ ] Color palette matches Section 2 alternatives?
- [ ] Typography not using Inter/serif without justification?
- [ ] Hero fits viewport? ≤2 line headline, ≤20 word subtext?
- [ ] Eyebrow count ≤ ceil(sectionCount/3)?
- [ ] No split-header sections?
- [ ] No duplicate CTA intent?
- [ ] Image references match business context?
- [ ] Real SVG logos used (no text-wordmarks)?
- [ ] Photos Pexels > Unsplash for Russian audience?
- [ ] No AI-tells from Section 4?
- [ ] Preferences reduced motion respected?
- [ ] Dark mode tokens defined?
- [ ] Mobile collapse explicit?
- [ ] Viewport stability with min-h-[100dvh]?
- [ ] Antislop pre-flight complete?

**All must pass for production-ready SKILL.md.**

---

*Created from integration of Jaytel0/taste and senlindesign/taste-skill + anti-slop design principles*
*One stop shop for comprehensive design taste extraction and curation*