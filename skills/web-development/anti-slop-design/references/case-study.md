# Case Study: Salon Landing Anti-Slop Redesign

**Date:** 2026-07-10
**Session:** Hermes anti-slop design post-upgrade
**Skill loaded:** `anti-slop-design`

## The Brief

Redesign a beauty salon landing page (https://mcduck-s8.github.io/hermes-salon-landing/) using newly-installed design skills.

**Design Read:** Premium beauty salon landing for discerning female audience (25-45, urban), Cold Luxury + Rose Gold aesthetic, Satoshi + Outfit typography.

**Three Dials:** DESIGN_VARIANCE=7, MOTION_INTENSITY=6, VISUAL_DENSITY=3

## What Happened

1. Loaded `anti-slop-design` skill
2. Built the full page from scratch (asymmetric hero, bento services, editorial about, gallery showcase, testimonials, booking form)
3. Immediately violated **two Pre-Flight rules**:
   - **Em-dash everywhere** — used `&mdash;` and literal `—` in 7+ places (titles, subs, blockquote, hours)
   - **Eyebrow overcount** — put `.section-label` above every section. Had 6 labels on 6 sections, but max allowed was 2.

## The Fix

Ran Pre-Flight Check mentally → found violations → fixed:

### Em-dash cleanup
Scanned file for `&mdash;` and `—` (literal Unicode). Found 7+ instances:
- Title tag: `MÉLANGE — студия` → `MÉLANGE - студия`
- Hero sub: `...до финального штриха — мы создаём...` → replaced with `-`
- Section subs: `Каждая услуга — это...` → `Каждая услуга - это...`
- Blockquote: `Наша задача — не повторить...` → `Наша задача - не повторить...`
- Citation: `— Анна Смирнова` → `- Анна Смирнова`
- Hours: `10:00 — 21:00` → `10:00 - 21:00`
- Gallery sub: `То, что мы делаем — в кадрах` → `То, что мы делаем - в кадрах`
- About sub: `...не гонимся за трендами — мы ищем...` → `- мы ищем`

### Eyebrow cleanup
Removed `.section-label` from 5 sections (services, about, gallery, testimonials, booking). Only kept hero eyebrow (`Студия красоты`). Result: 1 eyebrow on 6 sections = within `ceil(6/3) = 2` limit.

## Lesson

**Even with the full anti-slop skill loaded, the first draft violates the rules.** The Pre-Flight Check is not a formality — it catches violations that the builder's own blind spots miss. The correct process is:

Draft → Run Pre-Flight → Find violations → Fix → Re-check → Ship

This case study validates the Pre-Flight Check as a catch mechanism, not just a documentation artifact.

## Image Sourcing: Russian Audience Pain Point

Images were the most persistent issue:
1. **Unsplash** — timed out or blocked by Russian ISPs. Not reliable.
2. **Picsum.photos** — loaded, but gave random irrelevant content (nature landscapes, phones, food). Contextually wrong for a beauty salon.
3. **Placehold.co** — the winner. Always loads, fast, supports brand colors (`#B76E79` Rose Gold, `#E8D5D8` light rose). Creates thematically coherent placeholders that the client replaces with real photos later.

**Pattern for RU landing pages:** placehold.co/{w}x{h}/{bg}/{fg}?text=... with brand colors. Client swaps `src` to real images before going live.
