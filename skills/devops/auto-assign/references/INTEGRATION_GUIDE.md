# Auto-Assign Integration Guide

## Integration Points (Planned)

- **Telegram Bridge** → on incoming command/goal → `auto_assign.route()`
- **Goal Executor** → before spawning agent → classify first
- **Signal Daemon** → on new external signal → route to Research or Content
- **Cron** → scheduled tasks can self-route

## Architecture

```
User Goal / Signal
       │
       ▼
router.route(goal_text, context)
       │
       ▼
classifier.classify(goal_text)  ──► Gemini Flash (cheap, fast)
       │
       ▼
Returns: {agent: "content", confidence: 0.92, reasoning: "..."}
       │
       ▼
If confidence < 0.7 → fallback to Main (coordinator)
       │
       ▼
Log assignment → dispatch to agent
```

## Agent Capability Matrix (for classifier)

| Agent | Keywords | Domains | Tools | Typical Goals |
|-------|----------|---------|-------|---------------|
| Main | coordinate, decide, synthesize, prioritize | all | all | routing, war room, cross-cutting |
| Comms | telegram, email, notify, message, bridge | communication | telegram, email, slack | send msg, fix bridge, proxy |
| Content | write, publish, repurpose, article, video | content, creative | web, browser, write | create content, pipeline |
| Ops | deploy, cron, server, monitor, cost, infra | devops, system | terminal, cron, docker | fix server, add cron, cost |
| Research | search, analyze, trend, paper, hn, github | research, data | web_search, web_fetch | find info, analyze trend |

## Classifier Prompt (Gemini Flash)

```
You are a router for the Hermes Hive Mind. 
Agents: main, comms, content, ops, research.
Given a user goal, return JSON: {"agent": "...", "confidence": 0.xx, "reasoning": "..."}
Rules:
- Main: coordination, decisions, unclear/broad goals
- Comms: messaging, telegram, email, notifications
- Content: writing, publishing, content pipeline
- Ops: infrastructure, cron, servers, deployment, costs
- Research: external search, trends, papers, competitive intel
```

## Fallback Chain

1. Classifier confidence ≥ 0.7 → assigned agent
2. Confidence 0.4-0.7 → Main reviews, decides
3. Confidence < 0.4 → Main handles directly
4. Classifier unavailable → Main (safe default)

## Kill Switch
```env
HERMES_AUTO_ASSIGN_ENABLED=true
```