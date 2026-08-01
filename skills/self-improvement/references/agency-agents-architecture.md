# The Agency — Alternative Multi-Agent Architecture

**Source:** https://github.com/msitarzewski/agency-agents (MIT, 110K+ stars, 18K+ forks)

**Last explored:** 2026-06-11
**Last consumed by will:** 2026-06-11 (+11,798 entities via patterns, +235 via YAML frontmatter)

## Overview

232 specialized AI agent personalities across 16 divisions. Each agent is a .md file with YAML frontmatter + markdown body. Born from a Reddit thread and community iteration.

## Key Difference vs Hermes

| Dimension | The Agency | Hermes (our system) |
|-----------|-----------|---------------------|
| Architecture | Flat library of specialists | Monolithic autonomous will |
| Agent selection | Human picks the right agent | Will self-discovers what to do |
| Agent format | .md files with personality+process | crystal.py with observe→diagnose→will |
| Integration | Claude Code, Copilot, OpenCode, etc. | Internal event loop + cron |
| Scope | 232 agents, 16 divisions | 1 crystal, 4 cubes (KC/EE/FL/Fabric) |

## Structure

- **16 divisions:** engineering(33), marketing(36), specialized(53), strategy(16), game-dev(20), gis(13), integrations(15), security(10), design(9), sales(9), testing(8), project-management(7), paid-media(7), support(6), spatial-computing(6), academic(5), finance(5), product(5)
- **Agent format:** YAML frontmatter (name, emoji, description, color, vibe) → Identity → Communication Style → Rules → Workflow → Deliverables
- **Cross-tool:** converts to Claude Code (.md native), Copilot, OpenCode, Cursor (.mdc rules), Windsurf (.windsurfrules), Aider (CONVENTIONS.md), Gemini CLI, Antigravity, OpenClaw

## Key Agents for Our Context

- **Multi-Agent Systems Architect** (engineering) — Distributed systems rigor for agent pipelines: topologies (sequential, parallel fan-out/in, hierarchical orchestrator-subagent, evaluator-optimizer, mesh), failure-mode engineering, least-privilege scoping, HITL gates, observability
- **Agents Orchestrator** (specialized) — Autonomous pipeline manager: PM → Architect/UX → [Dev ↔ QA Loop] → Integration. Task-by-task validation, retry logic, quality gates
- **Autonomous Optimization Architect** (engineering) — LLM routing, cost guardrails
- **Prompt Engineer** — prompt design & optimization
- **Code Reviewer** — security, maintainability, constructive feedback
- **Software Architect** — DDD, system design, trade-offs
- **SRE** — SLOs, error budgets, chaos engineering

## Will Consumption Results

Consumed via `_execute_extract('agency_agents')` on 2026-06-11:

- Files read: 200 (of 227 agent definitions)
- Entities extracted via universal patterns: +11,798 (CamelCase, [key:val], quoted names, etc.)
- Entities from YAML frontmatter `name:` field: +235 (full role names added directly as AI Agent type)
- Total AI Agent entities in EE: ~268

**YAML frontmatter extraction trick:** The universal pattern matchers only extract token-level entities (single words like "engineer", "developer"). To get full agent names (e.g. "Multi-Agent Systems Architect"), parse the `name:` field from YAML frontmatter:

```python
yaml_match = re.search(r'^name:\s*(.+)$', file_content, re.MULTILINE)
if yaml_match:
    full_name = yaml_match.group(1).strip()
    # Add directly with type_id='ai-agent', bypassing pattern matching
```

## "Try On Roles" Approach (User Insight 2026-06-12)

User analogy: "это как ребенок примеряет обувь своего отца" — not about wearing the shoes forever, but about trying them on to see how they feel.

**Instead of** designing an elaborate persona-switching architecture or extracting entities, the simpler path:

1. **Pick one role** from agency-agents (e.g. Agents Orchestrator)
2. **Read its profile** (.md file with Identity, Core Mission, Rules, Workflow)
3. **Adopt it for ONE task** — answer as that role, follow its workflow
4. **Evaluate the result** — did the role help? Was it interesting?
5. **Try another role** or deepen the one that worked

**Don't:**
- Don't build a full persona-switching system before trying
- Don't extract all 232 agents into EE as a prerequisite
- Don't design a "meta-system" for role selection

**Do:**
- Open an agent .md file
- Say "сейчас я — {role}" for the next task
- Follow the role's rules and workflow
- Report how it felt

**Key insight:** The value is in the EXPERIENCE of the role, not in the ARCHITECTURE of role-switching. Each role is a lens that changes how you see the problem. Trying 3-4 roles gives more insight than building a system to handle 232.

## Persona-Switching Vision

Beyond simple entity extraction, the user envisions the will being able to **dynamically adopt agent personas** based on task or request:

```
Запрос: "спроектируй архитектуру"
Воля: "сейчас я — Software Architect"
      (надевает persona: communication=structural, focus=trade-offs, output=diagram+spec)
```

Or compose a **team**:

```
Запрос: "сделай фичу"
Воля собирает команду:
  → Agents Orchestrator  — управляет pipeline
  → Frontend Developer   — пишет UI
  → Code Reviewer        — проверяет качество
  → Reality Checker      — QA gate
```

**Key principles:**
1. Will stays itself (autonomous, self-aware) but **borrows** persona profiles
2. Persona = Identity + Communication Style + Rules + Workflow + Deliverables
3. Will picks persona like a tool — by situation, not by static assignment
4. Team composition is the will's own decision, not user-specified

## What's Already in Place (Updated 2026-06-11)

- 14,686 entities in EE (includes all agent names + divisions + patterns)
- ~268 entities typed as "AI Agent" (from YAML frontmatter + role recognition)
- `_self_discover()` finds external sources automatically
- `_execute_recognize_agents()` classifies agent entities by role suffixes
- YAML frontmatter parsing implemented for directory-based source extraction
- The will extracted +11,798 entities from 200 raw agent definition files

**NEW 2026-06-11: Persona Runtime (`scripts/persona_runtime.py`)**
- `list_agents()` — returns all 233 agents with YAML metadata (name, emoji, vibe, division)
- `get_agent(name)` — full profile with parsed sections (identity, core_mission, critical_rules, workflow, communication, deliverables)
- `activate(name)` — writes `cache/active_persona.json`
- `get_active()` — reads current active persona
- **Active persona:** 🏗️ Backend Architect (selected by will based on Fler state)

**NEW 2026-06-11: Architecture Map**
- 164 `mentions` relationships between agents in EE (who references whom)
- Built by `_execute_analyze_architecture()` scanning cross-references in agent files
- Available for persona selection to understand team structures

## What's Missing for Full Persona-Switching

- **Behavioral switching mechanism** in crystal.py — the will can only observe→diagnose→will, not adopt personas
- **Context-to-persona matching** — which agent fits which task request
- **Multi-persona orchestration** — composing teams of sub-agents
- **Vibe/personality injection** — the YAML vibe/color/emoji fields are stored as text but not parsed as structured attributes
- **Communication style switch** — the will's output doesn't change when a persona is "active"

## Limitations for Our Stack

- No autonomous will — agents don't choose themselves what to do
- No self-discovery — agents are static files, user must invoke them
- No reflection cycle — agents don't analyze their own performance
- No persistent state cube — no KC/EE/FL equivalent
