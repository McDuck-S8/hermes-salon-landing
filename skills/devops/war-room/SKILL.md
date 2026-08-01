---
name: war-room
description: War Room pattern from AI-First Business Playbook — multi-agent council with /standup and /discuss commands. Agents respond independently, consolidator synthesizes.
---

# War Room — Multi-Agent Council

Implements the AI-First Business Playbook War Room pattern:
- **Text War Room** (lower complexity, lower cost)
- **Voice War Room** (cinematic, higher complexity, requires voice features)

---

## Key Implementation Lessons (2026-07-03)

### Agent Creation
- Create agent directories under `HERMES_HOME/agents/<name>/`
- Each agent needs `agent.yaml` (model, tools) + `CLAUDE.md` (persona)
- Personas MUST be distinct: Main (coordinator), Comms (messaging), Content (pipeline), Ops (infra), Research (external intel)

### Mock Runner for Testing
- Created `war_room_mock.py` for testing without Claude CLI
- Uses same prompt templates + deterministic mock responses per persona
- Validates prompt flow, transcript saving, consolidator logic

### Integration
- CLI: `python scripts/war_room.py standup --agents main,comms,content,ops,research`
- CLI: `python scripts/war_room.py discuss --question "..." --agents main,comms,content,ops,research`
- Hot-reload watches `.env` for `WARROOM_TEXT_ENABLED` / `WARROOM_VOICE_ENABLED`

## Architecture

```
war-room/
├── SKILL.md                    # This file
├── references/
│   ├── WAR_ROOM_PROMPT_PATTERNS.md    # Prompt templates
│   ├── CONSOLIDATOR_GUIDE.md          # How consolidator works
│   └── AGENT_PERSONAS.md              # Required agent personas
├── scripts/
│   ├── war_room.py              # Main orchestrator
│   ├── standup.py               # /standup handler
│   ├── discuss.py               # /discuss handler
│   ├── consolidator.py          # Synthesis agent
│   └── agent_runner.py          # Runs individual agents
├── templates/
│   ├── STANDUP_PROMPT.md.template
│   ├── DISCUSS_PROMPT.md.template
│   └── CONSOLIDATOR_PROMPT.md.template
└── examples/
    └── example_war_room_session.md
```

## The Two Commands

### `/standup` — Morning Report
```
User: /standup
System:
  1. For each agent in war_room_agents:
     - Build status prompt: "Quick standup status. 2-3 sentences max. Cover: what you wrapped, what's queued, any blockers."
     - Run agent sequentially
     - Stream responses back as they complete
  2. Mark all responses with same source_turn_id for atomic persistence
```

### `/discuss <question>` — Council Deliberation
```
User: /discuss Should we add LanceDB to Knowledge Cube?
System:
  1. For each agent in war_room_agents:
     - Build discussion prompt: "The user just asked: <question>. From your perspective and based on what you have access to, give your take in 3-5 sentences."
     - Run agents sequentially (NOT in parallel - each needs full context)
  2. After all agents respond, run consolidator agent (Main by default):
     - Prompt: "Based on the above responses from [agent list], what's the recommendation?"
  3. Stream all responses, then consolidator synthesis
```

## Agent Requirements

Each agent in war room MUST have:
- Unique persona (CLAUDE.md) with distinct perspective
- Focused tool allowlist (default-deny on side effects)
- Access to relevant memory/skills
- `warroom_tools:` in agent.yaml for side effects during war room (optional)

## Integration Points

- **Telegram Bridge** — intercepts `/standup` and `/discuss` commands
- **Event Bus** — emits `war_room_standup` and `war_room_discuss` events
- **Audit Log** — records every war room session
- **Kill Switch** — `WARROOM_TEXT_ENABLED` gates text war room
- **Memory** — war room transcripts stored in `warroom_transcript` table

## Kill Switch
```env
WARROOM_TEXT_ENABLED=true    # default true
WARROOM_VOICE_ENABLED=false  # requires voice features
```

## Usage

```bash
# Start war room (via Telegram command)
/standup

# Or programmatically
python scripts/war_room.py standup --agents main,comms,content,ops,research

python scripts/war_room.py discuss --question "Should we add LanceDB?" --agents main,comms,content,ops,research
```