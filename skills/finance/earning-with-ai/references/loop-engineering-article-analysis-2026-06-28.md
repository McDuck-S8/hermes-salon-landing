# Loop Engineering Article Analysis (2026-06-28)

## Source
https://ai4dev.ru/posts/loop-engineering/

## Key Concepts

### Loop Engineering Definition
An emerging engineering pattern for designing agent workflows that goes beyond prompt engineering and context engineering. Focuses on designing **cycles** (not single prompts) that autonomously manage an agent's tasks, verification, and state.

> "You no longer just prompt the agent; you design the system that governs how, when, and why the model receives tasks."

### Inner vs Outer Cycle
- **Inner Cycle (Agent's Default Work):** Gathers context, plans a step, executes an action, checks results, fixes errors, continues.
- **Outer Cycle (Designed by Developer):** Defines triggers, scheduling, isolation, task decomposition, success criteria, limits, checks, and stop conditions.

### Six Key Components
1. **Automations:** Triggers the cycle (by schedule or event), performs initial task parsing.
2. **Git Worktrees:** Isolated working directories for parallel agent work, preventing file conflicts.
3. **Skills:** Practical task parsing logic to populate a `TODO.md` file.
4. **Plugins & Connectors (often MCP):** Link agents to real tools (CI/CD, Jira, GitHub, Slack, etc.).
5. **Subagents:** Separation of roles, enabling the **maker-checker** pattern (one agent creates, another verifies).
6. **Memory:** External state storage that persists between sessions.

### Maker-Checker Pattern
- **Why:** A model is too lenient with its own results; an independent checker reduces (but doesn't eliminate) the risk of flawed solutions.
- **Setup:** Configured via files (name, role, model, reasoning effort, instructions). More powerful models for audit/verification; faster, cheaper models for exploration and simple changes.

### Maturity Matrix for Adoption
| Level | System Action | Developer Role |
|-------|---------------|----------------|
| 1 | None | Prompts & checks everything manually |
| 2 | Parses tasks into TODO.md | Writes code; agent doesn't touch code |
| 3 | Makes changes in an isolated Git worktree | Reviews diff, runs tests, merges manually |
| 4 | Adds a checker validating Pull Requests | Makes final approval |
| 5 | Auto-merges after tests/linters pass | Monitors via logs, alerts, periodic review |

> **Warning:** Don't jump to Level 5 immediately. Expand autonomy only as you confirm where the agent is stable.

### Key Risks of Autonomy
1. **Token/Budget Burn:** Poorly limited cycles waste resources on useless iterations.
2. **False Security from Tests:** Tests can be written to match the (flawed) solution; they aren't 100% proof. **Human review remains mandatory for production code.**
3. **Architectural Degradation:** Agents may solve locally but violate global design, create duplication, or incorrect dependencies.
4. **Bottleneck Effect:** Agents generate code faster than humans can make engineering decisions. **Code review is essential.**
5. **Disabling Critical Thinking:** Don't assume full automation means the work is correct.

## What We Added to LOOPS.md
Based on this analysis, we added 6 components:

1. **Git Worktrees** — Isolation for Loop 3 parallel work
2. **Maker-Checker Pattern** — Separate verification process in Loop 2
3. **Maturity Matrix** — 5-level assessment (L0 Chaos → L4 Strategic)
4. **Budget/Token Limits** — Per-loop token budgets with auto-escalation
5. **Human Review Gates** — Blocking approval for high-risk operations
6. **Skills for Task Parsing** — NLP parsing of unstructured tasks into goal_queue format

## Revenue Principle
**Revenue = side effect of maturity, not a goal itself.**

Like a student who graduated university and entered life:
1. First develop capabilities
2. Then benchmark competitors
3. Then create competitive offering
4. THEN revenue comes naturally

**Anti-pattern:** "I have a landing page with prices" without benchmark or competitive advantage.
