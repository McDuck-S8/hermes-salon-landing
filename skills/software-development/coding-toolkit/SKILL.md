---
name: coding-toolkit
description: "Unified coding toolkit for Hermes: test-driven-development + writing-plans + plan + spike + systematic-debugging + debugging-toolkit + api-integration + code-review + task-driven-agent + subagent-driven-development + token-compression + tor-discipline. One skill to load, 12 engines at hand."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [coding, tdd, planning, debugging, api, review, agents, subagents, tokens, discipline]
    related_skills: [test-driven-development, writing-plans, plan, spike, systematic-debugging, debugging-toolkit, api-integration, code-review, task-driven-agent, subagent-driven-development, token-compression, tor-discipline]
  skill_updated: "2026-07-24"
  created_by: "auto_patch_g007"
  component_skills:
    - test-driven-development
    - writing-plans
    - plan
    - spike
    - systematic-debugging
    - debugging-toolkit
    - api-integration
    - code-review
    - task-driven-agent
    - subagent-driven-development
    - token-compression
    - tor-discipline
---

# Coding Toolkit — Unified Interface

**One skill to load. 12 coding engines. Zero context switching.**

This meta-skill wraps all core coding skills into a single loadable unit with a unified workflow interface.

## Quick Start

```python
# Load once, get all 12 tools
from hermes_tools import skill_view
skill_view("software-development/coding-toolkit")

# Now you have:
# - test-driven-development (RED-GREEN-REFACTOR)
# - writing-plans (implementation plans)
# - plan (actionable markdown plans)
# - spike (throwaway experiments)
# - systematic-debugging (4-phase root cause)
# - debugging-toolkit (python-debugpy + node-inspect + tui-commands)
# - api-integration (external API/SDK pattern)
# - code-review (pre-commit security + quality)
# - task-driven-agent (autonomous agent from natural language)
# - subagent-driven-development (delegate_task orchestration)
# - token-compression (50-80% tool output reduction)
# - tor-discipline (strict spec execution, no scope creep)
```

## Component Skills Map

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| **test-driven-development** | RED-GREEN-REFACTOR enforcement | ALWAYS — write failing test first |
| **writing-plans** | Bite-sized task plans with paths/code | Before any multi-step implementation |
| **plan** | Actionable markdown plans in `.hermes/plans/` | Feature work, PR prep |
| **spike** | Throwaway experiments, validate ideas | Before committing to implementation |
| **systematic-debugging** | 4-phase root cause methodology | ANY bug — Phase 1 before any fix |
| **debugging-toolkit** | python-debugpy + node-inspect + tui-commands | When systematic-debugging needs live debugger |
| **api-integration** | External API/SDK integration pattern | Any new external service |
| **code-review** | Pre-commit security + quality gates | Before every commit/PR |
| **task-driven-agent** | Build autonomous agent from natural language | When you need a self-running agent |
| **subagent-driven-development** | Orchestrate via delegate_task workers | Parallel implementation, review |
| **token-compression** | Compress LLM tool outputs 50-80% | Large JSON, logs, code outputs |
| **tor-discipline** | Strict spec execution, no scope creep | When executing TOR/specification |

## Unified Coding Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. SPECIFY (writing-plans / plan)                               │
│    • Break into bite-sized tasks with paths + code hints        │
│    • Save to .hermes/plans/<feature>.md                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. SPIKE (spike) — OPTIONAL                                     │
│    • Throwaway experiment to validate approach                 │
│    • Time-boxed (30-60 min), discard after learning            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. TEST FIRST (test-driven-development)                         │
│    • Write failing test (RED)                                   │
│    • Run → confirm failure                                      │
│    • This IS the spec                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. IMPLEMENT (tor-discipline + subagent-driven-development)     │
│    • Follow plan exactly — no scope creep                       │
│    • Delegate parallel workstreams via delegate_task            │
│    • One task at a time, verify before next                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. DEBUG IF NEEDED (systematic-debugging → debugging-toolkit)   │
│    • Phase 1: Root cause investigation (MANDATORY)             │
│    • Phase 2: Pattern analysis                                  │
│    • Phase 3: Hypothesis + minimal test                         │
│    • Phase 4: Fix root cause + regression test                  │
│    • Use python-debugpy / node-inspect for live debugging       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. REVIEW (code-review)                                         │
│    • Pre-commit security scan                                   │
│    • Quality gates                                              │
│    • Run full test suite                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. COMPRESS & LOG (token-compression + KC entry)               │
│    • Compress large outputs for next context                   │
│    • on_task_complete() to Knowledge Cube                      │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Commands Reference

### TDD Cycle
```bash
# Write failing test first
pytest tests/test_new_feature.py::test_x -v  # RED

# Implement minimal fix
# ... code ...

# Run test
pytest tests/test_new_feature.py::test_x -v  # GREEN

# Refactor
pytest tests/ -q  # All pass
```

### Plan + Execute
```bash
# Create plan
# Edit .hermes/plans/feature.md with tasks, paths, code hints

# Execute via subagents (parallel)
delegate_task(tasks=[
    {"goal": "Implement X", "context": "..."},
    {"goal": "Implement Y", "context": "..."}
])
```

### Debug (when tests fail)
```python
# 1. Systematic debugging Phase 1
# Read error fully → Reproduce → Trace data flow

# 2. Live debugger if needed
python -m debugpy --listen 5678 -m pytest tests/test_x.py::test_x -v
# Attach VS Code → breakpoints → inspect

# Or Node
node --inspect=9229 dist/app.js
# chrome://inspect
```

### API Integration
```python
# Follow api-integration pattern
# 1. Create client wrapper with retry/timeout
# 2. Add to provider registry
# 3. Implement fallback chain
# 4. Add health check endpoint
```

### Code Review (pre-commit)
```bash
# Security
bandit -r src/
# Quality
ruff check src/
# Types
mypy src/
# Tests
pytest -q
```

## Integration with Knowledge Cube

After ANY coding session:

```python
from scripts.event_evolution import on_task_complete

on_task_complete(
    content="Implemented X: used TDD cycle, debugged Y with python-debugpy, reviewed via code-review. All tests pass.",
    tags=["coding", "tdd", "debugging", "feature_x", "success"],
    source="agent"
)
```

## Anti-Patterns (from 170 coding entries, 62 failures)

| Anti-Pattern | Countermeasure |
|--------------|----------------|
| Fix without failing test | **tdd skill**: RED first, always |
| Debug without Phase 1 | **systematic-debugging**: root cause first |
| Scope creep during impl | **tor-discipline**: follow plan exactly |
| Large context from tool outputs | **token-compression**: compress before next turn |
| No review before commit | **code-review**: security + quality gates |
| Parallel work without orchestration | **subagent-driven-development**: structured delegation |
| API integration without fallback | **api-integration**: provider fallback chain |

## Verification Checklist

After using this toolkit:
- [ ] Plan created in `.hermes/plans/`
- [ ] Failing test written first (TDD)
- [ ] Implementation follows plan (tor-discipline)
- [ ] Any bugs debugged via systematic-debugging
- [ ] Code review passed (security + quality)
- [ ] Full test suite green
- [ ] KC entry created
- [ ] Large outputs compressed if needed

---

**Origin:** g-007 Unlock: coding (170 entries, 62 failures, 53 successes)
**Created:** 2026-07-24 via auto_patch_g007
**Source:** Knowledge Cube domain `coding` + all component skills