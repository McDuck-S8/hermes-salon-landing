---
name: auto-assign
description: Auto-Assign — Gemini Flash classifier routes incoming goals/tasks to the right specialist agent. Reduces manual routing, enables scalable hive mind.
---

# Auto-Assign — Intelligent Task Routing

Routes user goals, tasks, and signals to the correct agent automatically using a lightweight classifier (Gemini Flash).

## Architecture

```
auto-assign/
├── SKILL.md                    # This file
├── references/
│   ├── CLASSIFIER_PROMPT.md          # Prompt for Gemini Flash
│   ├── AGENT_CAPABILITIES.md         # Structured agent capability matrix
│   └── ROUTING_RULES.md              # Fallback & override rules
├── scripts/
│   ├── classifier.py            # Calls Gemini Flash, returns agent name
│   ├── router.py                # Main entry: route(goal) -> agent
│   └── capability_index.py      # Builds/maintains agent capability vectors
└── templates/
    └── ASSIGNMENT_LOG.md.template
```

## Flow

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

## Integration Points

| Component | Hook | Function |
|-----------|------|----------|
| Telegram Bridge | `scripts/telegram_bridge.py:141-170` | `handle_incoming_message(text, chat_id, metadata)` → `route_goal()` |
| Goal Executor | `scripts/goal_executor.py:194-210` | Auto-assign before `execute_goal()` |
| Goal Queue | `scripts/goal_queue.py:91-95` | `emit("goal_created", ...)` after `create_goal()` |
| Signal Daemon | (future) | On `new_external_signal` → route to Research/Content |

## Event-Driven Flow

```
signal_daemon.py (HN, GitHub trending)
       │
       ▼
event_bus.py emit new_external_signal
       │
       ├──► rd_processor (DIRECT) → workshop
       ├──► dev_processor (DIRECT) → goal queue (create_goal)
       └──► cube_feeder (DIRECT) → KC
       │
       ▼
goal_queue.create_goal() → emit("goal_created")
       │
       ▼
event_bus.DIRECT_EVENT_HANDLERS["goal_created"] → _handle_goal_created()
       │
       ▼
goal_executor.py goal_id (auto-assigns agent via auto-assign)
       │
       ▼
Execution → knowledge_added → cube_feeder
```

**No cron.** Event-driven only.

## Kill Switch
```env
HERMES_AUTO_ASSIGN_ENABLED=true
```

## Fallback Chain

1. Classifier confidence ≥ 0.7 → assigned agent
2. Confidence 0.4-0.7 → Main reviews, decides
3. Confidence < 0.4 → Main handles directly
4. Classifier unavailable → Main (safe default)