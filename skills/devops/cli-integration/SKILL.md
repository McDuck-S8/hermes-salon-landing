---
name: cli-integration
description: CLI Integration Pattern — Global `hermes` CLI install, auto-discovery of skills, commands, agents. One binary to rule them all.
---

# CLI Integration Pattern — Global Hermes CLI

Makes Hermes installable, discoverable, and extensible via single `hermes` command.

## Architecture

```
cli-integration/
├── SKILL.md                    # This file
├── references/
│   ├── COMMAND_REGISTRY.md          # All commands + handlers
│   ├── SKILL_DISCOVERY.md           # How skills register commands
│   └── AGENT_DISCOVERY.md           # How agents register
├── scripts/
│   ├── cli_entry.py              # Main `hermes` entry point
│   ├── command_dispatcher.py     # Routes subcommands
│   ├── skill_loader.py           # Discovers skills/*/scripts/*.py
│   ├── agent_loader.py           # Discovers agents/*/
│   └── install.py                # `hermes install` — global shim
├── templates/
│   ├── COMMAND_TEMPLATE.py
│   └── SKILL_CLI_TEMPLATE.md
└── examples/
    └── custom_command_example.py
```

## Command Registry

Every skill can expose CLI commands by adding `cli_commands` dict to its `SKILL.md` frontmatter or a `cli.py` in its scripts:

```yaml
# In SKILL.md frontmatter or separate cli.py
cli_commands:
  - name: "war-room"
    handler: "skills.devops.war-room.scripts.war_room:main"
    description: "Run /standup or /discuss"
    args:
      - name: "command"
        choices: ["standup", "discuss"]
      - name: "--question"
        required_if: "command==discuss"
```

## Auto-Discovery

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

## Kill Switch
```env
HERMES_CLI_ENABLED=true
```