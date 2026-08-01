---
name: content-quality-pipeline
description: Class-level skill for producing high-quality social media content by copying proven formats from top performers, not generating generic AI slop. Covers format library, quality gates, multi-platform publishing, and content warehouse management.
---

# Content Quality Pipeline

## Core Principle (USER DIRECTIVE)
> **"Он опять нагенерил воды и рекламных слоганов... Это не контент, а белый шум. Ему нужно перестать придумывать из головы и начать копировать лучших. В соцсетях есть чёткие, рабочие форматы — используй их."**

**NEVER generate content from scratch. ALWAYS:**
1. Research top-performing posts in the niche (Pinterest, YouTube Shorts, TikTok, Telegram)
2. Deconstruct their structure: hook → value → CTA
3. Adapt the structure to your topic
4. Pass quality checklist before publishing

---

## 7 Proven Content Formats (Extracted from Viral Case Studies)

| # | Format | Structure | Viral Example Source |
|---|--------|-----------|---------------------|
| 1 | **Problem → Solution** | "Stop [painful task] manually → I found [tool] that does it in [time] → 3-step setup → CTA" | Emilee Vales YT (4K views) |
| 2 | **Before → After** | "Before: [old way, metric] → After: [new way, metric] → What changed: [1 thing] → Steal my template" | Better Marketing article (Collage pins 42% higher CTR) |
| 3 | **Mistake Analysis** | "I lost $[X] on [mistake] → Here's what went wrong → The fix that saved me next time → Don't repeat my error" | Medium case studies |
| 4 | **Tool Close-up** | "This ONE tool replaces [X, Y, Z] → Watch me [task] in 60 sec → Settings I use → Free tier link" | YouTube Shorts "3 Best AI Tools" (millions of views) |
| 5 | **Comparison / Top-3** | "Top 3 [tools] for [job] → Quick verdict: #1 [name] because [reason] → Pros/cons table → My pick: [link]" | Ryan Doser YT (5.7K views) |
| 6 | **Personal Diary** | "Day 1: $0 / 0 subs → Day 30: $[X] / [Y] subs → 3 things that moved needle → Full breakdown in bio" | 30-day challenge videos |
| 7 | **News / Trend** | "BREAKING: [platform] just [change] → What this means for [niche] → My move: [action] → Details in thread" | Pinterest Predicts 2025 + algo updates |

---

## Shane's 5 Plays → Production Pipeline Templates (2026-07-26 Research)

| Play | Template | Pipeline Application |
|------|----------|---------------------|
| **1. Translator** | Multi-language repurposing → YT → Shorts → TikTok → Reels | `content_factory.py:TranslatorPlay` |
| **2. Juicer** | Long-form → shorts/clips automation (1 video → 20+ clips) | `content_factory.py:JuicerPlay` |
| **3. Documentary** | Research-heavy evergreen → high CPM niches | `content_factory.py:DocumentaryPlay` |
| **4. Campfire** | Narrative-driven engagement → community building | `content_factory.py:CampfirePlay` |
| **5. Buffet** | Curated resource lists → lead magnets → affiliate/CPA | `content_factory.py:BuffetPlay` |

---

## Google Flow Agent + ElevenLabs Integration (2026-07-26)

- **Avatar video generation**: Consistent character across videos
- **Voice cloning**: Consistent narration brand
- **Dialogue automation**: Interview-style videos without guests
- **Implementation**: `scripts/flow_agent_integration.py` (to be created)

---

## Custom Domain Automation (Google AI Studio) (2026-07-26)

- **Format**: `tool.yourdomain.com` → CNAME → auto-verify
- **Use case**: Deploy 10+ AI utility tools as lead magnets
- **Implementation**: `scripts/deploy_custom_domains.py` (to be created)

---

## SEO "AI-Citability" Scorer (2026-07-26)

- **Score factors**: Headings hierarchy, factual density, citation quality, structure clarity
- **Integration**: Pre-publish gate in content pipeline
- **Goal**: Make content cite-worthy for AI search (Perplexity, Google AI Overviews)
- **Implementation**: `scripts/crystal/intelligence.py` → `ai_citability_score()`

---

## Quality Checklist (MANDATORY before publish)

- [ ] **Emotion trigger**: Does it spark curiosity / greed / fear / anger?
- [ ] **Concrete value**: Specific number, fact, or step-by-step instruction?
- [ ] **Personal story**: "I did X, got Y" — not "you should do X"
- [ ] **Image stands alone**: Understandable without reading caption?
- [ ] **Hook in first line**: Stops the scroll?
- [ ] **AI-citability score ≥ 70**: Passes pre-publish gate?

**If ANY answer is "no" → REWRITE. Do not publish.**

---

## Content Warehouse Structure

```
D:/Portable_Soft/hermes/assets/content_warehouse/
├── images/
│   ├── pinterest/
│   ├── telegram/
│   ├── youtube_shorts/
│   └── tiktok/
├── video/
└── metadata/  # JSON per asset: prompt, source, format, niche, performance
```

---

## Multi-Platform Publishing Pipeline

### Telegram (via `telegram_poster.py`)
- **Library**: `python-telegram-bot` v22+ (async) — **direct HTTP fails due to proxy**
- **Channels**: 4 configured (`max_brain_chef_official`, `ai_frontier_you`, `max_brain_chef_ai`, `neuro_kitchen_ai`)
- **Schedule**: 5 posts/day across channels (09:00, 12:00, 15:00, 18:00, 21:00 MSK)
- **Features**: HTML formatting, inline keyboards, photo upload, DB logging

### Pinterest (via `pinterest_auto_pinner.py`)
- **Current**: Dry-run mode (placehold.co images)
- **Target**: Real generation via Bing Image Creator (free, 100/day) + Leonardo AI (150 credits/day)
- **Schedule**: 8 slots/day (08:00-22:00 every 2h)
- **Niches**: ai_tools, finance, tech_reviews

---

## Image Generation Pipeline (Priority Order)

| Priority | Tool | Free Limit | Best For | Access |
|----------|------|------------|----------|--------|
| 1 | **Bing Image Creator** (DALL-E 3) | 100/day | Text-heavy pins, clean typography | Web UI (Microsoft account) |
| 2 | **Leonardo AI** | 150 credits/day | Photorealistic people, ControlNet | Web UI |
| 3 | **Playground AI** | 500/day | Batch variations, style transfer | Web UI |
| 4 | **Fal.ai** (Flux/Nano Banana) | **Paid only** ($0.003/img) | Premium quality when monetizing | API |

**Typography styles**: 65 styles from `https://ai2play.net/typography-art-styles.html` — inject into prompts.

---

## Content Factory Setup (Ghost Browser Automation)

Register accounts on all free tiers using `ghost_browser.py` + `human_behavior.py`:
1. Leonardo AI (leonardo.ai)
2. Playground AI (playgroundai.com)
3. Bing Image Creator (bing.com/create)
4. NightCafe (creator.nightcafe.studio)
5. Clipdrop (clipdrop.co)
6. RunwayML (runwayml.com) — video
7. Pika Labs (pika.art) — video
8. CapCut Web (capcut.com) — editing
9. ElevenLabs (elevenlabs.io) — voice
10. Upscale.media (upscale.media) — enhancement

**Store credentials in IdentityDB (encrypted SQLite)**. Never mix user's API keys with agent's own accounts.

---

## Pitfalls & Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Generate "earn money on autopilot" generic slogans | Copy structure from viral posts in niche |
| Use placehold.co colored rectangles | Generate real images via Bing/Leonardo |
| Post same content everywhere unmodified | Adapt format per platform (Pinterest=vertical 2:3, Telegram=horizontal+buttons) |
| Skip quality checklist | Treat checklist as publish gate |
| Mix user's credentials with agent's | Separate IdentityDB per persona |

---

## References

- `references/7-formats.md` — Detailed breakdown with 5 examples each
- `references/multi-agent-delegation.md` — Multi-agent delegation patterns
- `references/pinterest-winning-formats.md` — Case study synthesis (collage pins win)
- `references/telegram-poster-tech.md` — python-telegram-bot async patterns
- `references/typography-styles.md` — 65 prompt-ready styles from ai2play.net
- `references/shane-5-plays.md` — Shane's 5 plays mapped to pipeline templates (NEW 2026-07-26)
- `references/flow-agent-elevenlabs.md` — Google Flow Agent + ElevenLabs integration (NEW 2026-07-26)
- `references/custom-domain-automation.md` — Google AI Studio custom domain deployment (NEW 2026-07-26)
- `references/ai-citability-scorer.md` — SEO AI-citability pre-publish gate (NEW 2026-07-26)

---

## Scripts

- `scripts/telegram_poster.py` — Multi-channel poster with queue, scheduling, images
- `scripts/pinterest_image_gen.py` — Bing/Leonardo/Fal.ai generation pipeline
- `scripts/content_warehouse.py` — Asset inventory & metadata management
- `scripts/content_factory.py` — Content pipeline with Shane's 5 plays (NEW 2026-07-26)
- `scripts/flow_agent_integration.py` — Google Flow Agent + ElevenLabs (NEW 2026-07-26, to create)
- `scripts/deploy_custom_domains.py` — Custom domain automation (NEW 2026-07-26, to create)