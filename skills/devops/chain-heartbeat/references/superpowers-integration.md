# Superpowers Integration

## Methodology Layer

Superpowers provides **process skills** that govern HOW we work — they sit above domain skills and enforce discipline.

### Installed Process Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `using-superpowers` | Mandatory skill check before ANY response | Every session start, every task |
| `brainstorming` | Explore → design → spec → writing-plans | New features, creative work |
| `writing-plans` | Bite-sized TDD tasks, interfaces, constraints | Multi-step implementation |
| `subagent-driven-development` | Fresh subagent per task + review loop | Executing plans |

### Integration with Chain Heartbeat

**Chain Heartbeat** = System health monitoring (domain skill)
**Superpowers** = Work methodology (process skills)

They operate at different layers:

```
User Request
    ↓
using-superpowers (mandatory check)
    ↓
brainstorming (if new feature) OR systematic-debugging (if bug)
    ↓
writing-plans (implementation plan)
    ↓
subagent-driven-development (execute via subagents)
    ↓
    ├─ Task 1: domain skill (e.g., cpa-landing-generator)
    ├─ Task 2: domain skill (e.g., chain-heartbeat fix)
    └─ Task N: domain skill
    ↓
verification-before-completion (quality gates)
    ↓
Done
```

### Rule for Agents

> **Process skills FIRST, then domain skills.**

When starting ANY task:
1. Load `using-superpowers` (triggers skill check)
2. Load relevant process skill (`brainstorming`, `writing-plans`, `systematic-debugging`, `subagent-driven-development`)
3. THEN load domain skills (`chain-heartbeat`, `cpa-income-pipeline`, etc.)

### Red Flags (from using-superpowers)

| Thought | Action |
|---------|--------|
| "This is just a simple question" | → Questions are tasks. Check for skills. |
| "I need more context first" | → Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | → Skills tell you HOW to explore. Check first. |
| "This doesn't need a formal skill" | → If a skill exists, use it. |
| "The skill is overkill" | → Simple things become complex. Use it. |

See `skills/superpowers/using-superpowers/SKILL.md` for full rule and red flag table.