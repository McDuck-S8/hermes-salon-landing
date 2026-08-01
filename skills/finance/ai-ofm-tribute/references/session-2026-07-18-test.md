# AI OFM Tribute — Session 2026-07-18 Test Run

## Summary
Cron-triggered test run to verify generator works after previous cron path error. Direct execution of `scripts/generate.py` since cron.sh path was invalid.

## Generated Sessions

| Session | Style | Model | Attempted | Generated | Failed | Success Rate | Output Path |
|---------|-------|-------|-----------|-----------|--------|--------------|-------------|
| 37 | fantasy | flux | 5 | 2 | 3 | 40% | content/sessions/37/ |
| 38 | fantasy | seedream | 5 | 0 | 5 | 0% | content/sessions/38/ |
| 39 | fantasy | turbo | 5 | 5 | 0 | 100% | content/sessions/39/ |

**Total: 7/15 images (47% overall, but 100% on turbo)**

## Model Reliability — Updated

| Model | Status | Notes |
|-------|--------|-------|
| **turbo** | ✅ **RECOMMENDED** | 5/5 success, ~90KB/image, fast |
| **flux** | ⚠️ UNSTABLE | 2/5 success; SSL/EOF errors (network, not model) |
| **seedream** | ❌ BROKEN | 0/5 success; HTTP 500 Internal Server Error |

> **Action:** Default model in generate.py should be changed from `flux` to `turbo`.

## Style Rotation
- Style index was `2` (realistic) → updated to `1` (anime)
- Next cron run will generate **anime** style
- Rotation: fantasy (0) → anime (1) → realistic (2) → fantasy...

## Files Created/Modified
- `content/sessions/37/` — fantasy/flux (2 images)
- `content/sessions/38/` — fantasy/seedream (0 images)
- `content/sessions/39/` — fantasy/turbo (5 images, **production ready**)
- `content/.style_index` — updated from `2` → `1`

## Issues Found
1. **Cron path mismatch** — Cron job looks for `scripts/cron.sh` under HERMES_HOME/scripts but actual script is at `projects/ai-ofm-tribute/scripts/cron.sh`
2. **Default model** — `flux` default has SSL reliability issues; `turbo` is stable
3. **count mismatch** — Project cron.sh has `--count 3` but skill version has `--count 5` (skill is correct per requirement)

## Next Cron Run
- **Style:** anime (index 1)
- **Model:** turbo (recommended)
- **Count:** 5
- **Expected session:** 40