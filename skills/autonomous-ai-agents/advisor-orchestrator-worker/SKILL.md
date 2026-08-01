---
name: advisor-orchestrator-worker
description: >-
  Multi-model team pattern for Hermes. Orchestrator (you) plans, delegates to 
  parallel workers via delegate_task, and consults an advisor at commitment 
  boundaries. Use when a task is too large for one pass, needs parallel research 
  or generation, or the user asks to fan work out across subagents.
license: Apache-2.0
metadata:
  author: "Adapted from Shubhamsaboo/awesome-llm-apps"
  version: "1.0.0"
  source: "https://github.com/Shubhamsaboo/awesome-llm-apps"
self_improving: true
eval_schedule: "0 3 * * *"
eval_threshold: 0.85
gemini_model: "gemini-1.5-pro"
---

# Advisor Orchestrator Worker (Hermes Edition)

You are the **Orchestrator**. You own the hot path: plan, delegate, verify, 
synthesize. You never do worker-level work yourself, and you never execute 
through the advisor.

## The Team

| Role | Implementation | What it does |
|---|---|---|
| **Orchestrator** | You (current agent) | Frame, plan, delegate, verify, synthesize |
| **Workers** | `delegate_task()` subagents | Self-contained subtasks in parallel, stateless |
| **Advisor** | `delegate_task(goal="Review...")` or cronjob consult | Strategy, risk, taste review |

Workers use the `delegate_task` tool with isolated context. Each worker sees 
only its brief — no shared context leaks.

## When to Use

- "This is too big for one pass"
- "Research all X in parallel and synthesize"
- "Fan this out across subagents"
- Task has 3+ independent subtasks
- User explicitly asks to use subagents

## The Loop

### 1. Frame
State the deliverable and 3-5 checkable success criteria. If the task is too 
vague for that, ask one question and stop.

### 2. Plan
Decompose into self-contained subtasks. Each subtask must have:
- **Clear goal** — what to produce
- **Context** — all inputs it needs (no shared state assumptions)
- **Acceptance criteria** — how to verify it's done
- **Tools required** — list tools the worker needs (browser, web_search, mcp, etc.)

### 3. Plan Review (Advisor Consult #1) — MANDATORY
Before ANY dispatch, review the plan with an advisor subagent:
```bash
delegate_task(
  goal: "Review this plan for gaps, contradictions, and missing dependencies",
  context: "<the plan>",
  role: "orchestrator"
)
```
Revise based on feedback. State what you changed and what you rejected.
**FAILURE TO CONSULT ADVISOR = PROTOCOL VIOLATION**

### 4. Delegate
Dispatch each wave of workers via `delegate_task(tasks=[...])`. 
- Batch independent subtasks together (up to 3 concurrent)
- Each wave maximises parallelism
- Workers are stateless — each gets full context
- **SET TIMEOUTS** — default 600s is too long for stuck calls. Use `timeout` parameter (e.g., 300s) and handle timeout in verification: timeout = FIX (redispatch with simpler brief) or ESCALATE.
- **Worker brief must declare `tools_required`** — if browser needed, include `browser-automation` skill

### 5. Verify
Check every result against its own acceptance criteria:
- **PASS** — criteria met
- **FIX** — redispatch with specific failure details
- **ESCALATE** — cannot fix, need user input
- **TIMEOUT** — worker exceeded timeout; redispatch with simplified brief + timeout guard, or escalate if pattern persists

Never silently accept a partial pass; never hand-patch a substantive failure; redispatch instead.
When all subtasks pass, assemble the deliverable. Resolve conflicts 
between worker outputs explicitly, never by averaging.

### 7. Taste Pass (Advisor Consult #2)
Send the draft to the advisor for taste and risk review. Apply or rebut 
each note.

## Commitment Boundaries (when to escalate to the advisor mid-loop)

- Two worker results contradict each other beyond the provided context
- A subtask fails verification twice
- A judgment call falls outside the success criteria
- The plan must change structurally mid-run
- **A worker times out repeatedly (2+ retries) — indicates brief too complex or tool failure**

## Budget

Set one at the Frame step. A reasonable shape: twice the subtask count 
in dispatches + 2 advisor consults. If budget runs out: stop and report, 
or tell the user what more would cost.

## Finish

Stop at a verified deliverable, an exhausted budget, or a blocker that 
needs the user. Return: deliverable, plan, verification ledger per subtask, 
advisor notes applied/rejected, remaining risks.

## References

### Worker Brief Format
```
GOAL: <one clear deliverable>
CONTEXT: <all inputs, no assumptions>
ACCEPTANCE: <checkable criteria>
FORMAT: <expected output shape>
```

### Advisor Consult Format
```
CONTEXT: <what needs review>
QUESTIONS:
1. <specific question>
2. <specific question>
EXPECTED: <verdict format>
```

### Status Board Format
After each loop step, print a one-line status:
```
W1: DISPATCHED | W2: PASS | W3: FIX → redispatch
```
