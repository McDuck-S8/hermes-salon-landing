# Install herdr-multiagent

## Prerequisites

| Component | Install Command | Purpose |
|-----------|----------------|---------|
| **Herdr** | `cargo install herdr` | Terminal workspace manager |
| **Windows Terminal** | Microsoft Store | Required for Herdr TUI |
| **Hermes profiles** | See below | Separate config per agent role |

## 1. Install Herdr

```bash
# Install Rust if needed
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Install Herdr
cargo install herdr

# Verify
herdr --version  # herdr 0.1.0
```

**Must run in Windows Terminal** (not Git Bash/MSYS).

## 2. Create Hermes Profiles

Each agent role needs its own Hermes profile:

```bash
# Base profile (orchestrator)
hermes profile create orchestrator

# Agent profiles
hermes profile create coder
hermes profile create browser
hermes profile create researcher
hermes profile create deployer
hermes profile create cpa-operator
```

Each profile gets isolated:
- `~/.hermes/profiles/<name>/config.yaml`
- `~/.hermes/profiles/<name>/skills/`
- `~/.hermes/profiles/<name>/memories/`
- `~/.hermes/profiles/<name>/cron/`

## 3. Configure Profiles

**Orchestrator profile** (`orchestrator`):
```yaml
# ~/.hermes/profiles/orchestrator/config.yaml
mcp:
  servers: {}
skills:
  - superpowers:using-superpowers
  - superpowers:writing-plans
```

**Coder profile** (`coder`):
```yaml
# ~/.hermes/profiles/coder/config.yaml
mcp:
  servers: {}
skills:
  - software-development:coding-toolkit
  - superpowers:subagent-driven-development
```

**Browser profile** (`browser`):
```yaml
# ~/.hermes/profiles/browser/config.yaml
mcp:
  servers:
    browserclaw:
      type: http
      url: http://127.0.0.1:9010/mcp
    browseros:
      type: http
      url: http://127.0.0.1:9003/mcp
skills:
  - automation:ego-windows
  - automation:browser-automation-toolkit
```

**Researcher profile** (`researcher`):
```yaml
# ~/.hermes/profiles/researcher/config.yaml
mcp:
  servers: {}
skills:
  - autonomous-ai-agents:omh-deep-research
  - integration:agent-reach
```

**Deployer profile** (`deployer`):
```yaml
# ~/.hermes/profiles/deployer/config.yaml
mcp:
  servers: {}
skills:
  - devops:github-pages-deployment
  - devops:devops-toolkit
```

**CPA Operator profile** (`cpa-operator`):
```yaml
# ~/.hermes/profiles/cpa-operator/config.yaml
mcp:
  servers: {}
skills:
  - finance:cpa-affiliate-bot-development
  - automation:n8n
```

## 4. Start MCP Servers (for browser agent)

```bash
# Terminal 1: BrowserClaw MCP
hermes gateway run  # starts both BrowserClaw (9010) and BrowserOS (9003)

# Terminal 2: browser-harness (YOUR Chrome)
cd /d/Portable_Soft/hermes/browser-harness
python -m src.browser_harness.daemon
# Requires Chrome with: --remote-debugging-port=9222
```

## 5. Setup Workspace

```bash
# Create agent workspaces
mkdir -p /d/Portable_Soft/hermes/workspaces/{orchestrator,coder,browser,researcher,deployer,cpa-operator}

# Initialize agent bus
python -c "
from skills.herdr_multiagent import get_bus
bus = get_bus()
print('Agent bus ready at:', bus.bus_dir)
"
```

## 6. Launch Herdr Workspace

```bash
# In Windows Terminal:
herdr

# Then run setup (creates spaces/panes):
herdr-multiagent setup --roles orchestrator,coder,browser,researcher,deployer,cpa-operator
```

## 7. Verify

```bash
# Check spaces created
herdr space list

# Check agent status
agent_status --all

# Send test task
agent_send --to coder --type task --payload '{"test": "hello"}' --from orchestrator

# Receive in coder pane
agent_receive --agent coder --limit 5
```

## Quick Test Script

```bash
# One-liner to verify everything
python -c "
import sys
sys.path.insert(0, 'skills/herdr-multiagent')
from scripts.herdr_multiagent import HerdrMultiAgent
from scripts.agent_bus import get_bus
from scripts.task_templates import TaskTemplateManager, ensure_builtin_templates

# Test orchestrator
o = HerdrMultiAgent()
print('Roles:', list(o.roles.keys()))

# Test bus
bus = get_bus()
msg_id = bus.send(bus.__class__.__bases__[0](id='test', from_agent='test', to_agent='test', type='test', payload={}, timestamp=''))
print('Bus OK')

# Test templates
mgr = TaskTemplateManager()
ensure_builtin_templates(mgr.templates_dir)
print('Templates:', [t['name'] for t in mgr.list_templates()])
"
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `herdr: command not found` | Add `~/.cargo/bin` to PATH, restart terminal |
| `Keyboard progressive enhancement...` | Use **Windows Terminal**, not Git Bash |
| `Herdr not found in PATH` | Install via `cargo install herdr` |
| Spaces not creating | Run `herdr` first to initialize, then run setup |
| Agent not receiving messages | Check `cache/agent_bus/` permissions, verify profile name matches |
| MCP connection failed | Ensure `hermes gateway run` is running, check ports 9010/9003 |
| Chrome CDP not connecting | Start Chrome with `--remote-debugging-port=9222` |

## Architecture

```
herdr-multiagent/
├── SKILL.md                    # This documentation
├── __init__.py                 # Exports
├── scripts/
│   ├── herdr_multiagent.py     # Main orchestrator class
│   ├── agent_bus.py            # Message bus (KC + files)
│   ├── space_manager.py        # Herdr CLI automation
│   ├── task_templates.py       # Template loader/renderer
│   └── cli.py                  # CLI entry points
├── templates/
│   ├── cpa-scrape.yaml         # CPA offer scraping
│   ├── code-implement.yaml     # Code implementation
│   ├── omh-research.yaml       # OMH deep research
│   └── deploy-github-pages.yaml # GitHub Pages deploy
└── references/
    └── install.md              # This file
```