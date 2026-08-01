# Session 2026-07-25 — Manual Generation Run (Cron Still Blocked)

**Date:** 2026-07-25  
**Trigger:** Cron job failed with "Blocked: script path resolves outside the scripts directory" — same issue as 2026-07-18 through 2026-07-24  
**Action:** Manual generation of 5 sessions (76-80) across 3 styles, testing 3 models

---

## Sessions Summary

| Session | Style | Model | Count | Success | Fail | Success Rate | Notes |
|---------|-------|-------|-------|---------|------|--------------|-------|
| 76 | fantasy | flux | 5 | 1 | 4 | 20% | 4 timeouts/connection errors |
| 77 | realistic | flux | 5 | 3 | 2 | 60% | 2 SSL EOF errors |
| 78 | anime | flux | 5 | 3 | 2 | 60% | 2 SSL EOF errors |
| 79 | fantasy | turbo | 5 | 1 | 4 | 20% | 1 HTTP 429, 3 SSL EOF |
| 80 | fantasy | seedream | 5 | 0 | 5 | **0%** | **All HTTP 500 — confirmed broken** |
| 81 | fantasy | flux | 5 | 2 | 3 | 40% | 3 SSL EOF errors |

**Totals:** 30 images requested, 10 successful (33%), 20 failed

---

## Model Reliability Update (2026-07-25)

| Model | Fantasy | Anime | Realistic | Overall | Status |
|-------|---------|-------|-----------|---------|--------|
| **flux** | 30% (2/7) | 60% (3/5) | 60% (3/5) | **43% (8/17)** | ⚠️ Unreliable — needs high delay |
| **turbo** | 20% (1/5) | — | — | **20% (1/5)** | ⚠️ Poor for fantasy |
| **seedream** | 0% (0/5) | — | — | **0% (0/5)** | ❌ **Broken** (HTTP 500) |

**Conclusion:** flux is still best for quality but needs `--delay 5-8`. turbo is faster but unreliable for fantasy. seedream is dead.

---

## Error Patterns Observed

| Error | Frequency | Model(s) | Mitigation |
|-------|-----------|----------|------------|
| `The read operation timed out` | High | flux, turbo | Increase `--delay` to 5-8s |
| `Remote end closed connection without response` | High | flux, turbo | Retry logic needed |
| `SSL: UNEXPECTED_EOF_WHILE_READING` | High | flux, turbo | Network/Pollinations issue; retry |
| `HTTP Error 429: Too Many Requests` | Medium | turbo | Rate limit — need delay |
| `HTTP Error 500: Internal Server Error` | 100% | seedream | **Do not use seedream** |

---

## Style Index State

- **Before:** `content/.style_index` = `2` (realistic)
- **After manual runs:** Not auto-updated (cron.sh not run)
- **Next cron run (if fixed):** Will read index=2 → anime style
- **Note:** Manual runs don't update `.style_index` — only `cron.sh` does

---

## Cron Job Status: **STILL BLOCKED**

**Error:** `Blocked: script path resolves outside the scripts directory (D:\Portable_Soft\hermes\scripts): 'D:/Portable_Soft/hermes/projects/ai-ofm-tribute/scripts/cron.sh'`

**Root Cause:** Hermes cron runner only allows scripts under `HERMES_HOME/scripts/`. The project script is at `projects/ai-ofm-tribute/scripts/cron.sh`.

**Fix Required (since 2026-07-18, still not deployed):**
1. Copy `templates/ai-ofm-generate-wrapper.sh` → `D:/Portable_Soft/hermes/scripts/ai-ofm-generate.sh`
2. Update `jobs.json` to reference `ai-ofm-generate.sh`
3. Ensure wrapper has executable permissions

**Wrapper script content (already in skill templates):**
```bash
#!/bin/bash
cd "D:/Portable_Soft/hermes/projects/ai-ofm-tribute" && bash scripts/cron.sh
```

---

## Generated Assets

| Session | Style | Model | Output Dir | Preview |
|---------|-------|-------|------------|---------|
| 76 | fantasy | flux | `content/sessions/76/` | `preview.html` |
| 77 | realistic | flux | `content/sessions/77/` | `preview.html` |
| 78 | anime | flux | `content/sessions/78/` | `preview.html` |
| 79 | fantasy | turbo | `content/sessions/79/` | `preview.html` |
| 80 | fantasy | seedream | `content/sessions/80/` | `preview.html` (all placeholders) |
| 81 | fantasy | flux | `content/sessions/81/` | `preview.html` |

Each session contains:
- `{style}_NN_XX.jpg` — images (real or placeholder)
- `manifest.json` — full metadata (prompts, seeds, captions, model, success flags)
- `preview.html` — dark-theme gallery with real images

---

## Action Items

1. **DEPLOY CRON WRAPPER** — Copy `templates/ai-ofm-generate-wrapper.sh` to `scripts/ai-ofm-generate.sh` and update `jobs.json`
2. **Add retry logic to `generate.py`** — Retry on SSL/timeout errors with exponential backoff
3. **Remove seedream from model choices** — It's been broken for 4+ test sessions
4. **Consider model fallback** — If flux fails, auto-fallback to turbo
5. **Increase default delay** — Change `--delay` default from 2.0 to 5.0
6. **Style index sync** — After manual runs, manually update `.style_index` if needed