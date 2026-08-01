---
name: codebase-update-audit
description: "Safely review and apply updates to any git-based codebase with local modifications. Pre-flight audit, conflict assessment, stash/rebase, post-update verification."
---

# Codebase Update Audit

Safely update a git-based project when local changes exist. Never blindly `git pull`. Also covers the **pre-edit versioning** discipline that MUST fire before ANY file change.

## When to Use

- Before ANY file change via `patch` / `write_file` — first commit or stash current state (Hard Rule, SOUL.md §7)
- User asks to update a git repo (`git pull`, `hermes update`, `update X`)
- "N commits behind" warning detected
- Need to bring a fork/checkout up to date without losing local work

## Pre-Edit Versioning (Mandatory)

**Before ANY `patch` or `write_file` call**, even on a single file:

```bash
# Check if there are dirty files worth preserving
git status --short

# Stash or commit — pick ONE per session
git add path/to/file.py
git commit -m "pre-edit: <brief description of the change about to be made>"

# OR for quick work-in-progress:
git stash push -m "pre-edit-$(date +%Y%m%d): <what I'm about to change>"
```

**Rationale (from user correction 2026-07-19):** Не редактировать файлы без pre-flight коммита. Даже один файл. Даже строчку. Без коммита нет отката, а без отката ошибка становится необратимой. Пользователь больше не должен напоминать.

**Size doesn't matter:** One-line doc fix → commit. Single file patch → commit. The commit message can be one line. The only unacceptable state is editing without a safety net.

**Rollback when things go wrong:**

```bash
# Option A: reset to pre-edit state
git checkout -- path/to/broken_file.py

# Option B: if committed, revert the commit
git revert HEAD --no-edit

# Option C: if stashed
git stash drop                    # Discard the experimental changes
```

## Workflow

### Phase 1: Reconnaissance

```bash
# Current state
git log --oneline -1                           # Where am I?
git branch -vv                                  # What branch + tracking
git remote -v                                   # Which remote(s)
git status --short                              # Local changes (dirty files)
git stash list                                  # Any stashed work
```

### Phase 2: Assess Incoming Changes

```bash
# What's coming (count + titles)
git rev-list --count HEAD..origin/main          # How many commits
git log --oneline origin/main | head -30        # What's in them (gives summary)

# Check for files we also modified locally (conflict risk)
git diff --stat HEAD..origin/main -- $(git diff --name-only 2>/dev/null | tr '\\n' ' ')
```

**Key questions to answer before proceeding:**
- How many commits behind? (small = safe, large = need careful review)
- Any security fixes? (upgrade priority)
- Does upstream touch files we modified? (conflict risk)
- Breaking changes in release notes?

### Phase 2.5: Categorize Changes (for user report)

When reporting to user, group changes by category:

```bash
# Security
git log --oneline HEAD..origin/main --all-match --grep="CVE\|security\|vuln"
# Agent stability fixes
git log --oneline HEAD..origin/main --grep="fix" -- agent/ -- ':!apps/desktop' ':!ui-tui'
# Platform-specific (Windows, etc.)
git log --oneline HEAD..origin/main --grep="win\|windows\|pty"
```

**Categories to extract:**
- 🔴 **Security** — CVE patches, dependency bumps, hardening
- 🟡 **Stability** — crash fixes, memory leaks, hang prevention
- 🟢 **Features** — new capabilities relevant to user's setup
- 🟢 **Platform-specific** — fixes for user's OS
- ⚪ **Cosmetic** — docs, README, icons, unrelated to core

### Phase 3: Safe Update

```bash
# 1. Stash local changes (so pull is clean)
git stash push -m "pre-update-$(date +%Y%m%d): summary of local mods"

# 2. Fast-forward only (NO merge commits, NO rebase surprises)
git pull --ff-only origin main

# 3. Restore local changes
git stash pop

# 4. ONLY if pull fails (non-fast-forward): use rebase
#    git rebase origin/main
#    (resolve conflicts manually if any)
```

#### Handling stash pop conflicts (proactive resolution)

When `git stash pop` reports conflicts, the stash entry is **kept** (not dropped). This happens when upstream changed a file you also modified locally.

**Determine which version to keep:**
- `--theirs` (from stash perspective) = your stashed/local version
- `--ours` (from stash perspective) = the new upstream version

```bash
# Check what files collided
git status --short
# → UU path/to/file.md    (both modified)

# Resolve each known file:
# Keep YOUR version (for files you deliberately customized, like AGENTS.md):
git checkout --theirs path/to/file.md

# Keep UPSTREAM version (for accidental local changes or config you don't care about):
git checkout --ours path/to/file.md

# Mark each file as resolved
git add path/to/file.md

# Verify resolution
git status --short      # Should show M (modified), not UU

# Drop the kept stash (conflicted stash pop doesn't auto-drop)
git stash drop stash@{0}
```

**Do NOT blindly accept all --theirs or --ours** — pick file-by-file based on what the local modification was. Config overrides and custom docs → --theirs. Accidental edits and old WIP → --ours.

If the conflicted file requires merging BOTH sets of changes (e.g. a code file where both sides added different logic), resolve manually by editing the conflict markers in the file, then `git add`.

### Phase 3.5: Dependencies Check

After pulling, update project dependencies. On hermes-agent specifically, if `hermes.exe` breaks after git pull (ModuleNotFoundError for hermes_cli), see `references/hermes-update-troubleshooting.md` for the immediate workaround (direct Python import) and full fix.

```bash
# Python (uv)
uv sync                               # Fast, cached — preferred
# OR
pip install -e .                      # Fallback if uv not available

# Node (if project has package.json)
npm ci                                # Clean install from lockfile

# Check for known CVEs
pip-audit                             # If available
```

Skip if project has no dependency manager (config-only repo, docs site, etc.).

### Phase 4: Post-Update Verification

```bash
git log --oneline -1                    # New HEAD
git diff --stat HEAD@{1} HEAD           # What actually changed

# Verify imports still work
python -c "import <package>; print(<package>.__version__)"  # Core module

# Refresh version cache (if the repo has one, e.g. .update_check)
echo 'behind:0, ver:"<new-version>", rev:"<new-commit>"' > .update_check
```

Then verify system still works:
- Run a quick health check (e.g. `python -c "from package import module"`)
- Test the specific feature that was modified locally
- Check that local customizations are intact

### Phase 3.5: Recovering from Existing Merge Conflicts

**Use this when you find conflict markers or `UU` status in a working repo — before attempting any safe update.**

> See `references/gateway-cron-conflict-chain.md` for a detailed transcript of the gateway-crash-from-cron-conflict pattern, including exact tracebacks and recovery commands.

#### Detection

Common signs of an existing conflict:

```bash
# Unmerged paths in status
git status --short
# → UU path/to/file.py   (both sides modified, not resolved)

# Check for conflict markers in modified files
grep -rn '<<<<<<<\|=======\|>>>>>>>' --include='*.py' --include='*.js' --include='*.ts' --include='*.json' --include='*.yaml' --include='*.yml' --include='*.md' . 2>/dev/null | head -20

# Check stash for context
git stash list
```

#### Analyze the Conflict

1. **Read the markers** — Each file has:
   ```
   <<<<<<< <version-A>   # What's currently in your working tree
   =======
   >>>>>>> <version-B>   # What was being merged/popped
   ```
2. **Check HEAD** — `git log --oneline -1` tells you which commit you're on
3. **Check stash** — `git stash list` + `git stash show -p stash@{0}` reveals what stashed changes were
4. **Check both versions** of the conflicted file — often one is the upstream (repo) version and the other is stale local WIP

#### Decide Which Version to Keep

- **Upstream (HEAD)** — current repo version. Keep this when the stash/worktree is old WIP that doesn't need preserving.
- **Stashed/local** — only meaningful if the stashed changes do something the upstream version doesn't (new feature, bugfix in progress).
- **Merge both** — when both sides have meaningful changes in different parts of the file.

#### Resolve

```bash
# Option A: Keep upstream version (most common safe choice)
# Read the file, extract the version between <<<<<<< and =======
# Remove everything from <<<<<<< through >>>>>>>, keep only the version you want

# Option B: After manual resolution
git add path/to/file.py                    # Mark resolved

# Verify the conflict is resolved
git status --short                         # Should show M (modified), not UU
grep -rn '<<<<<<<\|=======\|>>>>>>>' path/to/file.py  # No markers
```

#### Verify the Fix

After resolving all conflicts:

```bash
# Test the specific command/module that was failing
python -c "from cron.jobs import list_jobs; print(list_jobs())"  # Example
hermes cron list                           # Or whatever command was broken

# Ensure imports work cleanly
python -c "import <package>"

# If the conflict was in cron/scheduler.py, verify gateway can start:
# (Do this AFTER killing stale processes)
hermes gateway run &
sleep 5 && kill %1                          # Quick smoke test
# → Should NOT crash with SyntaxError in cron-ticker thread
```

#### Pitfalls

- **Don't keep both versions whole** — when conflict markers wrap the entire file (not just a section), the file was a complete replacement. Pick one version, don't concatenate.
- **Don't skip testing** — after removing markers, the file may have subtle issues. Always test the feature that was broken.
- **Stash == WIP** — a stash with old commit base (`stash@{0}: WIP on main: <old-hash>`) is almost certainly stale. The upstream version is safer.
- **Check for cascading failures** — a broken file in a Python module tree prevents ALL imports from that module. Fix one conflict can unblock many downstream tools.
- **Cron module conflict → gateway crash** — `cron/scheduler.py` is imported by the gateway's `_start_cron_ticker` thread (`from cron.scheduler import tick`). A SyntaxError from a conflict marker in this file does NOT cause a Python-level crash with traceback to stdout/stderr that the gateway runner shows — instead it throws in a background thread and kills the gateway silently (exit code 1). **Diagnosis**: the gateway banner ("Hermes Gateway Starting...") appears, then the process exits seconds later with no visible error. The real traceback is in the process output (captured by background task), not in logs. **Fix**: resolve the conflict in `cron/scheduler.py`, then kill ALL stale gateway processes before restarting.
- **`hermes gateway stop` hangs on crashed gateway** — when the gateway is already dead (exited uncleanly), `hermes gateway stop` may hang trying to drain a non-existent process. Do not wait for it — use `kill -9` directly on the stale PID(s) found via `ps aux | grep hermes`, then start fresh. `hermes gateway stop` only works on a healthy gateway that responds to the shutdown signal.
- **Must kill stale processes after file fix** — Python caches compiled modules in memory once imported. If a gateway process loaded the broken `cron/scheduler.py` before you fixed it, simply restarting `hermes gateway run` spawns a new process that imports the FIXED file from disk correctly. **But if the old gateway process is still running and holds the Telegram token lock, the new gateway fails with "Telegram bot token already in use".** Always kill ALL `hermes` processes before restarting after a file-level fix to the cron or gateway code.

### Phase 5: Closing the Loop

If this repo is tracked with issues (beads, GitHub Issues, etc.):

```bash
# Close the update task
bd close <task-id> -r "Updated from X to Y. Changes: security N, fixes N, features N. Local mods preserved. Deps synced."

# Reasonable update task name
bd create "Post-update verification" P2  # If follow-up checks are needed
```

Mark the old version in the close reason so it's searchable later.

## Hermes Update (`hermes update`) vs Manual Git Pull

`hermes update` is NOT just `git pull`. It does:
1. Auto-stashes local changes (creates its own stash, separate from yours)
2. Fetches + pulls from origin
3. Updates Python deps via `uv sync` / `pip install`
4. Replaces `hermes.exe` (Windows — may be locked, needs `--force` or reboot)
5. Writes `.update_check` (version cache: `{"behind": N, "ver": "X.Y.Z"}`)

**Key difference from manual git pull:**
- `.update_check` is what reports "N commits behind" — it's a cached file, not live git state
- If no remote configured, `hermes update` still updates the pip package but can't git pull
- After `hermes update`, your stash is in a different stash entry than your original — check `git stash list` to find yours (it's labeled with your original message)

**Windows-specific:**
- `hermes update` fails if another `hermes.exe` is running → use `--force` to override
- `hermes.exe` replacement may be locked by the running process → scheduled for next reboot
- Verify update: `cat .update_check` → should show `"behind": 0`

## Submodule / Nested Repo Pattern (hermes-agent inside hermes)

Some projects have a nested git repo (submodule or just a separate checkout inside the parent). This was the case here: `D:/Portable_Soft/hermes/hermes-agent/` is a separate git repo tracking `NousResearch/hermes-agent`, while the parent `D:/Portable_Soft/hermes/` tracks the user's own fork.

**Update procedure for nested repos:**

```bash
# 1. Check BOTH repos independently
cd /parent/repo
git status && git remote -v
cd /parent/repo/nested-repo
git status && git remote -v

# 2. Update each one separately - they have different remotes
# Parent repo: user's fork / custom branch
# Nested repo: upstream (NousResearch/hermes-agent)
```

**In this session:** The parent repo (`hermes/`) was on branch `user/hermes-session-2026-06-09` with no remote configured (or wrong remote). The nested repo (`hermes/`) had `origin` = `NousResearch/hermes-agent` and was 597 commits behind.

**Correct approach used:**
1. `cd hermes-agent && git stash push -m "local-config-changes"` — stash local modifications
2. `git pull origin main` — fast-forward to upstream
3. `git stash pop` — restore local changes (conflict in `hermes_bootstrap.py`)
3. Resolve conflict by **keeping both changes**: upstream added `activate_durable_lazy_target()` call at module level; local added `boot()` function with autonomous action. Both were needed.
4. `git add hermes_bootstrap.py && git status` — verify clean
5. Test: `python hermes_bootstrap.py` → runs successfully
6. Verify parent repo's update check: `cd .. && python scripts/self_update_check.py` → "Behind: 0"

**Key insight:** When both sides add different code to the SAME file (not conflicting logic, just different functions), the resolution is to KEEP BOTH. Not "pick one" — merge them.

**Conflict resolution rule for additive changes:**
- If conflict markers wrap ENTIRE file → it's a full replacement, pick one version
- If conflict markers wrap SECTIONS → each side added something different, KEEP BOTH
- Example: upstream added init call, local added new function → both go in final file

**Key difference from manual git pull:**
- `.update_check` is what reports "N commits behind" — it's a cached file, not live git state
- If no remote configured, `hermes update` still updates the pip package but can't git pull
- After `hermes update`, your stash is in a different stash entry than your original — check `git stash list` to find yours (it's labeled with your original message)

**Windows-specific:**
- `hermes update` fails if another `hermes.exe` is running → use `--force` to override
- `hermes.exe` replacement may be locked by the running process → scheduled for next reboot
- Verify update: `cat .update_check` → should show `"behind": 0`

## Session: 2026-07-08 — 1490 Commits Behind Update

See `references/hermes-submodule-update-2026-07-08.md` for full transcript.

### Summary
- Nested repo `hermes-agent/` was **1490 commits behind** (v0.17.0 → v0.18.2+)
- Local changes in 3 files: `cron/scheduler.py` (Kill Switch + Exfiltration Guard), `hermes_bootstrap.py` (boot() function), `plugins/platforms/telegram/adapter.py` (proxy timeouts)
- **Clean auto-merge** — stash pop had zero conflicts because local changes were in different sections from upstream changes
- Post-update verification: nested boot works, parent update check shows "Behind: 0"

### New Pattern Reinforced
Large gaps (1490 commits, major version bump v0.17→v0.18) can still auto-merge cleanly when local modifications are well-isolated in different file sections. This validates the strategy of keeping local customizations focused and additive.

### Local Safety Patterns Preserved
Two production-grade safety patterns in `cron/scheduler.py` (NOT in upstream) were preserved across the update:
- **Kill Switch** (`HERMES_CRON_ENABLED`) — instant disable of all cron execution
- **Exfiltration Guard** — pre-execution scan of job prompt/script for secrets/PII

See `references/local-cron-safety-patterns-2026-07-08.md` for implementation details and preservation procedure.

### Custom scripts never in upstream

**Critical discovery:** If your repo has custom scripts that were NEVER part of upstream (e.g. `scripts/autonomous_agent.py`, `scripts/crystal.py`), a `git merge origin/main --allow-unrelated-histories` will mark them as "deleted" because upstream doesn't have them. This is NOT a real conflict — git just sees "we have it, they don't" and concludes it was removed upstream.

**Rule:** Before merging unrelated histories, check `git log --oneline origin/main -- path/to/your/file.py`. If no commits touch it, the file was never in upstream. Do NOT merge with unrelated histories in this case — use `hermes update` or manual stash/pull/pop instead.

**User directive (2026-06-21):** "Оставь как есть. Пакет обновлён, кастомные скрипты на месте. Не трогай git." — When custom scripts are entirely user-created and upstream has restructured, the correct move is: update the pip/uv package only, leave git alone. `hermes update` handles package updates via pip/uv regardless of git state.

**Transparency rule:** When you add a remote, remove a branch, or modify git state during an update, EXPLAIN what you did and why BEFORE the user sees the result. "это как, это что Remote: удалён (не был оригинальный)" — user was confused when I removed a remote I'd just added. State intent before acting: "Добавляю remote для fetch, потом удалю если merge не нужен."

## Pitfalls

- **Remote not configured**: No `origin` → add it first: `git remote add origin <url>`. If no write access, use `upstream` remote instead.
- **Detached HEAD**: Checkout a branch before pulling. `git checkout main` (or the tracked branch).
- **Local changes in files upstream also changed**: HIGH conflict risk. Report to user, don't auto-merge. Suggest `git stash` or manual conflict resolution.
- **Fast-forward rejected**: Local and upstream diverged. `--ff-only` fails intentionally — don't force-pull, use `git rebase origin/main` instead after confirming with user.
- **Pre-update snapshot**: `hermes update` auto-creates one. For manual git pulls, create a backup or tag first: `git tag pre-update-$(date +%Y%m%d)`
- **Large gap (100+ commits)**: Always inspect before applying. Check for breaking changes, DB migrations, config format changes.
- **Untracked files getting in the way**: `git stash --include-untracked` or clean up manually.
- **Conflicted stash pop keeps the stash**: When `git stash pop` produces conflicts, git keeps the stash entry — it does NOT drop it even on success (unlike a clean pop). You must manually `git stash drop stash@{0}` after resolving or the stale stash accumulates. Check with `git stash list` after any conflicted pop.

## User Preference (Alexander)

- MUST review changes before applying. "Не тупо ставить, а проверять."
- Report in Russian: what changed, what's risky, what's safe.
- Always prefer `--ff-only` over merge commits.
- If local modifications exist AND upstream changed same files → report to user, do NOT auto-resolve.
