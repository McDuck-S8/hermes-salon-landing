# Fargo Three-Attempt Case Study (2026-07-26)

## Context

Beauty salon landing page for "Fargo" (Kyiv, Poznyaky). Local neighborhood salon targeting Ukrainian women 25-45. The goal was a unique design — NOT the AI-default purple-gradient + card-grid template.

The agent produced three versions before reaching anti-slop compliance. This document tracks what went wrong at each step and which anti-slop rules caught the violation.

---

## Attempt 1: "The Pipeline" (v1)

**File:** `nicheforge_demo/fargo.html`

**Concept:** Warm cream + gold + rose. Playfair Display for headlines. Editorial magazine layout. Services as cards, price as tables.

**User feedback:** "честно... неудивил. я такие 20 лет тому видел на друпал" — dated, templated.

**Anti-slop violations:**

| Rule | Violation | Severity |
|------|-----------|----------|
| Premium Palette Ban (Sec 2) | Used `#fdf8f3` + `#b45309` + `#a13d4d` — warm beige+brass+oxblood, the EXACT banned family | P0 |
| Font ban (Sec 1) | Playfair Display as default serif — explicitly banned | P0 |
| Three Dial undefined | No Design Read or Three Dials declared before start | P0 |
| Fixed nav with nav-links | Desktop-only nav hidden on mobile — no collapse | P1 |
| Grid of equal cards | 6 service cards in 3-column grid — three-equal-cards variant | P1 |
| Numbered sections | None (hero only) — OK here | — |

**Why it felt templated:** Every AI-generated landing page uses warm beige + muted accent + Playfair. The user recognized it instantly as "yet another AI site."

---

## Attempt 2: "The Mirror" (v2)

**File:** `nicheforge_demo/fargo-v2.html`

**Concept:** Overcorrection. Pure black, huge typography, mirror reflection effect (scaleY(-1) + blur), Inter 200/900 weight contrast. No nav, no cards, no sections as blocks.

**User feedback:** "v2 (2026): скорее подойдёт для похоронного бюро, чем салону красоты" — wrong vibe, wrong business.

**Anti-slop violations:**

| Rule | Violation | Severity |
|------|-----------|----------|
| Pure `#000000` / `#ffffff` (Sec 7) | Background `#000`, text `#fff` — pure black/white banned | P0 |
| Font ban (Sec 1) | Inter as default — explicitly banned | P0 |
| Scroll cue (Sec 3) | "Scroll" with CSS animation — banned | P1 |
| Section-numbering eyebrows (Sec 3) | "/ 01", "/ 02", "/ 03" — banned | P1 |
| Design Read undefined | Still no Design Read or Three Dials | P0 |
| Wrong business context | All-black+Inter+monochrome reads as funeral, not beauty | P0 |

**Why it failed:** Overcorrection from v1. Swung to the opposite extreme (pure minimal) without considering the BUSINESS context. A beauty salon needs warmth, not funeral minimalism. Anti-slop rules caught the technical violations, but the business-context mismatch was caught only by user feedback.

**Lesson for Pre-Flight:** After checking all technical rules, ask: "Does this page communicate the RIGHT feeling for this specific business?" The anti-slop checklist has "Photos match business context" (Sec 8) but not "Visual tone matches business context."

---

## Attempt 3: "Forest" (v3)

**File:** `nicheforge_demo/fargo-v3.html`

**Concept:** Forest palette: deep green `#2d4a3e` + bone `#f5f1eb` + amber `#c4954a`. Outfit font (not Inter, not Playfair). Offset 2-col layout, no cards, no scroll cues, no em-dashes.

**Design Read declared:** "Salon landing for neighborhood beauty salon. Ukrainian women 25-45. Professional but warm, not luxury, not cheap. Forest palette."

**Three Dials:**
- VARIANCE=6 (offset, not symmetric)
- MOTION=4 (CSS transitions only)
- DENSITY=3 (airy — salon should feel spacious)

**Anti-slop compliance (all clear):**
- ✅ Forest palette (deep green + bone + amber) — NOT beige+brass+espresso
- ✅ Outfit font — NOT Inter, NOT Playfair
- ✅ No em-dashes — replaced all with regular hyphens
- ✅ No scroll cues
- ✅ No section-numbering eyebrows
- ✅ No equal cards — services in 2-col grid with varied content
- ✅ No pure `#000` or `#fff` — off-black `#292524`, off-white `#faf8f5`
- ✅ Hero fits viewport: h1 + 1 subtext line + 2 CTAs + 3 meta items = 4 elements
- ✅ Section-Layout-Repetition: 7 different layout families for 7 sections
- ✅ Page Theme Lock: forest+amber+bone throughout
- ✅ Color lock: amber accent on every section

**Result:** User did not reject v3 (no negative feedback received yet).

---

## Key Takeaways for Beauty Salon Design

### Palette
- **Forest** (deep green + bone + amber) works well — natural, warm, not templated
- **Why it works:** Green is associated with growth, nature, health — relevant to beauty. Amber adds warmth. Bone keeps it light and airy.
- **Avoid:** Beige+brass (templated), Black+white (funeral), Purple gradient (AI-tell)

### Typography
- **Outfit** works as Inter alternative — similar readability, different DNA
- **Avoid:** Playfair Display (AI-default serif), Inter (AI-default sans)

### Layout
- No cards — use offset 2-col grid, filled lists, or subtitle tables
- Services: grid of items with thin lines (not card shadows)
- Prices: two-column layout, not tables (still shows ranges clearly)
- Navigation: omit fixed nav unless the page is long enough to scroll

### Business Context Check
- Before delivering: ask "Would a 30-year-old woman in Poznyaky feel this salon is for her?"
- If the answer is "it looks cool but cold" → wrong direction
- If the answer is "it looks professional and warm" → right direction

---

## Process Pattern (learned from this session)

When user says "сходи поищи ещё знаний" or equivalent:

1. **STOP** — do not defend or explain. They are right.
2. **SEARCH** — look at external references (Awwwards, siteInspire, YouTube, actual sites)
3. **IDENTIFY** — what specific rule did you break?
4. **FIX** — apply the rule, not a guess
5. **VERIFY** — Pre-Flight Check before showing
6. **SHOW** — then ask for opinion

This pattern is distinct from "fix bug X" — design feedback loops require looking at external references, not just iterating internally.
