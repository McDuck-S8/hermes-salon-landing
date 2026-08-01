---
name: ai-ofm-tribute
description: AI OFM Tribute Channel — Automated AI model image generation for OFM (OnlyFans Models) tribute content. Uses Pollinations.ai (free, no API key) to generate fantasy/anime/realistic images on cron schedule. Cycles through styles, produces session manifests and preview galleries.
tags: [ai-ofm, content-generation, pollinations, automation, cron, finance, arbitrage]
related_skills: [pollinations-ai-free-api, content-pipeline, finance-core, autonomous-income-system]
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ai-ofm, content-generation, pollinations, automation, cron, finance, arbitrage]
    related_skills: [pollinations-ai-free-api, content-pipeline, finance-core, autonomous-income-system]
---

# AI OFM Tribute — Automated Content Generation

**Class-level skill** for operating the AI OFM Tribute channel: a fully automated pipeline that generates AI model images via Pollinations.ai (free, no API key), organizes them into sessions with manifests, and produces preview galleries.

## What This Skill Covers

- **Generator script** (`scripts/generate.py`) — Python CLI for batch image generation with style/model/count control
- **Cron automation** (`scripts/cron.sh`) — Round-robin style cycling, runs every 2 hours
- **Session management** — Auto-incrementing sessions, manifest.json, preview.html galleries
- **Style system** — Fantasy / Anime / Realistic with curated prompts and captions
- **Model selection** — flux (best), turbo (fast), seedream (broken), nanobanana (untested)
- **Output structure** — `content/sessions/NN/` with images + metadata + HTML preview

## Quick Start

```bash
# Generate 5 fantasy images (flux model)
cd D:/Portable_Soft/hermes/projects/ai-ofm-tribute
python scripts/generate.py --count 5 --style fantasy --model flux

# Generate 5 anime images (turbo model)
python scripts/generate.py --count 5 --style anime --model turbo

# Generate 5 fantasy images (turbo model, reliable with 12s delay) — RECOMMENDED
python scripts/generate.py --count 5 --style fantasy --model turbo --delay 12

# Run cron job manually (cycles style, generates 3 images)
bash scripts/cron.sh
```

## Architecture

```
projects/ai-ofm-tribute/
├── scripts/
│   ├── generate.py      # Main generator (this skill: scripts/generate.py)
│   └── cron.sh          # Cron wrapper (this skill: scripts/cron.sh)
├── content/
│   ├── .style_index     # Round-robin index (0=fantasy, 1=anime, 2=realistic)
│   └── sessions/
│       ├── 01/
│       │   ├── fantasy_01_01.jpg
│       │   ├── ...
│       │   ├── manifest.json
│       │   └── preview.html
│       └── 02/
└── config.yaml          # Optional: override prompts/captions/styles
```

## Supported Arguments (generate.py)

| Arg | Default | Options | Description |
|-----|---------|---------|-------------|
| `--count` | 5 | 1-50 | Images per session |
| `--style` | fantasy | fantasy, anime, realistic | Art style (determines prompt/caption pool) |
| `--session` | auto | integer | Session number (auto-increments) |
| `--model` | flux | flux, seedream, turbo, nanobanana | Pollinations model |
| `--width` | 768 | 256-2048 | Image width |
| `--height` | 1024 | 256-2048 | Image height |
| `--delay` | 2.0 | 0.5-10.0 | Delay between requests (seconds) |

## Output Per Session

```
session_NN/
├── {style}_NN_01.jpg  ... {style}_NN_NN.jpg
├── manifest.json      # Full metadata: prompts, seeds, captions, model, success flags
└── preview.html       # Interactive dark-theme gallery with real images
```

## Model Reliability (Updated 2026-07-26)

| Model | Fantasy | Anime | Realistic | Overall | Status | Notes |
|-------|---------|-------|-----------|---------|--------|-------|
| **turbo** | **100%** (5/5) | — | ⚠️ 40% (2/5) | **~70%** | ⚠️ **Best for fantasy** | Fast; **100% at `--delay 12` for fantasy**; needs more anime/realistic tests |
| **flux** | ⚠️ **40%** (2/5 + 2/5 = 4/10) | ⚠️ **80%** (4/5) | ⚠️ **30%** (3/10) | **~47%** | ⚠️ **Best for fantasy/anime quality** | Best quality; needs `--delay 5-8` for reliability; hits HTTP 429 without delay; **5th image timeout at 180s recurring (2026-07-24, 2026-07-26×2)**; **SSL errors on all styles (2026-07-26: fantasy 3/5, anime 1/5 timeout, realistic 2/5)** |
| **seedream** | ❌ 0% | ❌ 0% | ❌ 0% | **0%** | ❌ **Broken — DO NOT USE** | HTTP 500 / SSL errors (confirmed 2026-07-15, 2026-07-18, 2026-07-23, 2026-07-24, 2026-07-25, **2026-07-26×2** — **8 sessions**) |
| **nanobanana** | — | — | — | — | ❓ Untested | Unknown |

> **Action Required:** Update `cron.sh` to use style-specific models (flux for fantasy/anime, turbo for realistic, turbo for anime). Change default model in `generate.py` from `flux` to `turbo` for backward compatibility. Add retry logic to `generate.py` for SSL/connection failures. **Remove seedream from model choices.**

## Session History
- **2026-07-26 (cron run)**: **Cron job generated 5 fantasy images (session 88)** — **flux model with 2s delay achieved 5/5 success (100%)** — all 5 images downloaded successfully (80-101 KB each). Session 88 dir: `content/sessions/88/`. Style index was 1 (anime) → advanced to 2 (next: realistic). Cron script still at wrong path (`projects/ai-ofm-tribute/scripts/cron.sh`) but generator ran manually from project dir. See `references/session-2026-07-26-cron-generation.md`.
- **2026-07-26 (morning manual)**: **Manual generation of 5 fantasy images (session 86)** — cron job still blocked by path restriction. **turbo model with `--delay 12` achieved 100% success (5/5)** — first 100% success since 2026-07-23. seedream 0/5 (broken confirmed for **6th session**). flux 43% overall, turbo 100% for fantasy. See `references/session-2026-07-26-generation.md`.
- **2026-07-26 (evening session 87)**: **Manual generation of 5 anime images (session 87)** — cron job still blocked. **flux model with 2s delay achieved 4/5 success (80%)** — 5th image timed out at 180s (recurring). Style index advanced 1→2. See `references/session-2026-07-26-generation.md`.
- **2026-07-26 (session 92)**: **Manual generation of 5 realistic images (session 92)** — **flux model with 2s delay achieved 1/5 success (20%)** — **SSL errors on 4/5 images**. Style index at 2 (realistic). See `references/session-2026-07-26-manual-generation.md`.
- **2026-07-26 (evening sessions 93-95)**: **Manual generation of 3 styles × 5 images (sessions 93-95)** — **flux model at 1024×1536, 3s delay achieved 9/15 success (60%)** — SSL errors on fantasy (3/5) and realistic (2/5), anime 4/5 but 5th timed out at 180s. Session 93: fantasy 2/5; Session 94: anime 4/5 (timeout); Session 95: realistic 3/5. See `references/session-2026-07-26-evening-generation.md`.
- **2026-07-25**: **Manual generation of 30 images across 6 sessions (76-81)** — cron job still blocked by path restriction (`Blocked: script path resolves outside the scripts directory`). Tested 3 models (flux, turbo, seedream) across 3 styles. **seedream 0/5 (broken confirmed for 4th session)**, flux 43% overall, turbo 20% for fantasy. 10/30 images successful (33%). See `references/session-2026-07-25-generation.md`.
- **2026-07-24**: **Two runs recorded:**
  - **Morning (session 64)**: Manual generation of 4/5 fantasy images — cron job blocked by path restriction. 5th image timed out at 180s. Style index updated 0→1 (next: anime). See `references/session-2026-07-24-generation.md`.
  - **Afternoon (sessions 65-74)**: Manual generation of 19 images across 7 sessions — cron job still blocked by path restriction (`Blocked: script path resolves outside the scripts directory`). Tested 3 models (flux, seedream, turbo) across 3 styles. **seedream 0/5 (broken confirmed)**, turbo most reliable (53% overall), flux best for fantasy quality. See `references/session-2026-07-24-afternoon-generation.md`.
- **2026-07-23**: Manual generation of 12 images (4 fantasy + 4 anime + 4 realistic) — cron job blocked by path restriction. See `references/session-2026-07-23-generation.md`.
- **2026-07-23 (cron job session)**: Manual generation of 15 images (5 fantasy + 5 anime + 5 realistic) across sessions 61-63. All 15/15 successful. Style index reset to 0 (fantasy) for next cron run. Model reliability confirmed: flux for fantasy/anime, turbo for realistic. See `references/session-2026-07-23-generation.md`.

## Cron Integration

The project includes `scripts/cron.sh` for automated runs (every 2 hours via system cron or Hermes cron job).

**Current cron.sh behavior:**
- Cycles style via `content/.style_index` (fantasy → anime → realistic → repeat)
- Generates **5 images** per run (updated 2026-07-15 from 3 to match requirement)
- **Uses style-specific models** (flux for fantasy/anime, turbo for realistic)
- **Uses `--delay 5-8` to avoid rate limiting (HTTP 429)**

> **⚠️ Sync Note (2026-07-17, still pending deploy):** The skill's copy of `cron.sh` (in `scripts/cron.sh`) has `--count 5` and style-specific models/delays, but the project's actual `cron.sh` at `projects/ai-ofm-tribute/scripts/cron.sh` still has `--count 3` and uses default model. They need to be synced. The skill's `templates/ai-ofm-generate-wrapper.sh` also needs to be deployed to `scripts/ai-ofm-generate.sh` for the Hermes cron job to work.

**Known Recurring Issue: 5th Image Timeout**
- **Pattern:** Sequential 5-image generation with 2s delay + slow Pollinations responses exceeds 180s terminal timeout on the 5th request
- **Observed:** 2026-07-24 (session 64), 2026-07-26 (session 87)
- **Workarounds:** Increase cron terminal timeout; use `--delay 1` with turbo model; make generator resumable; split into 2+ batch calls from cron

**Hermes Cron Job Configuration (jobs.json):**

The Hermes cron job `ai-ofm-generate` (id: `fbb3a8e05695`) currently points to the WRONG path:
```json
"script": "projects/ai-ofm-tribute/scripts/cron.sh"
```

This causes "Script not found" errors because the cron runner looks for scripts under `HERMES_HOME/scripts/`.

**Fix Options:**
1. **Wrapper script** (recommended): Create `scripts/ai-ofm-generate.sh` that calls the project script
2. **Move project script**: Move `projects/ai-ofm-tribute/scripts/cron.sh` → `scripts/projects/ai-ofm-tribute/scripts/cron.sh`
3. **Update jobs.json**: Change script path to absolute or use workdir

**Wrapper Script Example (`scripts/ai-ofm-generate.sh`):**
```bash
#!/bin/bash
cd "D:/Portable_Soft/hermes/projects/ai-ofm-tribute" && bash scripts/cron.sh
```

Then update jobs.json:
```json
"script": "ai-ofm-generate.sh"
```

> **Update (2026-07-15):** Changed `--count 3` → `--count 5` in cron.sh to match the "5 images per session" requirement. See `references/session-2025-07-15-test-run.md` for details.

## Configuration (config.yaml)

Optional override file at project root:

```yaml
styles: ["fantasy", "anime", "realistic"]
prompts:
  fantasy:
    - "Your custom fantasy prompt..."
  anime:
    - "Your custom anime prompt..."
  realistic:
    - "Your custom realistic prompt..."
captions:
  fantasy:
    - "Your fantasy caption..."
  anime:
    - "Your anime caption..."
  realistic:
    - "Your realistic caption..."
```

## Pollinations.ai Reference

See `pollinations-ai-free-api` skill for full API docs. Key endpoints:
- **GET** `https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1024&seed=42&model=flux` — no key, free
- **POST** `https://gen.pollinations.ai/v1/images/generations` — OpenAI-compatible, needs API key (free tier at enter.pollinations.ai)

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| HTTP 429 (rate limit) | Pollinations API throttling | Use `--delay 5` (or higher) between requests; both flux and turbo need delays |
| HTTP 500 from seedream | Pollinations backend down | Use flux or turbo instead |
| Timeout (>30s) | Network or Pollinations load | Retry with same seed; increase timeout |
| Small file (<1KB) | Error response (HTML) not image | Generator checks size, marks as FAIL |
| Style not cycling | `.style_index` not updating | Check cron.sh write permissions |
| **Cron job "Script not found"** | Path mismatch: cron job points to `scripts/projects/ai-ofm-tribute/scripts/cron.sh` but actual path is `projects/ai-ofm-tribute/scripts/cron.sh` | **Fix:** Move script to `scripts/projects/ai-ofm-tribute/scripts/cron.sh` OR update jobs.json to use correct path OR create wrapper in `scripts/` that calls the project script |
| **5th image timeout (180s)** | Sequential downloads with 2s delay + slow Pollinations responses exceed terminal timeout | Increase terminal timeout for cron job, or use `--delay 1` with faster model (turbo), or make generator resumable. See `references/session-2026-07-24-generation.md`. |
| **Cron job "Blocked: script path resolves outside"** | Cron job points to `projects/ai-ofm-tribute/scripts/cron.sh` but cron runner expects scripts under `HERMES_HOME/scripts/` | **Fix (2026-07-18, still pending deploy):** Create wrapper script at `scripts/ai-ofm-generate.sh` that `cd`s to project and calls `scripts/cron.sh`. Update jobs.json to use `ai-ofm-generate.sh`. See `references/session-2026-07-18-cron-fix.md`, `references/session-2026-07-23-generation.md`, `references/session-2026-07-24-generation.md`. |
| **5th image timeout (180s)** | Sequential downloads with 2s delay + slow Pollinations responses exceed terminal timeout | **Recurring:** 2026-07-24 (session 64), 2026-07-26 (session 87), 2026-07-26 (session 94). Fix: increase terminal timeout, use `--delay 1` with turbo, or make generator resumable. See `references/session-2026-07-24-generation.md`, `references/session-2026-07-26-evening-generation.md`. |
| **SSL/connection errors from Pollinations.ai** | Pollinations.ai backend returning SSL errors (UNEXPECTED_EOF_WHILE_READING, CERTIFICATE_VERIFY_FAILED) on ~40% of requests | **New failure mode (2026-07-26):** Affects all styles with flux model. Fix: add retry logic with exponential backoff to `generate.py`, implement model fallback to turbo. See `references/session-2026-07-26-manual-generation.md`, `references/session-2026-07-26-evening-generation.md`. |
## Session Test Reference

**Files:**
- `references/session-2025-07-15-test-run.md` — 7 test sessions (35 images) on 2026-07-15
- `references/session-2026-07-15-report.md` — 2026-07-15 cron run report
- `references/session-2026-07-17-cron-run.md` — 2026-07-17 cron run report
- `references/session-2026-07-18-cron-fix.md` — 2026-07-18 cron path fix + model reliability findings
- `references/session-2026-07-18-cron-run.md` — 2026-07-18 **cron job run** (session 43)
- `references/session-2026-07-18-generation.md` — 2026-07-18 manual generation run (sessions 37-39)
- `references/session-2026-07-18-test.md` — 2026-07-18 test run report
- `references/session-2026-07-23-generation.md` — 2026-07-23 manual generation run (12 images, cron still blocked)
- `references/session-2026-07-24-afternoon-generation.md` — 2026-07-24 afternoon run (7 sessions, 35 images, 20% success)
- `references/session-2026-07-24-generation.md` — 2026-07-24 manual generation run (4/5 images, 5th timed out, cron still blocked)
- `references/session-2026-07-24-cron-session.md` — 2026-07-24 cron session: anime style, turbo model, 4/5 success, cron path block still active
- `references/session-2026-07-25-generation.md` — 2026-07-25 manual generation run (6 sessions, 30 images, 33% success, cron still blocked)
- `references/session-2026-07-26-generation.md` — 2026-07-26 manual generation (session 86, 5/5 turbo fantasy, 100%, cron still blocked)
- `references/session-2026-07-26-cron-generation.md` — 2026-07-26 cron generation (session 88, 5/5 flux fantasy, 100%, style_index 1→2)
- `references/session-2026-07-26-manual-generation.md` — 2026-07-26 manual generation (session 92, realistic, 1/5 flux, SSL errors)
- `references/session-2026-07-26-evening-generation.md` — 2026-07-26 evening generation (sessions 93-95, 3 styles, 9/15 flux, SSL errors, timeout on 5th)

Contains full transcripts of all test sessions and cron runs, including:
- Success/failure counts per model
- Output paths
- Model reliability conclusions
- Next cron run predictions

This skill feeds the `content-pipeline` (finance/content-pipeline) for the **Create** phase:
1. **Research** → Trending styles/keywords (separate)
2. **Create** ← **THIS SKILL** generates raw image assets
3. **Publish** → Telegram, web, social (content-pipeline publish.py)
4. **Repurpose** → Variations, formats (content-pipeline repurposing matrix)
5. **Analyze** → Performance tracking (content-pipeline analysis)

## Files in This Skill

| File | Type | Purpose |
|------|------|---------|
| `scripts/generate.py` | script | Main generator CLI |
| `scripts/cron.sh` | script | Cron wrapper (style cycling) |
| `references/session-2025-07-15-test-run.md` | reference | Test run transcript & findings |
| `references/session-2026-07-18-cron-fix.md` | reference | Cron path fix + model reliability findings (2026-07-18) |
| `references/session-2026-07-24-afternoon-generation.md` | reference | 2026-07-24 afternoon run (7 sessions, 35 images, 20% success) |
| `references/session-2026-07-24-generation.md` | reference | 2026-07-24 manual generation + timeout findings (morning) |
| `references/session-2026-07-24-cron-session.md` | reference | 2026-07-24 cron session: anime style, turbo model, 4/5 success, cron path block still active |
| `references/session-2026-07-25-generation.md` | reference | 2026-07-25 manual generation run (6 sessions, 30 images, 33% success, cron still blocked) |
| `references/session-2026-07-26-generation.md` | reference | 2026-07-26 manual generation (session 86, 5/5 turbo fantasy, 100%, cron still blocked) |
| `references/session-2026-07-26-cron-generation.md` | reference | 2026-07-26 cron generation (session 88, 5/5 flux fantasy, 100%, style_index 1→2) |
| `references/session-2026-07-26-manual-generation.md` | reference | 2026-07-26 manual generation (session 92, realistic, 1/5 flux, SSL errors) |
| `references/session-2026-07-26-evening-generation.md` | reference | 2026-07-26 evening generation (sessions 93-95, 3 styles, 9/15 flux, SSL errors, timeout on 5th) |

## Maintenance Notes

- **Update prompts/captions** in `generate.py` DEFAULT_CONFIG or via `config.yaml`
- **Monitor seedream** — check if Pollinations fixes HTTP 500 (broken since 2026-07-15, confirmed 4+ sessions)
- **Add nanobanana test** when time permits
- **Cron count** — update to 5 if 5/session is hard requirement
- **Session cleanup** — old sessions accumulate; consider retention policy
- **DEPLOY CRON WRAPPER** — The Hermes wrapper script `scripts/ai-ofm-generate.sh` must be copied to `HERMES_HOME/scripts/ai-ofm-generate.sh` for cron to work. Current cron fails with "Blocked: script path resolves outside the scripts directory". This has been outstanding since 2026-07-18.
- **Add retry logic to generate.py** — Retry on SSL/timeout errors with exponential backoff (high priority)
- **Remove seedream from model choices** — It's been broken for 4+ test sessions (2026-07-15, 2026-07-18, 2026-07-23, 2026-07-24, 2026-07-25)
- **Consider model fallback** — If flux fails, auto-fallback to turbo
- **Increase default delay** — Change `--delay` default from 2.0 to 5.0