# Session 2026-07-26 Evening Generation — Sessions 93, 94, 95 (3 Styles)

**Date:** 2026-07-26 (evening)  
**Sessions:** 93 (fantasy), 94 (anime), 95 (realistic)  
**Models:** flux (all)  
**Images requested:** 15 (5 per session)  
**Images successful:** 9 (60%)  
**Images failed:** 6 (40%)

## Commands Executed

```bash
# Session 93 - Fantasy
cd D:/Portable_Soft/hermes/projects/ai-ofm-tribute
python scripts/generate.py --count 5 --style fantasy --model flux --width 1024 --height 1536 --delay 3

# Session 94 - Anime
python scripts/generate.py --count 5 --style anime --model flux --width 1024 --height 1536 --delay 3

# Session 95 - Realistic
python scripts/generate.py --count 5 --style realistic --model flux --width 1024 --height 1536 --delay 3
```

## Results Summary

| Session | Style | Requested | ✅ Success | ❌ Failed | Success Rate | Notes |
|---------|-------|-----------|-----------|----------|--------------|-------|
| 93 | fantasy | 5 | 2 | 3 | 40% | SSL errors (3) |
| 94 | anime | 5 | 4 | 1* | 80% | 5th timed out at 180s |
| 95 | realistic | 5 | 3 | 2 | 60% | SSL errors (2) |
| **TOTAL** | **3 styles** | **15** | **9** | **6** | **60%** | |

*Session 94: 5th image request timed out at 180s terminal limit; no manifest/preview generated.

## Detailed Results

### Session 93 — Fantasy (1024×1536, flux, delay 3s)

| # | Filename | Seed | Size | Status | Error |
|---|----------|------|------|--------|-------|
| 1 | fantasy_93_01.jpg | 551603 | 115 KB | ✅ Success | — |
| 2 | fantasy_93_02.jpg | 274122 | 99 KB | ✅ Success | — |
| 3 | fantasy_93_03.jpg | 252782 | — | ❌ Fail | Remote end closed connection |
| 4 | fantasy_93_04.jpg | 80450 | — | ❌ Fail | SSL: UNEXPECTED_EOF_WHILE_READING |
| 5 | fantasy_93_05.jpg | 701664 | — | ❌ Fail | SSL: UNEXPECTED_EOF_WHILE_READING |

**Output:** `content/sessions/93/` — manifest.json, preview.html, 2 images

### Session 94 — Anime (1024×1536, flux, delay 3s)

| # | Filename | Seed | Size | Status | Error |
|---|----------|------|------|--------|-------|
| 1 | anime_94_01.jpg | 393092 | 81 KB | ✅ Success | — |
| 2 | anime_94_02.jpg | 276817 | 73 KB | ✅ Success | — |
| 3 | anime_94_03.jpg | 24635 | 83 KB | ✅ Success | — |
| 4 | anime_94_04.jpg | 327961 | 94 KB | ✅ Success | — |
| 5 | anime_94_05.jpg | 309761 | — | ❌ Fail | **Timeout at 180s** |

**Output:** `content/sessions/94/` — 4 images only (no manifest/preview due to timeout)

### Session 95 — Realistic (1024×1536, flux, delay 3s)

| # | Filename | Seed | Size | Status | Error |
|---|----------|------|------|--------|-------|
| 1 | realistic_95_01.jpg | 558664 | — | ❌ Fail | SSL error |
| 2 | realistic_95_02.jpg | 858659 | 69 KB | ✅ Success | — |
| 3 | realistic_95_03.jpg | 43205 | 51 KB | ✅ Success | — |
| 4 | realistic_95_04.jpg | 329137 | 47 KB | ✅ Success | — |
| 5 | realistic_95_05.jpg | 106405 | — | ❌ Fail | SSL error |

**Output:** `content/sessions/95/` — manifest.json, preview.html, 3 images

## Key Findings

1. **SSL/connection errors persist** — Pollinations.ai returning SSL errors (UNEXPECTED_EOF_WHILE_READING, CERTIFICATE_VERIFY_FAILED) on ~40% of requests across all styles
2. **5th image timeout recurs** — Session 94 timed out on 5th request at 180s (same pattern as 2026-07-24 session 64, 2026-07-26 session 87)
3. **Flux at 1024×1536 less reliable** — Higher resolution + 3s delay = more timeouts/SSL errors vs previous 768×1024 runs
4. **Anime style most reliable with flux** — 80% success (4/5) despite timeout on 5th
5. **No manifest/preview on timeout** — Generator crashes before writing manifest when terminal times out

## Model Reliability Update (Including This Session)

| Model | Fantasy | Anime | Realistic | Overall | Status | Notes |
|-------|---------|-------|-----------|---------|--------|-------|
| **turbo** | **100%** (5/5) | — | 40% | **~70%** | ⚠️ **Best for fantasy** | Fast; 100% at `--delay 12` for fantasy; needs more anime/realistic tests |
| **flux** | 40% (2/5) | **80%** (4/5) | 40% (3/10) | **~50%** | ⚠️ **Best quality** | SSL errors on all styles; needs `--delay 5-8`; 5th image timeout recurring |
| **seedream** | 0% | 0% | 0% | **0%** | ❌ **Broken** | HTTP 500/SSL errors (7 confirmed sessions: 2026-07-15, 18, 23, 24, 25, 26×2) |
| **nanobanana** | — | — | — | — | ❓ Untested | Unknown |

## Recommendations

1. **Add retry logic with exponential backoff** to `generate.py` for SSL/connection/timeout errors (HIGH PRIORITY)
2. **Remove seedream from argparse choices** — broken for 7+ sessions
3. **Increase default `--delay`** from 2.0 to 5.0 in `generate.py`
4. **Add model fallback** — auto-retry failed requests with turbo model
5. **Fix 5th image timeout** — increase cron terminal timeout, or use `--delay 1` with turbo, or make generator resumable
6. **Deploy cron wrapper** — copy `scripts/ai-ofm-generate.sh` to `HERMES_HOME/scripts/` (blocked since 2026-07-18)
7. **Consider lower resolution for cron** — 768×1024 more reliable than 1024×1536
8. **Make manifest write incremental** — write after each successful image, not at end

## Style Index State
- **Before run (93):** 0 (fantasy) — advanced by cron session 88 to 1→2→0→1
- **Session 93 (fantasy):** manual, doesn't advance index
- **Session 94 (anime):** manual, doesn't advance index
- **Session 95 (realistic):** manual, doesn't advance index
- **Next cron run:** Will advance from current index (likely 1 = anime) → 2 (realistic)

## Related Sessions
- `session-2026-07-26-cron-generation.md` — Cron session 88 (fantasy, 5/5 flux, 100%)
- `session-2026-07-26-manual-generation.md` — Session 92 (realistic, 1/5 flux, SSL errors)
- `session-2026-07-26-generation.md` — Session 87 (anime, 4/5 flux, timeout on 5th)
- `session-2026-07-25-generation.md` — 6 sessions, 30 images, 33% success