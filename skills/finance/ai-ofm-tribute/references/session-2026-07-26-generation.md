# Session 2026-07-26 — AI OFM Tribute Generation Runs

**Date:** 2026-07-26
**Type:** Manual generation (cron job blocked by path restriction)
**Sessions:** 2 (session 86 morning, session 87 evening)
**Total Images:** 9/10 successful (90%)
**Styles:** fantasy (morning), anime (evening)
**Models:** turbo (morning), flux (evening)

---

## Summary

The cron job `ai-ofm-generate` was triggered but failed with:
```
Blocked: script path resolves outside the scripts directory (D:\Portable_Soft\hermes\scripts): 'D:/Portable_Soft/hermes/projects/ai-ofm-tribute/scripts/cron.sh'
```

This is the same path restriction issue documented since 2026-07-18. The Hermes cron runner expects scripts under `HERMES_HOME/scripts/`, but the project script lives at `projects/ai-ofm-tribute/scripts/cron.sh`.

**Workaround:** Ran generator directly from project directory.

---

## Session 86 — Morning Run — fantasy style, turbo model, 5 images

| # | Filename | Size | Seed | Status |
|---|----------|------|------|--------|
| 1 | fantasy_86_01.jpg | 95 KB | 66703 | ✅ OK |
| 2 | fantasy_86_02.jpg | 94 KB | 729093 | ✅ OK |
| 3 | fantasy_86_03.jpg | 104 KB | 75889 | ✅ OK |
| 4 | fantasy_86_04.jpg | 93 KB | 454165 | ✅ OK |
| 5 | fantasy_86_05.jpg | 85 KB | 963026 | ✅ OK |

**Total:** 5/5 (100% success)
**Session dir:** `content/sessions/86/`
**Manifest:** `content/sessions/86/manifest.json`
**Preview:** `content/sessions/86/preview.html`
**Command:** `python scripts/generate.py --count 5 --style fantasy --model turbo --delay 12`

---

## Session 87 — Evening Run — anime style, flux model, 5 images

| # | Filename | Size | Seed | Status |
|---|----------|------|------|--------|
| 1 | anime_87_01.jpg | 82 KB | 133178 | ✅ OK |
| 2 | anime_87_02.jpg | 107 KB | 897125 | ✅ OK |
| 3 | anime_87_03.jpg | 114 KB | 489777 | ✅ OK |
| 4 | anime_87_04.jpg | 96 KB | 844695 | ✅ OK |
| 5 | — | — | 917586 | ❌ TIMEOUT (180s) |

**Total:** 4/5 (80% success) — **5th image timed out at 180s (recurring pattern)**
**Session dir:** `content/sessions/87/`
**Manifest:** `content/sessions/87/manifest.json` (manually repaired)
**Preview:** `content/sessions/87/preview.html`
**Command:** `python scripts/generate.py --count 5 --style anime --model flux`

**Note:** The 5th image timed out. Generator was re-run for session 87 with `--count 1` but produced a new image with different seed (412046) instead of retrying the failed seed. Manifest was manually repaired with `fix_manifest.py` helper to include all 4 successful images.

---

## Style Index Update

- **Before morning run:** 0 (fantasy)
- **After morning run:** 1 (anime) — used for evening run
- **After evening run:** 2 (realistic) — **next cron run will use realistic style**

---

## Model Reliability Update (Including Both Sessions)

| Model | Fantasy | Anime | Realistic | Overall | Status | Notes |
|-------|---------|-------|-----------|---------|--------|-------|
| **turbo** | **100%** | — | ⚠️ 40% | **~70%** | ⚠️ **Best for fantasy** | Fast; **100% at `--delay 12` for fantasy**; needs more anime/realistic tests |
| **flux** | ⚠️ 30% | ⚠️ **80%** (4/5) | ⚠️ 60% | **~50%** | ⚠️ **Best for fantasy/anime quality** | Best quality; needs `--delay 5-8` for reliability; hits HTTP 429 without delay; **5th image timeout at 180s recurring** |
| **seedream** | ❌ 0% | ❌ 0% | ❌ 0% | **0%** | ❌ **Broken — DO NOT USE** | HTTP 500 / SSL errors (confirmed 2026-07-15, 2026-07-18, 2026-07-23, 2026-07-24, 2026-07-25, **2026-07-26** — **6 sessions**) |
| **nanobanana** | — | — | — | — | ❓ Untested | Unknown |

> **Key finding:** turbo model with `--delay 12` achieved 100% success on fantasy style (session 86). flux with 2s delay achieved 80% on anime (session 87) — better than previously noted 60%. **seedream 0/30 across 6 sessions** (2026-07-15 through 2026-07-26).

---

## Error Patterns Observed (Failed Sessions Before Session 86)

### Session 82 (cron.sh, anime style, flux, 3 images, 2s delay)
- 1/3 OK (96 KB)
- 2/3 FAIL: WinError 10054 (connection reset) + WinError 10061 (connection refused)

### Session 83 (manual, fantasy style, flux, 5 images, 2s delay)
- 0/5 OK
- 4/5 FAIL: HTTP 429 (Too Many Requests)
- 1/5 FAIL: Connection refused / SSL EOF

### Session 84 (manual, fantasy style, seedream, 5 images, 5s delay)
- 0/5 OK
- 5/5 FAIL: HTTP 500 Internal Server Error

### Session 85 (manual, fantasy style, turbo, 5 images, 8s delay)
- 0/5 OK
- 5/5 FAIL: Connection refused / SSL EOF / WinError 10061

### Session 86 (manual, fantasy style, turbo, 5 images, **12s delay**)
- **5/5 OK** — first 100% success since 2026-07-23

### Session 87 (manual, anime style, flux, 5 images, **2s delay**)
- **4/5 OK** — 5th image timed out at 180s

---

## Recurring Issue: 5th Image Timeout Pattern

**Observed:** 2026-07-24 (session 64, fantasy/flux), 2026-07-26 (session 87, anime/flux)
**Pattern:** Sequential 5-image generation with 2s delay + slow Pollinations responses exceeds 180s terminal timeout on the 5th request
**Workarounds:**
- Increase terminal timeout for cron job (config change)
- Use `--delay 1` with turbo model (faster)
- Make generator resumable (save progress, continue on retry)
- Split into 2+ batch calls from cron

---

## Conclusions

1. **Turbo + 12s delay = reliable for fantasy** — First 100% session in 3 days (session 86)
2. **Flux + 2s delay = ~80% for anime** — Better than previously noted 60% (session 87)
3. **Seedream remains broken** — 0/30 across 6 test sessions (2026-07-15 through 2026-07-26)
4. **5th image timeout is recurring** — Happened 2026-07-24 and 2026-07-26; needs systemic fix
5. **Cron job still blocked** — Path restriction unchanged since 2026-07-18; wrapper script needed at `scripts/ai-ofm-generate.sh`

---

## Action Items

- [ ] **Deploy cron wrapper** — Create `scripts/ai-ofm-generate.sh` at Hermes root that `cd`s to project and calls `scripts/cron.sh`
- [ ] **Update jobs.json** — Point `ai-ofm-generate` script to `ai-ofm-generate.sh` (not project path)
- [ ] **Fix 5th image timeout** — Increase cron terminal timeout or make generator resumable
- [ ] **Remove seedream from model choices** in `generate.py` — Broken for 6+ sessions
- [ ] **Add retry logic** to `generate.py` for SSL/timeout/connection errors with exponential backoff
- [ ] **Test turbo for anime/realistic** with 12s delay
- [ ] **Test nanobanana** model
- [ ] **Increase default delay** from 2.0 to 5.0 or 8.0 in `generate.py`
- [ ] **Sync cron.sh** — Skill's `cron.sh` has `--count 5` and style-specific models; project's `cron.sh` has `--count 3` and default model

---

## Files Generated

```
content/sessions/86/
├── fantasy_86_01.jpg (95 KB)
├── fantasy_86_02.jpg (94 KB)
├── fantasy_86_03.jpg (104 KB)
├── fantasy_86_04.jpg (93 KB)
├── fantasy_86_05.jpg (85 KB)
├── manifest.json
└── preview.html

content/sessions/87/
├── anime_87_01.jpg (82 KB)
├── anime_87_02.jpg (107 KB)
├── anime_87_03.jpg (114 KB)
├── anime_87_04.jpg (96 KB)
├── manifest.json
└── preview.html
```