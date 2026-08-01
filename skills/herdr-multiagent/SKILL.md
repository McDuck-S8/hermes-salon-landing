---
name: herdr-multiagent
description: |
  Multi-agent orchestration via Herdr terminal workspace manager.
  Creates isolated spaces/panes per agent role, shared message bus via Knowledge Cube,
  persistent sessions, and task templates for orchestrator-driven workflows.
version: 1.0.0
category: autonomous-ai-agents
tags: [herdr, multi-agent, orchestration, terminal, workspace, delegation]
---

# herdr-multiagent — Multi-Agent Orchestration via Herdr

**Hermes agents as parallel Herdr spaces. You orchestrate, agents execute.**

## Architecture

```
Windows Terminal (Herdr)
├── Space: "orchestrator"     ← YOU (human)
│   ├── Pane: command         — issue tasks, monitor
│   └── Pane: logs            — aggregated agent logs
├── Space: "coder"            ← Agent: code implementation
│   ├── Pane: editor          — vim/code in repo
│   └── Pane: tests           — pytest, lint
├── Space: "browser"          ← Agent: web automation (ego-windows)
│   ├── Pane: browserclaw     — MCP automation
│   └── Pane: harness         — YOUR Chrome (CDP 9222)
├── Space: "researcher"       ← Agent: OMH deep-research, Agent Reach
│   ├── Pane: search          — YouTube, GitHub, Web
│   └── Pane: synthesize      — KC entries, reports
├── Space: "deployer"         ← Agent: GitHub Pages, n8n, servers
│   ├── Pane: deploy          — git, ssh, docker
│   └── Pane: monitor         — health checks
└── Space: "cpa-operator"     ← Agent: Telegram bot, n8n funnel
    ├── Pane: bot             — aiogram polling
    └── Pane: funnel          — n8n workflow
```

## Quick Start

```bash
# 1. Install Herdr (once)
cargo install herdr

# 2. Run setup (creates spaces, panes, profiles)
herdr-multiagent setup --roles orchestrator,coder,browser,researcher,deployer,cpa-operator

# 3. Launch Herdr in Windows Terminal
herdr

# 4. In orchestrator pane: send tasks
agent_send --to coder "Implement login flow in src/auth.py"
agent_send --to browser "Scrape adcombo offers for geo=IN"
agent_send --to researcher "OMH deep-research: faceless YouTube 2024"
agent_send --to deployer "Deploy smart-home-cpa to GitHub Pages"
agent_send --to cpa-operator "Start n8n funnel + Telegram bot"

# 5. Monitor all
agent_status --all
```

## Core Commands

| Command | Purpose |
|---------|---------|
| `herdr-multiagent setup` | Create spaces/panes/profiles for roles |
| `herdr-multiagent teardown` | Stop all agents, cleanup |
| `agent_send --to <role> "<task>"` | Send task envelope to agent |
| `agent_task --template <name> --params k=v` | Run task from template |
| `agent_status --all` | Table: space, pane, PID, current task, KC writes |
| `agent_logs --role <name> --tail 50` | Stream agent output |
| `agent_kc --role <name>` | Show recent KC entries by agent |

## Message Bus (via Knowledge Cube)

```
agent_send --to coder "Fix bug in auth.py"
        │
        ▼
┌─────────────────────────────────────┐
│ Task Envelope (JSON)                │
│ {                                   │
│   "id": "task-uuid",                │
│   "from": "orchestrator",           │
│   "to": "coder",                    │
│   "type": "implement",              │
│   "payload": {...},                 │
│   "created": "ISO8601",             │
│   "status": "pending"               │
│ }                                   │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│ Knowledge Cube (tasks collection)   │
│ + File: cache/agent_bus/coder.jsonl │
└─────────────────────────────────────┘
        │
        ▼
Agent (coder) polls KC → executes → writes result to KC
        │
        ▼
Orchestrator sees: agent_status shows "completed" + KC entry
```

## Task Templates

```yaml
# templates/cpa-scrape.yaml
name: cpa-scrape
role: browser
params:
  - geo
  - vertical
  - min_payout
script: |
  await navigate({url: "https://adcombo.com/offers?geo={{geo}}&vertical={{vertical}}"})
  const snap = await snapshot()
  return await extract({selector: ".offer-card"})

# templates/omh-research.yaml
name: omh-research
role: researcher
params:
  - topic
  - depth
script: |
  # Calls omh-deep-research skill via OMHIntegration
```

## Files

- `scripts/herdr_multiagent.py` — Main orchestrator class
- `scripts/agent_bus.py` — Message bus via KC + files
- `scripts/space_manager.py` — Herdr space/pane automation
- `scripts/task_templates.py` — Template loader + renderer
- `scripts/cli.py` — CLI entry points (herdr-multiagent, agent_send, etc.)
- `templates/*.yaml` — Task templates
- `references/install.md` — Setup guide