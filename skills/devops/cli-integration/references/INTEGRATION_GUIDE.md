# CLI Integration Pattern Integration Guide

## Integration Points (Planned)

- **Global Install** → `hermes install` creates `~/.local/bin/hermes` shim
- **Auto-Discovery** → scans `skills/*/scripts/*.py` for `cli_commands` export
- **Agent Discovery** → scans `agents/*/agent.yaml` for `cli_commands`
- **Command Dispatcher** → unified command tree with dynamic subcommands

## Architecture

```
hermes (CLI entry)
       │
       ▼
cli_entry.py → command_dispatcher.py
       │
       ▼
skill_loader.py → discovers skills/*/scripts/*.py cli_commands
       │
       ▼
agent_loader.py → discovers agents/*/agent.yaml cli_commands
       │
       ▼
Unified command tree → executes handler
```

## Skill CLI Template

```python
# skills/my-skill/scripts/cli.py
def cli_commands():
    return [
        {
            "name": "my-skill",
            "handler": "skills.my_skill.scripts.my_module:main",
            "description": "Does X",
            "args": [
                {"name": "--input", "required": True},
                {"name": "--output", "default": "stdout"}
            ]
        }
    ]

def main(args):
    # Your logic
    pass

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
```

## Agent CLI Template

```yaml
# agents/my-agent/agent.yaml
cli_commands:
  - name: "my-agent"
    handler: "agents.my_agent.scripts.cli:main"
    description: "Agent-specific command"
    args:
      - name: "--goal"
        required: true
```

## Auto-Discovery Logic

On `hermes` startup:
1. Scan `skills/*/scripts/*.py` for `cli_commands` export
2. Scan `agents/*/agent.yaml` for `cli_commands`
3. Build unified command tree
4. Register subcommands dynamically

## Global Install

```bash
# User runs once:
hermes install

# Creates ~/.local/bin/hermes shim → points to current env
# Adds shell completion (bash/zsh/fish)
# Registers `hermes` globally
```

## Usage Examples

```bash
# Core commands
hermes war-room standup
hermes war-room discuss --question "Add LanceDB?"
hermes kill-switch status
hermes kill-switch disable HERMES_LLM_ENABLED
hermes memory query "test experience" --layer 3
hermes content research --topic "arbitrage"
hermes content create --spec specs/topic_123.json
hermes agent spawn --role content --goal "Write article"

# Skill management
hermes skill list
hermes skill enable test-harness
hermes skill create my-skill --category finance

# Agent management
hermes agent list
hermes agent spawn --name analyst --role research
```

## Kill Switch
```env
HERMES_CLI_ENABLED=true
```