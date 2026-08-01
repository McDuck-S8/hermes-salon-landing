# CLI Integration — Implementation Notes (Session 2026-07-03)

## Actual Work Done

### 1. Skill Skeleton Created
- `SKILL.md` with full architecture
- Command registry design
- Auto-discovery from skills/*/scripts/*.py and agents/*/
- Global install via `hermes install`
- Shell completion (bash/zsh/fish)

### 2. Key Design Decisions
- **Skills expose CLI via** `cli_commands` in SKILL.md frontmatter or `cli.py` in scripts/
- **Auto-discovery** on startup: scan skills + agents for commands
- **Command tree** built dynamically, registered as subcommands
- **Global shim** at `~/.local/bin/hermes` pointing to current env

### 3. Command Registry Pattern
```yaml
# In SKILL.md frontmatter or cli.py
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

### 4. Next Steps
1. Implement `scripts/cli_entry.py` — main `hermes` entry point
2. Implement `scripts/command_dispatcher.py` — routes subcommands
3. Implement `scripts/skill_loader.py` — discovers skills commands
4. Implement `scripts/agent_loader.py` — discovers agents commands
5. Implement `scripts/install.py` — global shim + shell completion
6. Add CLI commands to existing skills (test-harness, kill-switches, war-room, etc.)