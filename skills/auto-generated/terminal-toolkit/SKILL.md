---
name: terminal-toolkit
description: "Unified terminal toolkit for Hermes: terminal-patterns + command-patterns + fix-command-skill + bugfix-patterns + log_tool_error-auto-skill. One skill to load, all terminal engines at hand."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [terminal, commands, patterns, bugfix, tool-errors, automation]
    related_skills: [terminal-patterns, command-patterns, fix-command-skill, bugfix-patterns, log_tool_error-auto-skill, log_unknown-auto-skill, log_network_connect-auto-skill, log_network_httpx-auto-skill]
  skill_updated: "2026-07-24"
  created_by: "auto_patch_g007"
  component_skills:
    - terminal-patterns
    - command-patterns
    - fix-command-skill
    - bugfix-patterns
    - log_tool_error-auto-skill
    - log_unknown-auto-skill
    - log_network_connect-auto-skill
    - log_network_httpx-auto-skill
---

# Terminal Toolkit — Unified Interface

**One skill to load. All terminal/command engines. Zero context switching.**

This meta-skill wraps all core terminal/command skills into a single loadable unit.

## Quick Start

```python
# Load once, get all engines
from hermes_tools import skill_view
skill_view("auto-generated/terminal-toolkit")

# Now you have:
# - terminal-patterns (43 KC entries on terminal ops)
# - command-patterns (auto-generated command patterns)
# - fix-command-skill (recurring 'command' issues guard)
# - bugfix-patterns (28 KC entries on bugfix)
# - log_tool_error-auto-skill (tool_error log pattern guard)
# - log_unknown-auto-skill (unknown log pattern guard)
# - log_network_connect-auto-skill (network_connect log pattern guard)
# - log_network_httpx-auto-skill (network_httpx log pattern guard)
```

## Component Skills Map

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| **terminal-patterns** | 43 KC entries on terminal operations | Background process management, CDP, Windows/MSYS quirks |
| **command-patterns** | Auto-generated command patterns | Recurring command issues, CLI patterns |
| **fix-command-skill** | Guard for recurring 'command' issues | terminal, skill_manage, patch, search_files errors |
| **bugfix-patterns** | 28 KC entries on bugfix patterns | Debugging methodology, root cause patterns |
| **log_tool_error-auto-skill** | Tool error log pattern guard | Terminal, search_files, skill_manage, patch errors |
| **log_unknown-auto-skill** | Unknown log pattern guard | Unclassified log errors |
| **log_network_connect-auto-skill** | Network connect log pattern guard | HTTP core/httpx connection errors |
| **log_network_httpx-auto-skill** | Network httpx log pattern guard | httpx-specific network errors |

## Unified Terminal Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. DIAGNOSE (terminal-patterns + bugfix-patterns)               │
│    • Background process exit codes (-15, 0, etc.)              │
│    • Windows/MSYS encoding issues (cp1251)                     │
│    • CDP connection patterns (port 9222, DevToolsActivePort)   │
│    • Background process cleanup (sleep + kill)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. GUARD (fix-command-skill + log_* auto-skills)                │
│    • terminal → read_file/search_files (NEVER cat/grep)        │
│    • skill_manage → skill_view first, patch mode, verify absorb│
│    • patch → write_file if 3+ patches, re-read before retry    │
│    • SQLite → WAL mode + busy_timeout                          │
│    • network errors → safe_mcp_call with retries               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. EXECUTE (with guards active)                                 │
│                                                                  │
│   Background process:                                           │
│   python -m debugpy --listen 5678 -m pytest test_x.py          │
│                                                                  │
│   CDP/Playwright:                                               │
│   python -m playwright install chromium                         │
│   npx playwright install-deps                                   │
│                                                                  │
│   Terminal cleanup:                                             │
│   taskkill /PID X /F  (via cmd.exe /c)                         │
│                                                                  │
│   File ops (ALWAYS use Hermes tools):                           │
│   read_file / write_file / patch / search_files                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. VERIFY & LOG                                                 │
│    • Check exit codes                                           │
│    • Log to KC with tags: terminal, commands, bugfix, success  │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Commands Reference

### Terminal Patterns (from 43 KC entries)
```bash
# Background process cleanup
taskkill /PID X /F  (ALWAYS via cmd.exe /c)

# CDP connection
chrome.exe --remote-debugging-port=9222 --user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data"

# Windows encoding fix
chcp 65001  # UTF-8 in cmd
# In Python: sys.stdout.reconfigure(encoding='utf-8')

# Background process management
start /b python script.py  # Non-blocking
```

### Command Guards (fix-command-skill)
```python
# BEFORE terminal → use read_file/search_files
# BEFORE skill_manage → skill_view() first, then patch mode
# BEFORE patch → if 3+ patches on same file → write_file
# BEFORE patch retry → re-read file first
# SQLite → PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;
```

### Network Error Guards
```python
# safe_mcp_call with retries
async def safe_mcp_call(server, tool, args, retries=2):
    for i in range(retries + 1):
        try:
            return await mcp_call(server, tool, args)
        except Exception as e:
            if i == retries: raise
            await asyncio.sleep(2 ** i)
            if "stale" in str(e).lower() or "detached" in str(e).lower():
                # Re-snapshot / refresh page ref
                pass
```

## Anti-Patterns (from 17 terminal entries + 28 bugfix entries)

| Anti-Pattern | Guard |
|--------------|-------|
| `cat file.txt` | **read_file** — line numbers, pagination, auto-extract |
| `grep -r "pattern"` | **search_files** — regex, context, filtering |
| `sed -i 's/x/y/g'` | **patch** — syntax checks, context uniqueness |
| `echo "x" > file` | **write_file** — creates dirs, syntax checks |
| `ls -la` | **search_files(target="files")** — sorted by mtime |
| `pip install` on full C: | Check C: space first; use curl + unzip to site-packages |
| `taskkill /PID` in MSYS | **cmd.exe /c "taskkill /PID X /F"** |
| Background process leaves shell corrupted | After any `&` or `nohup`, test `echo "ok"` |
| `pip list` hangs | C: drive full → clean Temp, Windows Update cache |

## Integration with Knowledge Cube

```python
from scripts.event_evolution import on_task_complete

on_task_complete(
    content="Terminal ops complete: used read_file/search_files/patch for all file ops. Background process cleaned up. Exit code 0.",
    tags=["terminal", "commands", "bugfix", "background_process", "success"],
    source="agent"
)
```

## Verification Checklist

After using this toolkit:
- [ ] All file ops via Hermes tools (read_file/write_file/patch/search_files)
- [ ] No terminal cat/grep/sed/ls/echo for file ops
- [ ] Background processes cleaned up (tested with `echo "ok"`)
- [ ] Network calls use safe_mcp_call with retries
- [ ] SQLite uses WAL + busy_timeout
- [ ] skill_manage preceded by skill_view
- [ ] patch retries re-read file first
- [ ] KC entry created with tags

---

**Origin:** g-007 Unlock: terminal (17 entries, 13 unknown, 4 success)
**Created:** 2026-07-24 via auto_patch_g007
**Source:** Knowledge Cube domain `terminal` + auto-generated skills