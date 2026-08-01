# Hermes WebUI on Native Windows (No Docker)

The Hermes WebUI ships with `bootstrap.py` which refuses native Windows ("Native Windows is not supported"). **This check is for the installer/bootstrap only — the server itself runs fine on Windows.**

## Quick Start

```bash
cd /d/Portable_Soft/hermes-webui
HERMES_WEBUI_AGENT_DIR=/d/Portable_Soft/hermes/hermes-agent python server.py
```

That's it. Server listens on http://127.0.0.1:8787 by default.

## Env Vars That Actually Matter

| Variable | Purpose | Default |
|---|---|---|
| `HERMES_WEBUI_AGENT_DIR` | Path to hermes-agent source code | auto-detect from HERMES_HOME |
| `HERMES_HOME` | Hermes config root ($HOME/.hermes) | platform default |
| `HERMES_WEBUI_HOST` | Bind address | 127.0.0.1 |
| `HERMES_WEBUI_PORT` | Port | 8787 |
| `HERMES_WEBUI_STATE_DIR` | Sessions, settings, pins | HERMES_HOME/webui |
| `HERMES_WEBUI_AUTO_INSTALL` | Auto-install agent deps | 0 (off) |

## What Works

- Chat (full conversation)
- Tasks, Kanban, Todos
- Skills browser (all 182 skills visible)
- Memory viewer
- Spaces, Agent profiles
- Insights, Logs, Settings
- File workspace

Just the full web UI over HTTP.

## What Doesn't (or Isn't Needed)

- `bootstrap.py` — refuses Windows; skip it, run server.py directly
- `start.sh` — Linux/macOS only
- `start-portable.bat` — expects hermes-usb-portable-main structure; skip it
- Docker — not needed, server is pure Python stdlib HTTP

## Pitfalls

- The "Failed to load plugin 'hermes-lcm': module 'os' has no attribute 'statvfs'" warning on startup is harmless (statvfs is Unix-only)
- State dir defaults to `%LOCALAPPDATA%\hermes\webui` on Windows. Set `HERMES_WEBUI_STATE_DIR` explicitly if you want it elsewhere.
- Server logs are structured JSON to stdout; they're silent per-request (only errors show up).
- Test with: `curl http://127.0.0.1:8787/health` (returns HTTP 200 when alive)

## Lessons Learned

The bootstrap.py platform check is *not* a runtime check — it's an install-flow guard. The server itself has no Windows-specific blockers. When in doubt, try `python server.py` directly before declaring something "won't work on Windows."
