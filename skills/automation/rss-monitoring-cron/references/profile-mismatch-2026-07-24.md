# Profile Mismatch — Session 2026-07-24

## Critical Finding

**This skill documents a full RSS monitoring pipeline (rss_monitor.py, knowledge_pipeline.py, cron jobs, cache dirs) that exists in a DIFFERENT Hermes profile/instance — NOT in the current working directory (`D:\Portable_Soft\hermes`).**

## Current Instance: AI OFM Tribute Profile

| Path | Exists? | Contents |
|------|---------|----------|
| `D:\Portable_Soft\hermes\scripts\` | ✅ | `generate.py`, `preview.py`, `cron.sh` |
| `D:\Portable_Soft\hermes\scripts\rss_monitor.py` | ❌ | **MISSING** |
| `D:\Portable_Soft\hermes\scripts\knowledge_pipeline.py` | ❌ | **MISSING** |
| `D:\Portable_Soft\hermes\cron\jobs.json` | ❌ | **MISSING** |
| `D:\Portable_Soft\hermes\cache\rss_monitor\` | ❌ | **MISSING** |
| `D:\Portable_Soft\hermes\config.yaml` | ✅ | AI OFM Tribute config (channel, tribute, image_gen) |

**This instance is configured for AI image generation (Pollinations.ai), NOT for CPA/AI/tech RSS monitoring.**

## The Cron Job Failure

The cron execution that triggered this session tried to run `scripts/rss_monitor.py` but:
1. The script file doesn't exist in this profile
2. The cron job definitions (`jobs.json`) don't exist in this profile
3. Even if they did, the dependency/environment issues documented in `session-2026-07-24-disk-proxy-blockers.md` would prevent execution

## Root Cause: Wrong Profile Active

The user has multiple Hermes profiles. The RSS monitoring pipeline lives in a different profile (likely the default or a dedicated "arbitrage" profile). The cron scheduler ran in this profile (AI OFM Tribute) but the job definition references scripts that only exist in the other profile.

## Implication for Skill Users

**When using this skill:** Verify you're in the correct Hermes profile. The skill's documented paths, scripts, and cron jobs are profile-specific. Running cron jobs from the wrong profile will fail with misleading errors (missing imports, missing scripts) that obscure the real issue: profile mismatch.

## How to Switch Profiles

```bash
# List profiles
ls ~/.hermes/profiles/

# Switch profile for current session
export HERMES_PROFILE=arbitrage  # or whatever the RSS profile is named

# Or run hermes with explicit profile
hermes --profile arbitrage cron run
```

## Recommendation

Either:
1. **Switch to the correct profile** before running RSS monitoring cron jobs, OR
2. **Port the RSS monitoring scripts** to this profile if AI OFM Tribute should also do RSS monitoring

The skill documentation remains accurate for the profile where the pipeline actually exists — just not for this profile.