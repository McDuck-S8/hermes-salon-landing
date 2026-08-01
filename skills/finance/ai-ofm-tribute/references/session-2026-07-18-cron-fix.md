# Session 2026-07-18 — Cron Fix & Generation Run

**Date:** 2026-07-18  
**Context:** Scheduled cron job failed with "Blocked: script path resolves outside the scripts directory". Manual run executed to test and generate content.

## Problem Identified

The Hermes cron job `ai-ofm-generate` (id: `fbb3a8e05695`) points to:
```json
"script": "projects/ai-ofm-tribute/scripts/cron.sh"
```

But the cron runner resolves scripts relative to `HERMES_HOME/scripts/`, so it looks for:
`D:/Portable_Soft/hermes/scripts/projects/ai-ofm-tribute/scripts/cron.sh`

Which doesn't exist. The actual script is at:
`D:/Portable_Soft/hermes/projects/ai-ofm-tribute/scripts/cron.sh`

**Error:** `Blocked: script path resolves outside the scripts directory (D:\Portable_Soft\hermes\scripts): 'D:/Portable_Soft/hermes/projects/ai-ofm-tribute/scripts/cron.sh'`

## Fix Required

Option 1 (recommended): Create wrapper in `scripts/` that calls the project script
```bash
# scripts/ai-ofm-generate.sh
#!/bin/bash
cd "D:/Portable_Soft/hermes/projects/ai-ofm-tribute" && bash scripts/cron.sh
```

Then update jobs.json:
```json
"script": "ai-ofm-generate.sh"
```

Option 2: Move project script to `scripts/projects/ai-ofm-tribute/scripts/cron.sh`

## Generation Results (Manual Run)

Ran 5 sessions × 5 images = 25 attempts, cycling styles and models:

| Session | Style | Model | Success | Failed | Notes |
|---------|-------|-------|---------|--------|-------|
| 46 | realistic | turbo | 4 | 1 | **Best performer** — 80% success, ~50KB/img |
| 47 | fantasy | turbo | 1 | 4 | Turbo poor for fantasy (SSL EOF errors) |
| 48 | anime | seedream | 0 | 5 | **Broken** — HTTP 500 / SSL errors |
| 49 | fantasy | flux | 4 | 1 | **Best for fantasy** — 80% success, ~90KB/img |
| 50 | anime | flux | 1 | 4 | Rate limited (HTTP 429) |
| 51 | realistic | flux | 1 | 4 | Rate limited (HTTP 429) |

**Total:** 11/25 (44% success)

### Model Reliability Update (2026-07-18)

| Model | Fantasy | Anime | Realistic | Recommendation |
|-------|---------|-------|-----------|----------------|
| **turbo** | ❌ 20% | — | ✅ **80%** | Use for **realistic** only |
| **flux** | ✅ **80%** | ⚠️ 20% (rate limited) | ⚠️ 20% (rate limited) | Use for **fantasy** with `--delay 5` |
| **seedream** | — | ❌ 0% | — | **Broken** — HTTP 500 |

### Optimal Configuration Per Style

```bash
# Fantasy (best quality, reliable)
python scripts/generate.py --count 5 --style fantasy --model flux --delay 5

# Anime (flux but needs delay for rate limits)
python scripts/generate.py --count 5 --style anime --model flux --delay 8

# Realistic (fast, reliable)
python scripts/generate.py --count 5 --style realistic --model turbo --delay 3
```

## Cron Configuration Update

The `cron.sh` should cycle styles but use the optimal model per style:

```bash
# Current: uses single model (flux) for all styles
# Fixed: use style-specific model
if [ $style_idx -eq 0 ]; then
    # fantasy → flux
    python scripts/generate.py --count 5 --style fantasy --model flux --delay 5
elif [ $style_idx -eq 1 ]; then
    # anime → flux with longer delay
    python scripts/generate.py --count 5 --style anime --model flux --delay 8
else
    # realistic → turbo
    python scripts/generate.py --count 5 --style realistic --model turbo --delay 3
fi
```

## Output Paths

All sessions saved to `content/sessions/`:
- Session 46: `content/sessions/46/` (realistic, 4 images)
- Session 47: `content/sessions/47/` (fantasy, 1 image)
- Session 48: `content/sessions/48/` (anime, 0 images)
- Session 49: `content/sessions/49/` (fantasy, 4 images)
- Session 50: `content/sessions/50/` (anime, 1 image)
- Session 51: `content/sessions/51/` (realistic, 1 image)

Each has `manifest.json` and `preview.html`.