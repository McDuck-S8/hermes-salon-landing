# Hermes WebUI on Windows (No Docker)

## Quick Start

```bash
cd /d/Portable_Soft/hermes-webui
HERMES_WEBUI_AGENT_DIR=/d/Portable_Soft/hermes/hermes-agent python server.py
```

Server listens at http://127.0.0.1:8787 by default.

## Why It Works

The WebUI is a **pure Python HTTP server** (`server.py` + `api/*` modules). The bootstrap.py
that says "Native Windows is not supported" is ONLY for first-time dependency installation
(venv creation, pip install). The server itself has zero Docker dependency and runs on any
platform with Python 3.10+.

## Env Vars

| Variable | Purpose | Default |
|----------|---------|---------|
| `HERMES_WEBUI_AGENT_DIR` | Path to hermes-agent source | `$HERMES_HOME/hermes-agent` |
| `HERMES_HOME` | Hermes config directory | `%LOCALAPPDATA%/hermes` (Win) or `~/.hermes` (POSIX) |
| `HERMES_WEBUI_HOST` | Listen address | `127.0.0.1` |
| `HERMES_WEBUI_PORT` | Listen port | `8787` |
| `HERMES_WEBUI_STATE_DIR` | WebUI state (sessions, settings) | `$HERMES_HOME/webui` |

## Start-portable.bat

The shipped launcher expects `D:\Portable_Soft\hermes-usb-portable-main` with its own Python
runtime. If you already have Python + Hermes installed, just use the env-var approach above.

## Features Available

- Chat (full conversation with Hermes)
- Tasks management
- Kanban board
- Skills browser (browse, search, create)
- Memory viewer
- Workspace files
- Agent profiles
- Todos
- Insights (statistics)
- Logs viewer
- Settings (provider, model, themes)

## Troubleshooting

- **Port 8787 busy**: Set `HERMES_WEBUI_PORT=8788`
- **"Failed to load plugin 'hermes-lcm'"**: Non-fatal warning on Windows (statvfs is Unix-only)
- **Agent not found**: Point `HERMES_WEBUI_AGENT_DIR` to the actual hermes-agent checkout
