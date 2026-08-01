---
name: max-brain-lessons
description: Analyze prior system iterations to extract reusable patterns. Use when reviewing prototype archives, evaluating abandoned projects, or building from prior work.
category: self-improvement
---

# Prototype Analysis — Extracting Patterns from Prior Iterations

## When to Use
- User says "проанализируй прототипы" / "почитай что было раньше"
- Reviewing abandoned projects for reusable ideas
- Building new system and want to learn from old attempts
- User asks "что из этого взять?"

## Method: Archive Extraction Protocol

### Step 1: Map the Landscape
```bash
# Find all candidate directories
find /d/ -maxdepth 2 -name "*.py" -path "*brain*" 2>/dev/null | head -20
# Find chat/conversation files (richest source of user intent)
find <dir> -name "*chat*" -o -name "*dialog*" -o -name "*session*" -o -name "*.jsonl"
# Find architecture files
find <dir> -name "AGENTS.md" -o -name "SOUL.md" -o -name "orchestrator*" -o -name "IDENTITY*"
```

### Step 2: Extract to Local Analysis Dir
Copy key files to `data/<project>-prototypes/{chats,identity,architecture}/`. Don't read remotely — bring data local first.

### Step 3: Read Strategically (Not Everything)
Priority order:
1. **Chat logs** — richest source of user intent and frustration signals
2. **Identity/SOUL files** — what the system was supposed to be
3. **Architecture files** — what was actually built
4. **Error/log files** — what broke and why

### Step 4: Extract ACTIONABLE Patterns
For each finding, ask:
- Is this a **class-level pattern** (applies beyond this project)?
- Is this a **specific finding** (only useful for this project)?
- Can this be turned into a **policy, skill, or tool**?

### Step 5: Integrate — Don't Just Report
- Create skill with `skill_manage(action='create')`
- Add policy with `patch` to `agent_policies.md`
- Record to Knowledge Cube with `hermes_hooks`
- Report: what was taken, what was rejected, why

## Core Lessons (from MAX-BRAIN 6 iterations)

### Simplicity > Complexity
```
v1: 10 agents, 40+ skills, MCP, ChromaDB → СЛОЖНО, не работает
v2: "только лучшее" → ПРОЩЕ, но всё ещё сложно
REBORN: direct_executor.py (171 lines) → ПРОСТО, работает
```
**Rule:** If a file > 500 lines, split it. If > 3 dependencies, simplify.

### Forced Memory > Voluntary Memory
```
BAD:  Агент → "должен прочитать историю" → Игнорирует → Амнезия
GOOD: Memory Daemon → Вшивает историю в промпт → Агент ОБЯЗАН помнить
```

### Executor, Not Advisor
> "ТЫ — ИСПОЛНИТЕЛЬ, А НЕ СОВЕТНИК"
- Не предлагать "сделать" — ДЕЛАТЬ
- Результат, а не объяснения

### What Typically Works
- CRITICAL-MEMORY.md чеклисты
- Session history запись
- Process manager
- Reflex/pattern databases
- History learner (pattern extraction from logs)

### What Typically Doesn't Work
- Autonomous loop 24/7 (hangs without human-in-loop)
- Voice/STT/TTS (integration complexity > value)
- Too many agents (coordination overhead > parallelism benefit)
- Inner council (good idea, never used in practice)
- Agent composer (creates agents that don't run)

## Pitfalls
- **Don't read everything** — chat logs and identity files first, code second
- **Don't copy architecture blindly** — each system has different constraints
- **Don't create skills from session-specific findings** — extract the class-level pattern
- **Don't report without integrating** — analysis without action is waste

## Reference Files
- `references/prototype-findings.md` — detailed findings from MAX-BRAIN analysis
