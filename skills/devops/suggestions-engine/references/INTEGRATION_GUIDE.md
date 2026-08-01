# Suggestions Engine Integration Guide

## Integration Points (Planned)

- **Weekly Cron** → `0 3 * * 1` (Monday 3 AM) → runs `scripts/weekly_cron.py`
- **Metrics Collector** → gathers from all agents via fabric entries
- **Analyzer** → LLM analysis → proposals for new agents
- **Proposer** → creates agent scaffolds + PR for review

## Architecture

```
Weekly Trigger (cron)
       │
       ▼
collector.py → gather metrics from all agents
       │
       ▼
analyzer.py → LLM analysis → proposals JSON
       │
       ▼
proposer.py → create agent scaffolds + skill dirs
       │
       ▼
PR/Commit for human review (or auto-create if confidence ≥ 0.8)
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
- Confidence (0-1)
- Reasoning
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