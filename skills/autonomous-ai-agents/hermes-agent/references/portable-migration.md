# Portable Hermes Installation Migration & Diagnosis

## When to Use

Migrating between portable Hermes installations (e.g. USB, different directories) or diagnosing a broken portable installation.

## Critical Files to Migrate

These carry state, configuration, and user context:

| File/Dir | What it contains | Priority |
|----------|-----------------|----------|
| `memories/MEMORY.md` | Agent memory (lessons, project context, rules) | Must |
| `memories/USER.md` | User profile (preferences, style, corrections) | Must |
| `.hermes_history` | Conversation history (autocomplete, context) | Must |
| `branches.yaml` | Project context, active tasks, fix history | Must |
| `skills/` | User-created skills (not bundled ones) | Must |
| `plugins/` | Installed plugins | Must |
| `scripts/` | Custom scripts | Must |
| `cron/jobs.json` | Scheduled tasks | Must |
| `notes/` | User notes | Should |
| `config.yaml` | Main config | Only if same provider |
| `.env` | API keys, proxy, tokens | Only if same setup |
| `auth.json` | OAuth tokens, credential pools | Only if same providers |

**Migrate:**
- `state.db` — **session store, THE most important file**. Contains all sessions, messages, search indices. Without it, conversation history is lost. See "Recovering state.db" below for corruption recovery.
- `sessions/` — request dumps, debug artifacts (optional, low priority)

**Do NOT migrate:**
- `logs/` — historical errors, not portable
- `*.bak.*` — config backups from failed updates
- `models_dev_cache.json` — regenerated on startup
- `kanban.db` — regenerated

## Diagnostic Checklist

When a portable installation stops working:

### 1. Check gateway exit diagnostic
```
cat $HERMES_HOME/logs/gateway-exit-diag.log | tail -20
```
Look for `gateway.exit_nonzero` — repeated failures indicate a persistent issue.

### 2. Check errors.log for API failures
```
grep -i "error\|402\|401\|403\|timeout\|connection" $HERMES_HOME/logs/errors.log | tail -20
```
Common root causes:
- **HTTP 402**: API credits exhausted (OpenGateway, OpenRouter)
- **HTTP 401/403**: API key expired or revoked
- **ConnectTimeout**: proxy down or network issue
- **Connection error**: API endpoint unreachable

### 3. Check state.db size and integrity
```
ls -lh $HERMES_HOME/state.db
sqlite3 $HERMES_HOME/state.db "PRAGMA integrity_check"
```
If integrity returns "ok" but it's >50MB:
- `hermes sessions prune --older-than 30 days`
- `sqlite3 state.db "VACUUM"` to reclaim space

If integrity returns "malformed" — **do NOT delete**. The data is likely recoverable. See "Recovering state.db" below. Sessions and messages can be extracted even from a corrupted DB using immutable mode reads.

### 4. Check proxy connectivity
If using HTTP_PROXY/HTTPS_PROXY in .env:
```
curl -x socks5://proxy:port https://api.telegram.org
```
SOCKS5 proxies (especially third-party) are common failure points.

### 5. Check MCP server health
```
grep "MCP server.*keepalive failed" $HERMES_HOME/logs/errors.log | tail -5
```
Repeated MCP failures → the MCP server binary may be missing or crashed.

### 6. Check for locked files during update
```
grep "WinError 32\|busy\|locked" $HERMES_HOME/logs/update.log
```
Windows locks files during execution — updates fail if gateway is running.

## Common Failure Patterns

### Pattern: Gateway starts then immediately exits
**Symptoms**: `gateway.exit_nonzero` within 1 second of `gateway.start`
**Causes**:
- Port already in use (another gateway running)
- Config parse error (YAML syntax, BOM in config.yaml)
- Missing dependency in venv

### Pattern: Agent freezes / becomes unresponsive
**Symptoms**: User sends messages but no response, interrupt log shows repeated attempts
**Causes**:
- API provider down or credits exhausted
- Proxy timeout blocking all outbound requests
- MCP server hanging (blocks tool loop)
- Context too large (state.db bloated)

### Pattern: Telegram disconnects repeatedly
**Symptoms**: "Telegram network error", "Polling heartbeat probe failed"
**Causes**:
- SOCKS5 proxy unreliable
- Telegram API rate limiting
- Network instability

## Recovering state.db (Corrupted Session Store)

When state.db is corrupted ("database disk image is malformed"), sessions and messages may still be recoverable. This is critical — state.db is the user's entire conversation history.

### Step 1: Read from corrupted DB (immutable mode)

SQLite can often READ a corrupted database even when writes fail. Use `immutable=1` URI mode:

```python
import sqlite3
conn = sqlite3.connect(f"file:{corrupted_db}?mode=ro&immutable=1", uri=True, timeout=30)
c = conn.cursor()
c.execute("SELECT * FROM sessions")  # Usually works even on corrupted DB
sessions = [dict(zip([d[0] for d in c.description], row)) for row in c.fetchall()]
c.execute("SELECT * FROM messages")
messages = [dict(zip([d[0] for d in c.description], row)) for row in c.fetchall()]
conn.close()
```

**Key insight:** `immutable=1` bypasses WAL journaling and lock contention. This often succeeds when normal `sqlite3.connect()` fails with "database disk image is malformed".

### Step 2: Export to JSON, create fresh DB

Export the recovered data to JSON files, then create a fresh database with the correct schema and import:

```python
# Create fresh DB with correct schema (from hermes_state.py)
# Insert sessions, skipping columns that have NOT NULL DEFAULT (let defaults apply)
# DO NOT pass NULL for NOT NULL columns — omit them from INSERT instead
# Rebuild FTS: INSERT INTO messages_fts(messages_fts) VALUES('rebuild')
```

**Pitfall: NOT NULL DEFAULT columns.** If the schema has `rewind_count INTEGER NOT NULL DEFAULT 0`, you must either:
- Pass `0` explicitly, OR
- Omit the column from the INSERT statement entirely (so DEFAULT kicks in)
- Do NOT pass `None`/`NULL` — it will fail with "NOT NULL constraint failed"

### Step 3: Use sqlite3 .recover CLI (alternative)

If immutable mode doesn't work, try the built-in recovery command:

```bash
sqlite3 corrupted.db .recover > recovery.sql
sqlite3 fresh.db < recovery.sql
```

This generates SQL that recreates all readable data. Works even when the DB is severely corrupted. The output SQL can be 30MB+ for large databases — pipe directly to avoid disk space issues.

### Step 4: Swap the database

**Windows file locking:** On Windows, the running gateway process holds an exclusive lock on state.db. You CANNOT rename or replace it while the gateway is running.

Options:
1. Stop the gateway first: `hermes gateway stop`, swap files, restart: `hermes gateway start`
2. Use ATTACH DATABASE to merge data into the live (corrupted) DB without replacing it
3. Write a swap script that runs after gateway restart

**ATTACH DATABASE approach** (merges without replacing):
```python
conn = sqlite3.connect("current_corrupted.db", timeout=30)
c = conn.cursor()
c.execute("ATTACH DATABASE 'fresh_recovered.db' AS fresh")
c.execute("INSERT OR IGNORE INTO sessions SELECT * FROM fresh.sessions")
c.execute("INSERT OR IGNORE INTO messages SELECT * FROM fresh.messages")
c.execute("INSERT INTO messages_fts(messages_fts) VALUES('rebuild')")
conn.commit()
```

### Step 5: Verify

```python
c.execute("PRAGMA integrity_check")  # Should return "ok"
c.execute("SELECT count(*) FROM sessions")
c.execute("SELECT count(*) FROM messages")
```

## Portable Install Structure

```
hermes-portable/
├── launch.bat              # Windows launcher (sets HERMES_HOME, isolation)
├── launch.sh               # Unix launcher
├── scripts/
│   └── setup-windows.ps1   # First-run runtime download
├── src/hermes-agent/       # Source code (may have local patches)
├── data/                   # HERMES_HOME (all persistent state)
│   ├── config.yaml
│   ├── .env
│   ├── memories/
│   ├── skills/
│   ├── sessions/
│   ├── state.db
│   └── ...
└── .cache/
    └── runtimes/windows-x64/  # Downloaded runtimes (Python, Node, git)
        ├── venv/              # Python virtualenv with hermes installed
        ├── python/            # Embedded Python
        ├── node/              # Embedded Node.js
        └── ready.flag         # First-run completion marker
```

## Three-Layer Architecture (CRITICAL for Updates)

The Hermes USB Portable has THREE independent layers that MUST stay version-consistent:

| Layer | Location | Source | Updated by |
|-------|----------|--------|------------|
| Launcher | `launch.bat`, `launch.sh`, `scripts/` | Zip file | Re-extract zip |
| Runtime | `.cache/runtimes/windows-x64/` | GitHub (Python, Node, Git, uv) | `setup-windows.ps1` |
| Source | `src/hermes-agent/` | GitHub (hermes-agent repo) | `setup-windows.ps1` |

**The zip ONLY contains the launcher** — launch.bat, launch.sh, README.md, scripts/. It does NOT contain source code or runtimes. Those are downloaded by `setup-windows.ps1` on first run.

### How First Run Works

1. User double-clicks `launch.bat`
2. Launch.bat checks for `ready.flag` in `.cache/runtimes/windows-x64/`
3. If missing → runs `scripts/setup-windows.ps1 -Root <dir>`
4. setup-windows.ps1 downloads: Python, Node.js, uv, ripgrep, Git, and hermes-agent source from GitHub
5. Creates venv, installs dependencies, writes `ready.flag`
6. Subsequent launches skip setup and run directly

### Update Procedure (Safe)

**Correct way to update portable Hermes:**
```bash
# 1. Back up data (the ONLY thing that matters)
cp data/.env data/config.yaml data/state.db data/auth.json <backup>/
cp -r data/skills/ data/memories/ data/cron/ <backup>/

# 2. Delete old installation completely
rm -rf hermes-portable/

# 3. Extract fresh zip
unzip Hermes-USB-Portable-main.zip -d hermes-portable/

# 4. Restore data
cp <backup>/.env <backup>/config.yaml <backup>/state.db <backup>/auth.json hermes-portable/data/
cp -r <backup>/skills/ <backup>/memories/ <backup>/cron/ hermes-portable/data/

# 5. Launch — setup will re-download runtimes + source
double-click launch.bat
```

### Common Update Mistake (Version Mismatch)

**Symptom:** launch.bat opens then closes immediately, or shows errors.

**Root cause:** Manual partial update — copied `src/` from a newer version while keeping old launcher/runtime. This creates a version mismatch:

```
Launcher: v0.15.1 (old zip)
Runtime:  v0.15.1 (old setup)
Source:   v0.17.0 (manually copied)
→ Import errors, missing modules, behavioral differences
```

**Diagnosis:** Check version consistency:
```bash
# Launcher version — check launch.bat date/modifications
# Runtime version — check what Python/Node was downloaded
# Source version — grep version in src/hermes-agent/hermes_cli/__init__.py
grep "__version__" src/hermes-agent/hermes_cli/__init__.py

# If versions don't match → broken installation
```

**Fix:** Delete and re-extract (see Update Procedure above). Do NOT try to fix individual files — the venv, runtime binaries, and source code are tightly coupled.

### ready.flag

`ready.flag` in `.cache/runtimes/windows-x64/` controls whether setup runs. Deleting it forces re-setup on next launch. Useful when:
- Installation is corrupted and you want a clean re-download
- You want to update runtimes without deleting the entire directory
- Source code was manually modified and you want a fresh copy from GitHub

## Portability Notes

- `launch.bat` sets `HERMES_HOME`, `VIRTUAL_ENV`, `APPDATA` isolation, and `PATH`
- The `.cache/runtimes/` directory is ~600MB (downloaded on first run)
- Source code in `src/hermes-agent/` may have local patches (check `git diff` or grep for known patches)
- Python version differs between installs (3.11 in portable, 3.13 in newer) — venv is NOT portable across Python versions
- **Windows file locking:** `setup-windows.ps1` may fail with "Permission denied" on DLLs if Python or gateway is running from the same installation. Kill running hermes processes before re-setup.
