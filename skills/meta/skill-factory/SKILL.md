---
name: skill-factory
version: 1.1.0
author: Romanescu11 (via HermesHub)
repository: https://github.com/Romanescu11/hermes-skill-factory
license: MIT
category: meta
description: A meta-skill that silently watches your workflows and automatically generates reusable Hermes skills from them.
tags: [meta, automation, skills, learning, productivity, workflow-capture]
related_skills: [skill-evolution, skill-indexer, self-improvement-runtime]
---

# Skill Factory

A meta-skill for Hermes Agent that silently observes user workflows, detects repeatable patterns (e.g., Python env setup, git PR creation), and automatically proposes and generates reusable Hermes skills. Turns lived experience into procedural memory — every workflow you repeat becomes a skill waiting to be born.

## How It Works

Skill Factory operates in three stages:

```
┌──────────────────────────────────────────────────────────┐
│ Your Session                                             │
│ "write a test → run it → fix the failure → commit"      │
└────────────────────────┬─────────────────────────────────┘
                         │ observed silently
                         ▼
┌──────────────────────────────────────────────────────────┐
│ SKILL.md — The Meta-Skill (AI Brain)                     │
│ Tells Hermes HOW to observe, analyze, and propose skills │
└────────────────────────┬─────────────────────────────────┘
                         │ proposes + generates
                         ▼
┌──────────────────────────────────────────────────────────┐
│ Generated Skill Package                                  │
│ skills/<category>/<name>/SKILL.md                         │
└──────────────────────────────────────────────────────────┘
```

## Phase 1: Silent Observation

While active, maintain a log of session activity:
- **Repeated actions** — any command or approach used more than once
- **Multi-step workflows** — sequences of 3+ steps that accomplish a coherent goal
- **Tool combinations** — tools used together in a consistent pattern
- **Fixes and workarounds** — recurring debugging patterns

Ignore one-off tasks, trivial single-step actions, and workflows already handled by existing skills.

## Phase 2: Trigger Conditions

Propose skill creation when:
1. User explicitly requests "save this as a skill", "remember this workflow"
2. A workflow pattern repeats 2+ times in the session
3. Session is winding down (user says "done", "thanks")
4. User expresses frustration: "I always have to do this manually..."

## Phase 3: Proposal & Generation

When triggered, present a structured proposal:
1. Detect the workflow pattern from session history
2. Analyze what makes it reusable
3. Generate a complete SKILL.md with:
   - Trigger conditions
   - Step-by-step procedure
   - Concrete examples from the session
   - Pitfalls discovered
   - Verification steps

## Usage Pattern

```python
# During any session, watch for:
# 1. Repeated task patterns
# 2. Multi-step workflows done manually
# 3. User saying "remember this" or "save this"
#
# When detected, create a skill using skill_manage(action='create')

# Example pattern detection:
patterns = {
    'workflow': 'python_script_test_debug',
    'steps': ['write script', 'run with pytest', 'debug failure', 'fix'],
    'frequency': 2  # appeared twice
}
```

## What Makes a Good Skill to Generate

- **Reusable** — the workflow will be needed again
- **Specific** — solves one problem well
- **Verifiable** — has clear pass/fail criteria
- **Self-contained** — doesn't depend on external setup

## Requirements

- Hermes Agent v2026.3+
- Python 3.10+
- No external dependencies

## Pitfalls

- Don't generate skills for one-off tasks
- Don't capture trivial single-step actions
- Avoid overly broad workflows that don't generalize
- Keep generated skills under 600 lines
