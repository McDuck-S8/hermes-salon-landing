# Hermes Submodule Update — 2026-07-08

## Context
- Parent repo: `D:/Portable_Soft/hermes/` — branch `user/hermes-session-2026-06-09`, no remote configured
- Nested repo: `D:/Portable_Soft/hermes/hermes-agent/` — branch `main`, `origin` = `https://github.com/NousResearch/hermes-agent.git`, **1490 commits behind** (v0.17.0 → v0.18.2+)

## Local Changes in Nested Repo (stashed before update)
1. `cron/scheduler.py` — Kill Switch (`HERMES_CRON_ENABLED`) + Exfiltration Guard check on job content
2. `hermes_bootstrap.py` — New `boot()` function for full system boot + autonomous first action
3. `plugins/platforms/telegram/adapter.py` — Network retry/timeout tuning for v2rayN/SOCKS5 proxy stability

## Upstream Changes (1490 commits, key highlights from v0.18.1 + v0.18.2)
- Gateway: generic OIDC client-credentials relay (NAS-free) (#60730)
- TUI: derive gateway-owned sources from Platform enum, not hardcoded list
- Cron: drain in-flight jobs before shutdown tool kill; stop interrupted jobs from delivering pre-kill output
- Telegram: WhatsApp dashboard pairing flow (new)
- Tools: YAML write gate syntax-only (allow multi-doc/tagged YAML)
- Install: warn pip/Homebrew installs are unsupported
- WhatsApp: unpin Baileys, use published 7.0.0-rc13
- GATEWAY_MULTIPLEX_PROFILES env override
- Memory provider validation before filesystem lookup

## Resolution Steps
```bash
cd /d/Portable_Soft/hermes/hermes-agent
git stash push -m "local-config-changes" -- cron/scheduler.py hermes_bootstrap.py plugins/platforms/telegram/adapter.py
git pull origin main
# Fast-forward: 1490 commits, 1634 files updated
git stash pop
# → Auto-merged cleanly (no conflicts!)
git status  # Clean - all 3 local changes restored
```

## Key Differences from 2026-06-29 Update
| Aspect | 2026-06-29 | 2026-07-08 |
|--------|-----------|-----------|
| Commits behind | 597 | **1490** |
| Major version bump | v0.17.x | v0.17.0 → **v0.18.2** |
| Local files modified | 2 | **3** |
| Stash pop conflicts | 1 (hermes_bootstrap.py) | **0** (clean auto-merge) |
| Resolution needed | Manual merge (keep both) | **None** |

## Why Clean Auto-Merge This Time?
1. Upstream didn't touch `cron/scheduler.py` in the conflicting areas (Kill Switch + Exfil Guard added in different sections)
2. Upstream added `activate_durable_lazy_target()` at module level in `hermes_bootstrap.py`; local `boot()` function was at end of file — no line overlap
3. Upstream Telegram changes were in different areas than our proxy timeout tuning

## Post-Update Verification
```bash
# Nested repo
python hermes_bootstrap.py
# → utf8_bootstrap: already active
# → path_harden: OK
# → env_load: 11 vars loaded from .env
# → tool_catalog: 100 scripts in scripts/
# → autonomous_action: EXECUTED goal corrective-wf-daily-maintenance-1 — success

# Parent repo update check
cd ..
python scripts/self_update_check.py
# → Behind: 0 commits | Ahead: 0
# → ✅ Up to date!
```

## Key Lessons Reinforced
1. **Nested repos need separate update** — each has its own remote and history
2. **Additive conflicts = keep both** — when both sides add different functions to same file, merge both
3. **Test at both levels** — nested repo boot works AND parent repo's update check passes
4. **Stash with specific files** — `git stash push -- file1 file2 file3` to avoid stashing everything
5. **Large gap (1490 commits) can still auto-merge** — if local changes are in different sections from upstream changes, git handles it
6. **Major version bumps (v0.17→v0.18) don't guarantee breaking local changes** — the Hermes agent architecture is stable enough that well-isolated local mods survive

## New Pattern: Exfiltration Guard + Kill Switch in cron/scheduler.py
This session added two production-grade safety patterns to the cron scheduler that are NOT in upstream:
- **Kill Switch** (`HERMES_CRON_ENABLED=false`): Instant disable of all cron execution without code changes
- **Exfiltration Guard**: Pre-execution scan of job prompt/script for secrets/API keys/PII

These are local customizations that should be documented and preserved. They represent a class of "safety layer" patterns that could be proposed upstream but are currently local-only.

## Conflict Resolution Rule (Reaffirmed)
- If conflict markers wrap ENTIRE file → full replacement, pick one version
- If conflict markers wrap SECTIONS → each side added something different, KEEP BOTH
- Example: upstream added init call at top, local added new function at bottom → both go in final file