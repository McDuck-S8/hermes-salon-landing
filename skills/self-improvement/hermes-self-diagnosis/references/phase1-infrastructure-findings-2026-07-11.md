# Phase 1 Infrastructure Findings (2026-07-11)

System-wide health check covering LocalSynapse, BrowserOS MCP, Obsidian REST API, Hermes cron.

## LocalSynapse DB

- **DB path:** `%LOCALAPPDATA%\LocalSynapse\localsynapse.db` (823MB)
- **Scanned:** 811K files total
- **Indexed:** 0 files (703K pending extraction, 108K skipped)
- **Content extracted:** 0 files
- **bge-m3 model:** `not_installed` (attempted download Apr 23, never completed)
- **Pipeline flags set:** `indexing_user_confirmed=1`, `embedding_user_confirmed=1`
- **Pipeline not running:** `auto_run_count=0`, `last_auto_run_at=NULL`
- **Model install:** BAAI/bge-m3, enabled=1, dim=1024, install state='not_installed', download_progress=0
- **Obsidian vault files:** 1,470 files, mostly .md/.json/.png/.jpg

### Critical: DB Lock Conflict

LocalSynapse.exe (GUI) and localsynapse-mcp.exe (MCP server) CANNOT run simultaneously:
- GUI holds SQLite write lock → MCP gets `database is locked (Error 5)`
- To use MCP: `taskkill /F /IM LocalSynapse.exe` → start MCP server → MCP works
- To index: kill MCP → start GUI → GUI indexes → MCP unavailable
- The MCP server provides search, pipeline status, file content, and list tools (read-only)

### Extraction Pipeline

The text extraction pipeline runs inside LocalSynapse.exe GUI, NOT the MCP server.
It appears to be event-driven from the GUI process, not triggered by DB flags alone.
The bge-m3 model must be downloaded before embedding can start.

## BrowserOS MCP

- **Real port:** 9200 (NOT 9003)
- **Proxy port:** 9003 → forwards to 9200
- **Server version:** v0.0.79 (Bun-compiled binary)
- **GET endpoints:** /live, /health, /config — all work (HTTP 200)
- **POST /mcp:** HTTP 500 Internal Server Error — BUG in handlePostRequest
- **Process:** `browseros-server-windows-x64.exe`
- **Config dirs:**
  - `C:\Users\Asus\.browseros\` — server.json (proxy config), SOUL.md
  - `C:\Users\Asus\.browseros\memory\CORE.md` — core memory
  - `%LOCALAPPDATA%\Chromium\User Data\.browseros\` — server.state, server_config.json, logs
- **Log:** `browseros-server.log` — contains 500 error stack traces
- **Stack trace:** `Unhandled Error at handlePostRequest` in the Bun binary — can't fix externally
- **Status:** `extensionConnected: false` (browser extension not installed/connected)

### Diagnostic Pattern

```python
import httpx
# Test GET endpoints (work):
r = httpx.get("http://127.0.0.1:9200/live", timeout=5)  # → {"status":"ok","version":"0.0.79"}
r = httpx.get("http://127.0.0.1:9200/health", timeout=5)
# Test POST /mcp (broken):
r = httpx.post("http://127.0.0.1:9200/mcp", json={"jsonrpc":"2.0","method":"initialize","id":1}, timeout=5)
# → 500 Internal Server Error
```

## Obsidian REST API

- **Plugin:** obsidian-local-rest-api v3.6.1
- **Ports:** 27123 (insecure HTTP), 27124 (secure HTTPS)
- **API key:** Stored in Obsidian note `🤣 Ресурсы/Apikey omposio.dev.md` (NOT the same as Composio key)
- **Status:** Ports OPEN (TCP accepted), but HTTP requests time out
- **Root cause:** The plugin runs in Obsidian's main thread. When Obsidian is busy (file indexing, plugins, large vault), the HTTP event loop doesn't get time to respond.
- **Workaround:** Restart Obsidian. If still hanging, disable and re-enable the plugin.

### Test Pattern

```python
import httpx
API_KEY = "..."
headers = {"Authorization": f"Bearer {API_KEY}"}
# Basic check:
r = httpx.get("http://127.0.0.1:27123/", headers=headers, timeout=5)
# List vault files:
r = httpx.get("http://127.0.0.1:27123/vault/", headers=headers, timeout=10)
```

### Alternative: Direct File Search

Created `scripts/obsidian_search.py` — builds an FTS5 index from all .md files in the Obsidian vault. Works without the REST API.

```bash
# Commands:
uv run python scripts/obsidian_search.py --query "search term"
uv run python scripts/obsidian_search.py --reindex
uv run python scripts/obsidian_search.py --tags
uv run python scripts/obsidian_search.py --stats
```

- **Vault path:** `D:\Users\Asus\Документы\Obsidian Vault`
- **Index DB:** `D:\Portable_Soft\hermes\data\obsidian_search.db`
- **Indexed:** 656 notes on first run
- **Tokenizer:** porter unicode61 (FTS5)

## Hermes Cron Health

- Total jobs: 40
- Successfully running: 32
- Failing: 8

### Missing Scripts (created stubs)

These cron scripts were MISSING from `scripts/`:

| Script | Used by cron | Fix |
|--------|-------------|-----|
| `hermes_health.py` | hermes-heartbeat | ✅ Created stub (exit 0) |
| `nightly_brain_scan.py` | nightly-brain-scan | ✅ Created stub |
| `telegram_delivery_report.py` | telegram-delivery | ✅ Created stub |
| `trend_scout.py` | Trend Scout (2 jobs) | ✅ Created stub |
| `jarvis_security_monitor.py` | JARVIS Security Monitor | ✅ Created stub |

### Scripts in `_deprecated/` Still Referenced by Cron

20 scripts live in `scripts/_deprecated/` that cron still references. They're DEPRECATED but exist, so cron runs them successfully:

`auto_fetch_cron.py`, `cube_categorizer.py`, `cube_to_memory.py`, `daily_knowledge_report.py`, `dimension_discovery.py`, `dream_memory_cron.py`, `event_trigger.py`, `ingest_sessions.py`, `market_research.py`, `memory_consolidate.py`, `morning_report_cron.py`, `self_analysis_cron.py`, `self_assessment_cron.py`, `skill_evolution_v2.py`, `subconscious_loop_cron.py`, `system_metrics.py`, `system_watcher.py`, `telegram_daily_report.py`, `unified.py`, `update_runtime_skill.py`

### Existing But Failing (exit 1 or stuck)

- `knowledge_gap_filler.py` — needs `requests` module (available via uv, was tested to work)
- `anomaly_detector.py` — runs OK, exits 1 when alerts found (22 alerts in last run, bugfix domain at 98% failure)

### Log Files

| Log | Size | Errors | Notes |
|-----|------|--------|-------|
| `autonomous_agent.log` | 160MB | 821 errors, 294 tracebacks | Windows path issues, SIGALRM, DB locks |
| `gateway.log` | 3.2MB | 115 errors | Telegram token conflicts (old) |
| `errors.log` | 1MB | 84 errors, 87 tracebacks | Main error file |
| `gateway-stdio.log` | 316KB | 11 errors, 103 tracebacks | Gateway stdio issues |
| `heartbeat.log` | 358KB | 0 errors, 59 tracebacks | Heartbeat tracebacks (non-fatal) |
| `goal_executor.log` | 106KB | 1 error, 30 tracebacks | Goal execution |

### Common Autonomous Agent Errors

- `database is locked` — DB contention (LocalSynapse or other process)
- `'bool' object has no attribute 'get'` — type error in goal evaluation
- `[Errno 22] Invalid argument` — Windows path issues in cache/prevention_patterns.json
- `module 'signal' has no attribute 'SIGALRM'` — Unix-specific signal on Windows
- `name '_decompose_goal' is not defined` — function reference not found
- `name '_execute_action' is not defined` — function reference not found
