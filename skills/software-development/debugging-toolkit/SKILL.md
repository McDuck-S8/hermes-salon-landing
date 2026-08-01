---
name: debugging-toolkit
description: "Unified debugging toolkit for Hermes: systematic-debugging + python-debugpy + node-inspect-debugger + debugging-hermes-tui-commands. One skill to load, four tools at hand."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, troubleshooting, python, nodejs, hermes-tui, root-cause, systematic]
    related_skills: [systematic-debugging, python-debugpy, node-inspect-debugger, debugging-hermes-tui-commands, test-driven-development]
  skill_updated: "2026-07-24"
  created_by: "auto_patch_g007"
  component_skills:
    - systematic-debugging
    - python-debugpy
    - node-inspect-debugger
    - debugging-hermes-tui-commands
---

# Debugging Toolkit — Unified Interface

**One skill to load. Four debugging engines. Zero context switching.**

This meta-skill wraps the four core debugging skills into a single loadable unit with a unified command interface.

## Quick Start

```python
# Load once, get all four tools
from hermes_tools import skill_view
skill_view("software-development/debugging-toolkit")

# Now you have:
# - systematic-debugging (4-phase process)
# - python-debugpy (pdb + debugpy/DAP)
# - node-inspect-debugger (--inspect + CDP)
# - debugging-hermes-tui-commands (slash commands)
```

## Component Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| **systematic-debugging** | 4-phase root cause methodology | ALWAYS — Phase 1 before any fix |
| **python-debugpy** | pdb REPL + debugpy remote (DAP) | Python bugs, async, test failures |
| **node-inspect-debugger** | `--inspect` + Chrome DevTools Protocol | Node.js/TS bugs, TUI gateway, Ink UI |
| **debugging-hermes-tui-commands** | Slash command registry sync | Missing autocomplete, CLI≠TUI behavior |

## Unified Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: SYSTEMATIC INVESTIGATION (systematic-debugging)    │
│   • Read error fully → Reproduce → Trace data flow          │
│   • Check recent changes → Gather evidence                  │
│   • OUTPUT: Root cause hypothesis                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: TARGETED DEBUGGING (pick tool)                     │
│                                                             │
│   Python bug?       → python-debugpy                        │
│     python -m debugpy --listen 5678 -m pytest test_x.py     │
│     Attach VS Code / VS Codium → breakpoints → inspect     │
│                                                             │
│   Node/TS bug?      → node-inspect-debugger                 │
│     node --inspect=0.0.0.0:9229 app.js                      │
│     chrome://inspect OR cdp cli → breakpoints → inspect    │
│                                                             │
│   Hermes slash cmd? → debugging-hermes-tui-commands         │
│     Check COMMAND_REGISTRY ↔ TUI commands sync              │
│     Fix autocomplete / gateway dispatch                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: FIX & VERIFY                                       │
│   • Write regression test (test-driven-development)        │
│   • Single minimal fix at root cause                        │
│   • Run test → all pass → done                              │
└─────────────────────────────────────────────────────────────┘
```

## When to Use Each Tool

| Symptom | Primary Tool | Secondary |
|---------|--------------|-----------|
| "Test fails, don't know why" | systematic-debugging → python-debugpy | |
| "Async code hangs" | python-debugpy (DAP) | systematic-debugging |
| "TUI command missing from autocomplete" | debugging-hermes-tui-commands | |
| "CLI works, TUI doesn't" | debugging-hermes-tui-commands | systematic-debugging |
| "Node gateway crashes" | node-inspect-debugger | systematic-debugging |
| "Production error, no repro" | systematic-debugging (Phase 1 only) | python-debugpy / node-inspect |

## Quick Commands Reference

### Python (debugpy)
```bash
# Attach to running process
python -m debugpy --listen 5678 --pid <PID>

# Run test with debugger
python -m debugpy --listen 5678 -m pytest tests/test_x.py::test_name -v

# In code: breakpoint()
import debugpy; debugpy.listen(5678); debugpy.wait_for_client()
```

### Node (CDP)
```bash
# Start with inspector
node --inspect=0.0.0.0:9229 dist/app.js

# Chrome: chrome://inspect → Open dedicated DevTools
# Or CLI: npx cdp-cli@latest --port 9229

# Break on uncaught
node --inspect-brk=9229 dist/app.js
```

### Hermes TUI Commands
```bash
# Check registry
grep -n "commandname" hermes_cli/commands.py

# Check TUI definition
grep -n "commandname" ui-tui/src/app/slash/commands/*.ts

# Rebuild TUI
cd ui-tui && npm run build
```

## Anti-Patterns (from 998 debugging failures)

| Anti-Pattern | Countermeasure |
|--------------|----------------|
| Fix without Phase 1 | STOP → systematic-debugging Phase 1 |
| Multiple fixes at once | ONE change, test, repeat |
| Skip regression test | test-driven-development: RED first |
| Guess at async bugs | python-debugpy / node-inspect with breakpoints |
| "Works in CLI not TUI" | debugging-hermes-tui-commands registry sync |

## Integration with Knowledge Cube

After ANY debugging session, log to KC:

```python
from scripts.event_evolution import on_task_complete
on_task_complete(
    content="Debugged X: root cause was Y. Fix: Z. Tool used: python-debugpy",
    tags=["debugging", "python", "root_cause", "success"],
    source="agent"
)
```

## Verification Checklist

After using this toolkit:
- [ ] Phase 1 completed (root cause identified)
- [ ] Correct sub-tool selected and used
- [ ] Single minimal fix applied
- [ ] Regression test written and passing
- [ ] Full test suite green
- [ ] Knowledge Cube entry created

---

**Origin:** g-007 Unlock: debugging (100 failures in domain, 0 successes)
**Created:** 2026-07-24 via auto_patch_g007