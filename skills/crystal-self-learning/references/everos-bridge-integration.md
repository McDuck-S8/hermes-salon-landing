# EverOS Bridge Integration — Investigation Pattern

Used when user says "Я ЭТО УСТАНОВИЛ https://github.com/EverMind-AI/EverOS НО ОНО ПОЧЕМУ ТО НЕ ЗАПУСКАЕТСЯ"

## Step 1: Locate the installation

Search in order:

```bash
# 1. Under projects/ (if cloned with git)
ls -la D:/Portable_Soft/hermes/projects/EverOS/

# 2. User home (pip config directory)
ls -la /c/Users/<user>/.everos/

# 3. pip package (Python library, not the server itself)
pip show everos

# 4. Installed binary
find /d -name "everos.exe" -path "*/.venv/*" 2>/dev/null
```

The EverOS server is a **git clone** in `projects/EverOS`. The `everos` pip package is just the API client library (v0.4.0, from `evermemos/everos-python`).

## Step 2: Check if it's running

```bash
curl -s http://127.0.0.1:<port>/health
```

Default port: 8111 (from `.env: EVEROS_API__PORT=8111`).

Expected: `{"status":"ok"}`

## Step 3: Read the config

```bash
cat projects/EverOS/.env
```

Key config fields:
- `EVEROS_LLM__MODEL` — LLM model (must support function calling)
- `EVEROS_LLM__API_KEY` — API key for LLM provider
- `EVEROS_LLM__BASE_URL` — API endpoint
- `EVEROS_EMBEDDING__MODEL` — embedding model
- `EVEROS_EMBEDDING__BASE_URL` — embedding API endpoint
- `EVEROS_MEMORY__ROOT` — where memory data lives (~/.everos)
- `EVEROS_API__PORT` — server port

## Step 4: Start the server

```bash
cd projects/EverOS
.venv/Scripts/python.exe run_server.py
```

The `run_server.py` launcher:
- Adds `src/` to sys.path
- Creates app from `everos.entrypoints.api.app.create_app()`
- Runs uvicorn on configured host/port

## Step 5: Verify health after start

```bash
curl -s http://127.0.0.1:8111/health
```

## Step 6: Update bridge task

EverOS bridge task in `crystal_tasks.json` tends to go stale. After verifying:

1. Check the task context field — it may say "blocked: LLM doesn't support function calling"
2. If the actual .env has Mistral/OpenAI (which support function calling), the blocker is resolved
3. Update task status to "pending" or remove the stale context

```python
import json
tasks = json.load(open("cache/crystal_tasks.json"))
for t in tasks:
    if t["id"] == "everos_integration_20260614":
        t["status"] = "pending"
        t["context"] += "\n\n⚠ CONFIG UPDATED: .env now uses Mistral API (supports function calling). Health: ok."
json.dump(tasks, open("cache/crystal_tasks.json", "w"), indent=2, ensure_ascii=False)
```

## Step 7: Integrate with crystal

Since crystal's will() reads bridge tasks but does NOT execute them (see pitfall #22), the effective integration path is:

1. Do the work yourself (verify, configure, launch)
2. Record the result to KC via `on_task_complete()` with domain "everos" and relevant tags
3. Update the bridge task as documentation only (crystal won't act on it, but the info is there for reference)

The crystal learns from KC growth — fresh entries in an unstudied domain will trigger its conscience() on the next cycle.
