# Git Update with Local Modifications — Conflict Resolution Pattern

**Date:** 2026-06-29
**Scenario:** hermes-agent submodule was 597 commits behind origin/main with local modifications to `hermes_bootstrap.py` and `plugins/platforms/telegram/adapter.py`

## Problem

Standard `git pull` fails or creates merge commits when:
1. Local changes exist on files that upstream also modified
2. You need to preserve local config while getting upstream fixes

## Solution: Stash → Fast-Forward → Pop + Manual Resolution

### Step-by-Step (what we did)

```bash
# 1. Navigate to the submodule
cd /d/Portable_Soft/hermes/hermes-agent

# 2. Stash local changes with descriptive message
git stash push -m "local-config-changes" -- hermes_bootstrap.py plugins/platforms/telegram/adapter.py

# 3. Fast-forward update (no merge commits)
git pull --ff-only origin main

# 4. Restore stashed changes
git stash pop

# 5. Resolve conflicts manually
#    - Open conflicted file (hermes_bootstrap.py)
#    - Keep BOTH upstream improvements AND local additions
#    - Remove conflict markers (<<<<<<<, =======, >>>>>>>)
#    - git add hermes_bootstrap.py

# 6. Verify
python hermes_bootstrap.py
```

### Conflict Resolution Pattern (hermes_bootstrap.py case)

**Upstream added:** `activate_durable_lazy_target()` call at module level
**Local added:** `boot()` function with full bootstrap sequence + autonomous action

**Resolution:** Keep BOTH — upstream call at import time + local `boot()` function for programmatic use

```python
# After resolution - both preserved:
apply_windows_utf8_bootstrap()
activate_durable_lazy_target()  # upstream

def boot() -> list[str]:        # local
    """Full Hermes boot sequence..."""
    ...
```

### Key Principles

1. **Always stash before pull** — prevents merge commits and conflicts
2. **Use `--ff-only`** — fails fast if not fast-forwardable (forces you to handle properly)
3. **`git stash pop` not `apply`** — pop removes from stash list after successful apply
4. **Manual resolution > auto-merge** — when config files conflict, human judgment needed
5. **Verify immediately** — run the affected code to confirm it works

### Files That Commonly Conflict

| File | Local Changes | Upstream Changes |
|------|---------------|------------------|
| `hermes_bootstrap.py` | `boot()` function, autonomous action | `activate_durable_lazy_target()`, import fixes |
| `plugins/platforms/telegram/adapter.py` | Proxy timeouts, keepalive, SOCKS5 handling | Connection pool, proxy logic, HTTPX upgrades |
| `config.yaml.example` | Local provider configs | New provider defaults, schema changes |
| `pyproject.toml` | Local deps | Dependency updates |

### Post-Update Checklist

- [ ] `python hermes_bootstrap.py` — boot works
- [ ] `python -c "import agent.conversation_loop; print('OK')"` — core imports
- [ ] `hermes doctor` — dependencies
- [ ] `hermes config check` — config valid
- [ ] Update `.update_check` cache: `echo '{"behind": 0, "ver": "'$(git describe --tags --always)'"}' > ../.update_check`

## Automation Hook

Add to `scripts/self_update_check.py` post-update:
```python
# After successful pull, auto-run verification
subprocess.run(["python", "hermes_bootstrap.py"], cwd=HERMES_AGENT)
subprocess.run(["python", "-c", "import agent.conversation_loop"], cwd=HERMES_AGENT)
```