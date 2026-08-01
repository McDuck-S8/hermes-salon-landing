# Hermes Submodule Update — 2026-06-29

## Context
- Parent repo: `D:/Portable_Soft/hermes/` — branch `user/hermes-session-2026-06-09`, no remote configured
- Nested repo: `D:/Portable_Soft/hermes/hermes-agent/` — branch `main`, `origin` = `https://github.com/NousResearch/hermes-agent.git`, **597 commits behind**

## Local Changes in Nested Repo (stashed before update)
1. `hermes_bootstrap.py` — added `boot()` function for full system boot + autonomous first action
2. `plugins/platforms/telegram/adapter.py` — adjusted retry/timeout configs for v2rayN/SOCKS5 proxy stability

## Upstream Changes (597 commits, key highlights)
- Mixture of Agents (`agent/moa_loop.py`)
- Pet generation system (`agent/pet/generate/`)
- Verification evidence/stop (`agent/verification_*.py`)
- Desktop app: git worktrees, projects sidebar, code editor, embeds
- Gateway: cron cleanup, scale-to-zero, drain control
- Telegram platform: new `telegram_ids.py`, send path infographic
- Tests: extensive new test coverage

## Resolution Steps
```bash
cd /d/Portable_Soft/hermes/hermes-agent
git stash push -m "local-config-changes" -- hermes_bootstrap.py plugins/platforms/telegram/adapter.py
git pull origin main
git stash pop
# → Conflict in hermes_bootstrap.py (both modified)
# Resolution: KEPT BOTH changes (upstream added activate_durable_lazy_target() call; local added boot() function)
# Edit file to include both, then:
git add hermes_bootstrap.py
git status  # Clean
```

## Conflict Details: hermes_bootstrap.py
**Upstream version (HEAD):** Added `activate_durable_lazy_target()` call at module level after `apply_windows_utf8_bootstrap()`

**Stashed/local version:** Added `boot()` function + `if __name__ == "__main__"` block for autonomous boot sequence

**Resolution:** Both changes are additive and non-conflicting in logic. Merged file includes:
1. `apply_windows_utf8_bootstrap()` call
2. `activate_durable_lazy_target()` call  
3. `boot()` function definition
4. `if __name__ == "__main__":` block calling `boot()`

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

## Key Lessons
1. **Nested repos need separate update** — each has its own remote and history
2. **Additive conflicts = keep both** — when both sides add different functions to same file, merge both
3. **Test at both levels** — nested repo boot works AND parent repo's update check passes
4. **Stash with specific files** — `git stash push -- file1 file2` to avoid stashing everything