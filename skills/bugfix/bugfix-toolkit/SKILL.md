---
name: bugfix-toolkit
description: "Unified bugfix toolkit for Hermes: systematic-debugging + debugging-toolkit + recurrent-tool-error-fix + debugging-hermes-tui-commands. One skill to load, all bugfix engines at hand."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bugfix, debugging, systematic, tool-errors, terminal, skills, patch, tui]
    related_skills: [systematic-debugging, debugging-toolkit, recurrent-tool-error-fix, debugging-hermes-tui-commands, python-debugpy, node-inspect-debugger, test-driven-development]
  skill_updated: "2026-07-24"
  created_by: "auto_patch_g007"
  component_skills:
    - systematic-debugging
    - debugging-toolkit
    - recurrent-tool-error-fix
    - debugging-hermes-tui-commands
    - python-debugpy
    - node-inspect-debugger
    - test-driven-development
---

# Bugfix Toolkit — Unified Interface

**One skill to load. All bugfix engines. Zero context switching.**

This meta-skill wraps all core bugfix/debugging skills into a single loadable unit with a unified workflow interface.

## Quick Start

```python
# Load once, get all engines
from hermes_tools import skill_view
skill_view("bugfix/bugfix-toolkit")

# Now you have:
# - systematic-debugging (4-phase root cause methodology)
# - debugging-toolkit (python-debugpy + node-inspect-debugger + debugging-hermes-tui-commands)
# - recurrent-tool-error-fix (tool error patterns + guards)
# - debugging-hermes-tui-commands (slash command registry sync)
# - python-debugpy (pdb + debugpy/DAP)
# - node-inspect-debugger (Chrome DevTools Protocol for Node)
# - test-driven-development (RED-GREEN-REFACTOR)
```

## Component Skills Map

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| **systematic-debugging** | 4-phase root cause methodology | ANY bug — Phase 1 MANDATORY before any fix |
| **debugging-toolkit** | python-debugpy + node-inspect + tui-commands | Live debugging when systematic-debugging needs debugger |
| **recurrent-tool-error-fix** | Tool error patterns + guards | terminal/skill_manage/patch/SQLite errors |
| **debugging-hermes-tui-commands** | Slash command registry sync | Missing autocomplete, CLI≠TUI behavior |
| **python-debugpy** | pdb REPL + debugpy remote (DAP) | Python bugs, async, test failures |
| **node-inspect-debugger** | --inspect + CDP CLI | Node.js/TS bugs, TUI gateway, Ink UI |
| **test-driven-development** | RED-GREEN-REFACTOR enforcement | ALL bug fixes — regression test first |

## Unified Bugfix Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: SYSTEMATIC INVESTIGATION (systematic-debugging)        │
│   • Read error FULLY → Reproduce → Check recent changes         │
│   • Gather evidence (logs, state, data flow)                    │
│   • Trace data flow upstream to source                          │
│   • OUTPUT: Root cause hypothesis                               │
│   • RULE: NO FIXES BEFORE PHASE 1 COMPLETE                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: PATTERN ANALYSIS (recurrent-tool-error-fix)            │
│   • Check if this matches known tool error patterns             │
│   • terminal → read_file/search_files instead                   │
│   • skill_manage → skill_view first, patch mode, verify absorb  │
│   • patch → write_file if 3+, re-read before retry              │
│   • SQLite → WAL mode + busy_timeout                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: HYPOTHESIS + MINIMAL TEST (test-driven-development)    │
│   • Write FAILING test first (RED)                              │
│   • Single hypothesis, single variable change                   │
│   • If 3+ fixes fail → STOP, question architecture              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: LIVE DEBUG IF NEEDED (debugging-toolkit)               │
│                                                                  │
│   Python bug?     → python-debugpy                              │
│     python -m debugpy --listen 5678 -m pytest test_x.py::test  │
│     VS Code attach → breakpoints → inspect                     │
│                                                                  │
│   Node/TS bug?    → node-inspect-debugger                       │
│     node --inspect=9229 dist/app.js                             │
│     chrome://inspect OR npx cdp-cli                             │
│                                                                  │
│   Hermes slash cmd? → debugging-hermes-tui-commands             │
│     COMMAND_REGISTRY ↔ TUI commands sync                        │
│     Fix autocomplete / gateway dispatch                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 5: FIX + REGRESSION TEST (test-driven-development)        │
│   • Implement minimal fix at ROOT CAUSE                         │
│   • Run regression test → GREEN                                 │
│   • Run full suite → no regressions                             │
│   • Log to KC with root cause + fix                             │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Commands Reference

### Systematic Debugging (MANDATORY Phase 1)
```python
# Follow 4-phase methodology from systematic-debugging skill
# 1. Read error FULLY (stack trace, line numbers, codes)
# 2. Reproduce consistently (exact steps, every time?)
# 3. Check recent changes (git log, git diff)
# 4. Gather evidence (logs, state at each layer)
# 5. Trace data flow upstream to source
# ONLY THEN proceed to fix
```

### Recurrent Tool Error Fix
```bash
# Check improvement suggestions
python -c "
import json
with open('cache/improvement_suggestions.json') as f:
    s = json.load(f)
for sug in s.get('suggestions', []):
    if sug.get('issue_type','').startswith('tool_'):
        print(f\"{sug.get('occurrence_count')}x {sug['issue_type']}: {sug['title']}\")
"
```

### Python Debug (debugpy)
```bash
# Test with debugger
python -m debugpy --listen 5678 -m pytest tests/test_x.py::test_name -v

# In code
import debugpy; debugpy.listen(5678); debugpy.wait_for_client()
```

### Node Debug (CDP)
```bash
# Start with inspector
node --inspect=0.0.0.0:9229 dist/app.js

# Chrome: chrome://inspect
# CLI: npx cdp-cli@latest --port 9229
```

### Hermes TUI Commands
```bash
# Check registry
grep -n "commandname" hermes_cli/commands.py

# Check TUI
grep -n "commandname" ui-tui/src/app/slash/commands/*.ts

# Rebuild
cd ui-tui && npm run build
```

### TDD for Bug Fixes
```bash
# 1. Write failing test (RED)
pytest tests/test_regression.py::test_bug_X -v

# 2. Fix root cause (minimal change)

# 3. Test passes (GREEN)
pytest tests/test_regression.py::test_bug_X -v

# 4. Full suite
pytest tests/ -q
```

## Integration with Knowledge Cube

```python
from scripts.event_evolution import on_task_complete

on_task_complete(
    content="Bugfix complete: root cause was X (tool_error terminal). Fixed via read_file instead of cat. Regression test added.",
    tags=["bugfix", "systematic-debugging", "tool_error", "terminal", "regression_test", "success"],
    source="agent"
)
```

## Anti-Patterns (from 91 bugfix entries, 62 failures = 68% failure rate)

| Anti-Pattern | Guard |
|--------------|-------|
| Fix without Phase 1 | **systematic-debugging**: Phase 1 mandatory |
| Multiple fixes at once | **TDD**: single hypothesis, single change |
| 3+ fixes failed, try 4th | **Rule of 3**: STOP, question architecture |
| Debug without live debugger | **debugging-toolkit**: python-debugpy / node-inspect |
| Tool errors repeated | **recurrent-tool-error-fix**: guards for terminal/skill_manage/patch |
| Slash command out of sync | **debugging-hermes-tui-commands**: registry sync |

## Verification Checklist

After using this toolkit:
- [ ] Phase 1 completed (root cause identified)
- [ ] Tool error patterns checked (recurrent-tool-error-fix)
- [ ] Failing test written first (TDD)
- [ ] Live debugger used if needed (python-debugpy / node-inspect)
- [ ] Single minimal fix at root cause
- [ ] Regression test passes
- [ ] Full test suite green
- [ ] Hermes TUI commands synced if touched
- [ ] KC entry with root cause + fix

---

**Origin:** g-007 Unlock: bugfix (91 entries, 62 failures, 28 successes)
**Created:** 2026-07-24 via auto_patch_g007
**Source:** Knowledge Cube domain `bugfix` + all 7 component skills