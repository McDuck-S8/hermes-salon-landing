---
name: suggestions-engine
description: Suggestions Engine — weekly cron scans agent workload, performance, gaps → proposes new specialist agents for overloaded ones. Self-healing organizational design.
---

# Suggestions Engine — Autonomous Org Design

Weekly analysis → detects bottlenecks → proposes new agents → auto-creates skill scaffolds.

## Architecture

```
suggestions-engine/
├── SKILL.md                    # This file
├── references/
│   ├── ANALYSIS_PROMPT.md          # LLM prompt for weekly analysis
│   ├── AGENT_METRICS.md            # What metrics to collect
│   └── PROPOSAL_TEMPLATE.md        # New agent proposal format
├── scripts/
│   ├── collector.py              # Gathers metrics from all agents
│   ├── analyzer.py               # LLM analysis → proposals
│   ├── proposer.py               # Creates agent scaffolds + PR
│   └── weekly_cron.py            # Entry point for cron job
└── templates/
    ├── NEW_AGENT_SKILL.md.template
    └── NEW_AGENT_CLAUDE.md.template
```

## Metrics Collected (per agent, per week)

| Metric | Source | Threshold for Action |
|--------|--------|---------------------|
| Task count | fabric entries | >50/week |
| Avg duration | fabric timestamps | >30min avg |
| Failure rate | outcome=failure | >20% |
| Tool diversity | tool tags | >10 unique |
| Domain spread | axis_domain | >5 domains |
| Blocked count | blocker tags | >5/week |
| Skill gaps | missing skills | referenced but not owned |

## Analysis Prompt (to Main/LLM)

```
Analyze weekly agent metrics for Hermes Hive Mind.
Current agents: main, comms, content, ops, research.

METRICS:
{per_agent_metrics}

Identify:
1. Overloaded agents (high task count, high duration, high failures)
2. Domain clusters without clear ownership
3. Recurring tool combinations suggesting new specialization
4. Cross-agent dependencies causing bottlenecks

Propose 0-2 new agents with:
- Name, role, primary domain
- Capability keywords
- Tools needed
- Handoff boundaries with existing agents
- Skill scaffolding requirements
```

## Proposal Output

```json
{
  "proposals": [
    {
      "name": "analytics",
      "role": "Data & Metrics Specialist",
      "domain": "analytics",
      "keywords": ["dashboard", "kpi", "metric", "sql", "chart", "report"],
      "tools": ["terminal", "file", "web"],
      "handoffs": {
        "main": "receives metric requests",
        "ops": "provides infra metrics",
        "content": "provides content performance"
      },
      "skills_needed": ["dashboard-builder", "sql-analytics", "chart-generator"],
      "confidence": 0.85,
      "reasoning": "Content and Ops both request dashboards weekly. No owner for metrics."
    }
  ]
}
```

## Auto-Execution

If confidence ≥ 0.8 and `HERMES_SUGGESTIONS_AUTO_CREATE=true`:
1. Create agent directory + CLAUDE.md + agent.yaml
2. Scaffold skill directories from templates
3. Register in War Room agent list
4. Create PR/commit for review

## Cron Schedule
```env
HERMES_SUGGESTIONS_CRON="0 3 * * 1"  # Monday 3 AM
HERMES_SUGGESTIONS_AUTO_CREATE=false  # Require human approval by default
```

## Kill Switch
```env
HERMES_SUGGESTIONS_ENABLED=true
```