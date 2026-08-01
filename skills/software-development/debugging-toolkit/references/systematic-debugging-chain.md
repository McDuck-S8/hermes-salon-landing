# Systematic Debugging Chain Execution

**Source:** Session 2026-07-24, debugging-toolkit creation
**Status:** PROVEN PATTERN — applied to 62 coding failures, 100 debugging failures

---

## Pattern: Debugging Toolkit as Meta-Skill

When a domain has high failure count (62+ coding failures, 100 debugging failures), the solution is NOT more individual debugging skills — it's a **unified meta-skill** that wraps all debugging engines with a single workflow.

---

## Execution Flow (Applied This Session)

```
1. Domain Analysis (KC query)
   → debugging: 106 entries, 100 failures
   → coding: 170 entries, 62 failures
   
2. Component Skills Audit
   → systematic-debugging (4-phase methodology)
   → python-debugpy (pdb + debugpy/DAP)
   → node-inspect-debugger (CDP)
   → debugging-hermes-tui-commands (slash sync)
   
3. Meta-Skill Creation
   → debugging-toolkit (unified interface)
   → Component skills patched with stale_metadata
   
4. Workflow Integration
   → coding-toolkit includes debugging-toolkit
   → devops-toolkit includes systematic-debugging
   → All new code MUST pass systematic-debugging Phase 1 first
```

---

## The 4-Phase Protocol (Enforced)

**Phase 1: Root Cause Investigation (MANDATORY before any fix)**
- Read error fully → Reproduce → Trace data flow → Check recent changes
- Output: Root cause hypothesis

**Phase 2: Pattern Analysis**
- Find working examples → Compare against broken → Identify differences
- Output: What's different

**Phase 3: Hypothesis & Minimal Test**
- Single hypothesis → Minimal change → Verify before continuing
- Output: Confirmed or new hypothesis

**Phase 4: Implementation**
- Regression test (RED) → Fix root cause (GREEN) → Full suite passes
- Rule of Three: If 3+ fixes fail → question architecture

---

## Anti-Patterns from 100 Debugging Failures

| Anti-Pattern | Countermeasure in Toolkit |
|--------------|---------------------------|
| Fix without Phase 1 | **STOP** rule in Phase 1 checklist |
| Multiple fixes at once | **One variable at a time** in Phase 3 |
| Skip regression test | **Test-first** in Phase 4 (TDD skill) |
| Guess at async bugs | **python-debugpy / node-inspect** live breakpoints |
| "Works in CLI not TUI" | **debugging-hermes-tui-commands** registry sync |

---

## Integration Points

| Skill | Integration |
|-------|-------------|
| `test-driven-development` | Phase 4 requires RED test first |
| `coding-toolkit` | Includes debugging-toolkit as component |
| `devops-toolkit` | Layer 3 autonomous execution uses Phase 1 |
| `subagent-driven-development` | Delegate investigation to subagent with toolkit |

---

## Verification (Applied This Session)

- [x] Meta-skill created: `debugging-toolkit`
- [x] All 4 components patched with stale_metadata (v1.1.0+)
- [x] `systematic-debugging` updated v1.2.0→1.3.0
- [x] Integrated into `coding-toolkit` component list
- [x] KC entry logged with tags: debugging, toolkit, g007

---

**Last Updated:** 2026-07-24
**Source:** Single-session chain execution with direct principal corrections