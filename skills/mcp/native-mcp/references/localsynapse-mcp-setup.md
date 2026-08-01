# LocalSynapse MCP — Content Search on Windows

## What It Is

LocalSynapse is a Windows application that indexes local file contents into a SQLite database for fast search, with an MCP server (`localsynapse-mcp.exe`) for LLM integration.

## Setup

### Add to Hermes MCP Config

In `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  localsynapse:
    command: 'D:\Program Files\LocalSynapse\localsynapse-mcp.exe'
    args: []
```

Use **single quotes** for the Windows path to avoid YAML escaping issues with backslashes.

### Add to Claude Desktop MCP

```bash
claude mcp add localsynapse -- "D:\Program Files\LocalSynapse\localsynapse-mcp.exe"
```

This adds to `~/.claude.json` under `projects."C:/Users/<user>".mcpServers.localsynapse`.

## Database Lock Issue

If `LocalSynapse.exe` (the main desktop app) is running, the MCP server fails with:

```
SQLite Error 5: 'database is locked'
```

The main process holds a write lock on the SQLite DB. The MCP server tries to open the same DB and gets locked out.

**Workarounds:**
1. **Stop LocalSynapse.exe** before starting the MCP server (kill PID via Task Manager or `taskkill /PID <ID>`)
2. **Use a separate index** — configure a different SQLite DB path for the MCP server (if supported)
3. **Don't use MCP** — query the SQLite DB directly with Python (`import sqlite3`, `conn = sqlite3.connect('path/to/index.db')`)

## Status

- **Hermes config**: Added ✅
- **Claude Desktop MCP**: Added ✅
- **Connection**: ⚠️ Blocked by database lock when main app is running
