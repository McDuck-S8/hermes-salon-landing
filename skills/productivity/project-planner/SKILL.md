---
name: project-planner
version: 1.1.0
author: hermeshub
license: MIT
description: Structured project planning — task decomposition, timelines, dependencies, milestone tracking.
tags: [project-management, planning, tasks, timeline, roadmap]
---

# Project Planner

Structured project planning with task decomposition and tracking.

## When to Use

- User describes a project and needs a plan
- User wants to break down work into tasks
- User needs timeline estimates
- User wants to track progress against milestones

## Procedure

1. **Gather** project scope and constraints
2. **Decompose** into milestones (major deliverables)
3. **Break** milestones into tasks (actionable items)
4. **Identify** dependencies between tasks
5. **Estimate** effort for each task
6. **Generate** timeline with critical path
7. **Save** plan as markdown

## Plan Format

```markdown
# Project: [Name]
**Goal:** [One sentence]
**Timeline:** [Start] → [End]

## Milestones

### M1: [Milestone Name] (Due: [date])
- [ ] Task 1 (Est: 2h, Depends: none)
- [ ] Task 2 (Est: 4h, Depends: Task 1)

### M2: [Milestone Name] (Due: [date])
- [ ] Task 3 (Est: 8h, Depends: M1)
```

## Estimation Guidelines

| Size | Duration | Example |
|------|----------|---------|
| Small | 1-2 hours | Add a form field |
| Medium | 4-8 hours | New API endpoint |
| Large | 2-3 days | New feature module |

Add 20% buffer for unknowns. Multiply initial guess by 1.5 for realistic estimates.

## Dependency Types

- **Blocking** — B can't start until A finishes
- **Resource** — A and B share the same person
- **Knowledge** — B needs information only available after A

## Verification

- Every task has an owner and estimate
- Dependencies form a DAG (no cycles)
- Critical path is identified
- Buffer exists for high-risk items
- Plan has review points

## Pitfalls

- Over-optimistic estimates — multiply initial guess by 1.5
- Ignoring dependencies creates phantom parallelism
- Plans without review points drift silently
- Too granular = overhead; too coarse = no visibility
- Don't forget setup time (env, config, context switching)

---

## Project Schema / Map

When a set of projects needs organization, create a **project schema** — a visual map of all projects with themes, priorities, health metrics, and connections.

### When to Create a Project Schema

- Multiple projects exist but lack a parent view
- User says "projects folder needs schemas/themes"
- Priorities between projects are unclear
- You need to decide which project to work on next

### Schema Layers (General → Specific)

Following the priority chain **earnings > projects > specific**:

1. **Earnings pipeline** — which projects make money now? Which could?
2. **Themes** — group projects by domain (booking, tourism, content, infra)
3. **Per-project detail** — status, stack, readiness, next action
4. **Connections** — how projects relate (reuse, feed, depend)
5. **Health metrics** — count of running code, revenue status, document readiness

### Deliverables

| Artifact | Format | Purpose |
|----------|--------|---------|
| `PROJECT_MAP.md` | Markdown | Human-readable schema with tables and relationships |
| `PROJECT_MAP.mm.md` | Heading-only MD | Source for markmap.js interactive mindmap |
| `mindmap.html` | HTML+JS | Interactive viewer (see diagram-maker skill for markmap procedure) |
| `business-plan.md` | Markdown | Business model, pricing, financials, action plan |
| `AGENTS.md` update | Markdown | DOX: child index with statuses, links to schema docs |

### Schema Format (PROJECT_MAP.md sections)

1. **ASCII/visual hierarchy** — `earnings → projects → salons` tree
2. **Themes table** — theme name, projects, status, money potential
3. **What to fill** — per-theme task list ([ ] what needs building)
4. **Connections** — directed graph of relationships (`A → B`)
5. **Priority order** — numbered list (1. deploy 2. refactor 3. build)
6. **Health metrics** — running code, revenue, document completeness

### Markmap Source (PROJECT_MAP.mm.md)

Use pure heading hierarchy (no tables, no lists) — markmap parses only `#` headings:

```markdown
# Project Map
## Earnings — $0
### Priority: #1 Deploy
## Service Booking
### salon-bot ⭐
#### Status: Active
#### Stack: aiogram 3
## Tourism
### crimea-bots
#### Status: Active
```

### Verification

- Every project appears in at least one theme
- No dead projects (each has a status and next action)
- Priority order is actionable (not philosophical)
- Health metrics exist and are measurable
- Connections make sense (no imaginary links)
- Mindmap renders in browser without errors
- Business plan has pricing, financial projection, action plan
