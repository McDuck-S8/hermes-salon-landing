# Filesystem-First Architecture (Lazy Mode)

**Origin:** Session 2026-07-16 — user rejected eve/Node.js/Docker, demanded native Python implementation of eve's architectural ideas.

## Core Principle

**The filesystem IS the API.** No JSON config, no registry, no database. Folders and files ARE the configuration.

## Structure

```
agent/
├── instructions.md      # System prompt (the "brain")
├── tools/               # Custom tools (one file = one tool)
├── skills/              # Load-on-demand procedures
├── schedules/           # Cron jobs (YAML files)
├── channels/            # Message adapters
└── subagents/           # Specialist agents (folder = agent)
    ├── researcher/
    │   ├── agent.yaml   # model, description, tools, skills
    │   ├── instructions.md
    │   └── eval.yaml    # Test cases
    ├── writer/
    └── deployer/
```

## Loader Pattern (50 lines, stdlib)

```python
from pathlib import Path
import yaml

def load_all_subagents(root: Path) -> dict:
    subagents = {}
    for item in root.iterdir():
        if item.is_dir():
            agent_yaml = item / "agent.yaml"
            if agent_yaml.exists():
                config = yaml.safe_load(agent_yaml.read_text())
                config['instructions'] = (item / "instructions.md").read_text() if (item / "instructions.md").exists() else ""
                subagents[item.name] = config
    return subagents
```

## Sub-Agent Delegation

```python
# Build prompt from agent.yaml + instructions.md
system_prompt = f"""# Sub-Agent: {config.name}
## Description
{config.description}
## Instructions
{config.instructions}
## Tools
{config.tools}
## Skills
{config.skills}
"""
# delegate_task(goal=message, context=system_prompt, ...)
```

## Eval Tests (YAML per skill/agent)

```yaml
tests:
  - name: "basic_web_search"
    input: "search for latest AI news"
    expected: "found"
    match: "contains"
  - name: "handles_empty_query"
    input: ""
    expected: "error"
    match: "contains"
```

Run: `python -m scripts.skill_eval skills/agent-browser`

## Approval Levels (Decorators)

```python
@approval.always()   # ask every time
@approval.once()     # ask once per session
@approval.never()    # default (fail-safe)
```

## Schedules (YAML)

```yaml
name: daily_check
cron: "0 9 * * *"
prompt: "Check system health..."
skills: [devops]
```

## Ladder Application

| Rung | Decision |
|------|----------|
| 1. Need to exist? | Files exist anyway |
| 2. Stdlib? | `pathlib` + `yaml` |
| 3. Native feature? | Filesystem IS the platform |
| 4. Installed dep? | `pyyaml` (already there) |
| 5. One line? | `Path("agent/subagents").iterdir()` |
| 6. Minimal code | Loader = 50 lines |

## Ceiling

- No hot-reload of prompt changes mid-conversation (prompt caching)
- No GUI for editing schedules (user edits YAML directly)
- Add when user complains about editing files

## Verification

- Skill evals: `python scripts/skill_eval.py skills/` — all green
- Sub-agent loader: loads 3 agents (researcher, writer, deployer) correctly
- Approval decorators: always/once/never work as expected