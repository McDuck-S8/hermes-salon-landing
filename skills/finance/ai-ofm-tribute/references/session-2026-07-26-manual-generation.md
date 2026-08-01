# Session 2026-07-26 Manual Generation — Session 92 (Realistic Style)

**Date:** 2026-07-26  
**Session:** 92  
**Style:** realistic  
**Model:** flux  
**Images requested:** 5  
**Images successful:** 1 (20%)  
**Images failed:** 4 (80%)  
**Failure mode:** SSL certificate verification errors (CERTIFICATE_VERIFY_FAILED / UNEXPECTED_EOF_WHILE_READING)

## Command Executed
```bash
cd D:/Portable_Soft/hermes/projects/ai-ofm-tribute
python scripts/generate.py --count 5 --style realistic --session 92 --model flux --width 768 --height 1024 --delay 2.0
```

## Results

| # | Filename | Seed | Size | Status | Error |
|---|----------|------|------|--------|-------|
| 1 | realistic_92_01.jpg | 406321 | 58 KB | ✅ Success | — |
| 2 | realistic_92_02.jpg | 655546 | — | ❌ Fail | SSL: UNEXPECTED_EOF_WHILE_READING |
| 3 | realistic_92_03.jpg | 908757 | — | ❌ Fail | SSL: CERTIFICATE_VERIFY_FAILED |
| 4 | realistic_92_04.jpg | 927364 | — | ❌ Fail | SSL: CERTIFICATE_VERIFY_FAILED |
| 5 | realistic_92_05.jpg | 630959 | — | ❌ Fail | SSL: CERTIFICATE_VERIFY_FAILED |

## Output Location
```
D:/Portable_Soft/hermes/projects/ai-ofm-tribute/content/sessions/92/
├── manifest.json
├── preview.html
└── realistic_92_01.jpg (58 KB)
```

## Style Index State
- **Before run:** 2 (realistic) — set by cron job session 88
- **After run:** 2 (realistic) — manual run doesn't advance index
- **Next cron run:** Will advance 2→0 (fantasy)

## Key Findings
1. **SSL errors from Pollinations.ai** — 4/5 requests failed with SSL certificate verification failures. This is a new failure mode not seen in prior sessions (previously timeouts/HTTP 500/429).
2. **Flux model unreliable for realistic style** — 1/5 success (20%) is the worst performance for flux across all styles.
3. **Single success image is high quality** — 58 KB, properly generated.
4. **Cron path restriction still active** — The Hermes cron job (`ai-ofm-generate`) still fails with "Blocked: script path resolves outside the scripts directory" because it points to `projects/ai-ofm-tribute/scripts/cron.sh` instead of a wrapper in `scripts/`.

## Model Reliability Update (Including This Session)

| Model | Fantasy | Anime | Realistic | Overall | Status |
|-------|---------|-------|-----------|---------|--------|
| turbo | 100% (5/5) | — | 40% | ~70% | Best for fantasy |
| flux | 30% | 80% (4/5) | **20% (1/5 + 1/5 = 2/10)** | ~47% | Best quality; SSL issues on realistic |
| seedream | 0% | 0% | 0% | 0% | **Broken — 7 confirmed sessions** |
| nanobanana | — | — | — | — | Untested |

## Recommendations
1. **Add retry logic with exponential backoff** to `generate.py` for SSL/connection errors
2. **Consider model fallback** — if flux fails, auto-retry with turbo
3. **Test turbo model** for realistic style with `--delay 12`
4. **Fix cron wrapper** — deploy `scripts/ai-ofm-generate.sh` to `HERMES_HOME/scripts/`
5. **Remove seedream from model choices** in `generate.py` (argparse choices)
6. **Increase default `--delay`** from 2.0 to 5.0 in `generate.py`

## Related Sessions
- `session-2026-07-26-cron-generation.md` — Cron session 88 (fantasy, 5/5 flux)
- `session-2026-07-26-generation.md` — Manual session 87 (anime, 4/5 flux)
- `session-2026-07-25-generation.md` — 6 sessions, 30 images, 33% success