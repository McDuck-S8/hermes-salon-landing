# Cron Job Recovery & Proactive Architecture

## Why Jobs Fail

| Symptom | Cause | Fix |
|---|---|---|
| `402 Insufficient Credits` | OpenRouter out of credits | Switch to opencode_zen or convert to no_agent |
| `401 ModelError: gpt-4o not supported` | Default model in config doesn't match provider | Set explicit model per job (e.g. deepseek-v4-flash-free) |
| `Invalid API response after 3 retries: response time 30.2s` | Provider too slow for tool-calling cron | Convert to no_agent with script |
| Job registered but never runs | Scheduler dead | Check process: `tasklist \| grep python` |
| `last_status: error` without clear message | Scheduler crash on tick | Restart gateway or check .tick.lock |

## Conversion Patterns

### Pattern 1: Python script wrapper (no_agent=True)

For any job that calls system tools (session_search, file I/O, DB queries):

```python
#!/usr/bin/env python3
"""Script wrapper — replaces LLM cron job."""
import sys, os, sqlite3, json
from pathlib import Path
from datetime import datetime

# ... do the work directly without LLM ...
# Print output as cron result
print("[result] ...")
```

Create, then register:
```
hermes cron update <job_id> --script <name>.py --no-agent --prompt "Short description"
```

### Pattern 2: Silent watchdog (no_agent=True)

For health checks / change detection:
```python
# If nothing to report → exit silently
if not changes:
    sys.exit(0)

# If something happened → print report
print(f"[alert] {changes}")
```

The cron scheduler delivers stdout verbatim when no_agent=True.
Empty stdout = silent delivery = no spam.

### Pattern 3: Pure LLM (provider: opencode_zen)

For simple text generation (no tools needed):

```
hermes cron update <job_id> \
  --model '{"provider":"opencode_zen","model":"deepseek-v4-flash-free"}' \
  --prompt "Your prompt here"
```

**Warning:** This only works for prompts that don't need tools (session_search,
read_file, web_search, etc.). For tool-requiring jobs, use Pattern 1.

## Testing a New Provider

Before converting real jobs to a new provider:

```bash
# Create one-shot test
hermes cron create \
  --name test-provider \
  --model '{"provider":"opencode_zen","model":"deepseek-v4-flash-free"}' \
  --prompt "Say hello in exactly 3 words. No formatting." \
  --schedule "2027-01-01T00:00:00" \
  --deliver local

# Trigger immediately
hermes cron run <job_id>

# Wait for scheduler tick (~20-30s), then check
cat cron/output/<job_id>/*.md
```
Expected: clean output like `Hello world here`. If error → provider not
working for cron. Fall back to no_agent.

## Current Provider Status (2026-06-07)

| Provider | Status | Credits | For Cron | Notes |
|---|---|---|---|---|
| OpenCode Zen | ✅ WORKING | Free | ✅ YES (no tools) | deepseek-v4-flash-free model |
| OpenRouter | ❌ DEAD | 0 | ❌ | All jobs get 402 |
| OpenGateway | ❌ DEAD | 0 | ❌ | 404 since June 2026 |
| Groq | ⚠️ UNTESTED | Free | ❓ | Key exists in .env |

## Architecture Layers

For 24/7 autonomous operation:

```
Layer 1: Event Trigger (every 2m, no_agent)
  Detects new pending events → processes immediately
  Silent when idle. Reports when events fire.
  
Layer 2: System Watcher (every 60m, no_agent)
  Health checks: DB sizes, event backlog, error rates
  Produces status report if anything changed
  
Layer 3: Unified Cycle (every 120m, no_agent)
  Knowledge cube → gap analysis → chain reactions
  Memory tree → entity extraction → connections
```

All layers run script-based. No LLM dependency. If the LLM provider
goes down, the autonomous system keeps running.
