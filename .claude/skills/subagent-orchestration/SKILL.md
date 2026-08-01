---
name: subagent-orchestration
description: "Orchestrates subagents with proper context, proxy, and error handling. Defines what resources subagents receive, step-by-step instructions, result format, and retry logic."
trigger: "When delegating tasks to subagents, especially for web automation, marketplace scraping, or any task requiring external access."
usage: subagent-orchestration
argument-hint: "[delegate|monitor|retry] [task_type] [params]"
allowed-tools:
  - Bash(python scripts/subagent_orchestrator.py *)
  - Read(*)
  - Write(*)
---

# Subagent Orchestration — Subagent Management Skill

Manages subagent delegation with proper context injection, proxy configuration, error handling, and result formatting.

## Architecture

```
subagent-orchestration/
├── SKILL.md                    # This file
├── scripts/
│   ├── subagent_orchestrator.py  # Main orchestrator
│   ├── subagent_context.py       # Context builder
│   └── subagent_monitor.py       # Monitoring & retries
└── references/
    └── subagent_protocols.md     # Protocol definitions
```

## Quick Start

```bash
# Delegate a task to subagent
python scripts/subagent_orchestrator.py delegate --task "search_ozon" --params '{"query": "светодиодные лампы", "limit": 10}'

# Monitor running subagents
python scripts/subagent_orchestrator.py monitor

# Retry failed subagent
python scripts/subagent_orchestrator.py retry --id <subagent_id>
```

## Subagent Context Injection

Every subagent receives:

```python
SUBAGENT_CONTEXT = {
    "proxy": "socks5://127.0.0.1:10806",        # v2rayN proxy
    "env_vars": {
        "HERMES_HOME": "D:/Portable_Soft/hermes",
        "HTTP_PROXY": "socks5://127.0.0.1:10806",
        "HTTPS_PROXY": "socks5://127.0.0.1:10806",
        "PLAYWRIGHT_BROWSERS_PATH": "ms-playwright",
    },
    "tools": [
        "scripts/web_automation.py",
        "scripts/config_loader.py",
    ],
    "permissions": {
        "network": True,      # Can make HTTP requests
        "browser": True,      # Can launch Playwright
        "file_read": True,    # Can read configs
        "file_write": False,  # Cannot write files (security)
    },
    "instructions": "Use web_automation.search_and_extract for marketplace tasks. Always use proxy. Return JSON with success, data, error fields.",
}
```

## Task Templates

### Marketplace Search Task

```python
TASK_TEMPLATES = {
    "search_ozon": {
        "tool": "web_automation",
        "method": "search_and_extract",
        "params": ["query", "limit", "sort", "pages"],
        "timeout": 120,
        "retries": 3,
        "backoff": 2,  # exponential: 2s, 4s, 8s
    },
    "search_wb": {
        "tool": "web_automation", 
        "method": "search_and_extract",
        "params": ["query", "limit", "sort", "pages"],
        "timeout": 120,
        "retries": 3,
        "backoff": 2,
    },
    "get_product_details": {
        "tool": "web_automation",
        "method": "get_product_details",
        "params": ["url"],
        "timeout": 60,
        "retries": 2,
    },
}
```

## Result Format

```json
{
  "success": true,
  "data": [...],
  "error": null,
  "metadata": {
    "subagent_id": "sub_123",
    "task": "search_ozon",
    "duration_ms": 45000,
    "retries": 0,
    "proxy_used": "socks5://127.0.0.1:10806"
  }
}
```

## Error Handling & Retries

| Error Type | Action | Max Retries | Backoff |
|------------|--------|-------------|---------|
| Timeout | Retry with longer timeout | 3 | 2^n seconds |
| Proxy failure | Switch proxy / retry | 3 | 2^n seconds |
| 403/429 (rate limit) | Wait longer, retry | 2 | 5s, 15s |
| Browser crash | Restart browser, retry | 2 | 3s |
| Network error | Retry | 3 | 2^n seconds |

## Monitoring

```python
# Check subagent status
{
  "subagent_id": "sub_123",
  "status": "running|completed|failed|retrying",
  "progress": 0.45,
  "started_at": "2026-07-31T10:00:00",
  "last_heartbeat": "2026-07-31T10:00:30",
  "logs": [...]
}
```

## Feedback Store Logging

All subagent activities logged:

```json
{
  "timestamp": "2026-07-31T10:00:00",
  "event": "subagent_delegated|subagent_completed|subagent_failed|subagent_retry",
  "subagent_id": "sub_123",
  "task": "search_ozon",
  "params": {"query": "светодиодные лампы"},
  "result": {"success": true, "items_found": 10},
  "duration_ms": 45000
}
```

## Verification

```bash
# Verify skill
python scripts/subagent_verifier.py .claude/skills/subagent-orchestration/SKILL.md --strict

# Compliance check
python scripts/compliance_checker.py --check
```

## Core Mental Models

1. **Principal Obligation** — The orchestrator (principal) must provide subagents with all necessary context, tools, and permissions before delegation
2. **Context Isolation** — Each subagent gets its own isolated context with explicit permissions; no shared mutable state
3. **Graceful Degradation** — HTTP API first → Browser with human-like behavior → Error with clear diagnostics
4. **Observability First** — Every action logged, heartbeats monitored, retries tracked, results auditable
5. **Retry with Intelligence** — Exponential backoff, retry only on transient errors, permanent failures fail fast

## Key Frameworks & Decision Rules

| Framework | Purpose | When to Apply |
|-----------|---------|---------------|
| **Principal Obligation** | Orchestrator provides all context | Every delegation |
| **Context Isolation** | No shared state between subagents | Every delegation |
| **Graceful Degradation** | API → Browser → Error | Every execution |
| **Observability First** | Log everything, monitor heartbeats | Continuous |
| **Retry with Intelligence** | Exponential backoff, transient-only | On failure |

## Topic Index

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Subagent Context Injection](#subagent-context-injection)
- [Task Templates](#task-templates)
- [Result Format](#result-format)
- [Error Handling & Retries](#error-handling--retries)
- [Monitoring](#monitoring)
- [Feedback Store Logging](#feedback-store-logging)
- [Verification](#verification)
- [Core Mental Models](#core-mental-models)
- [Key Frameworks & Decision Rules](#key-frameworks--decision-rules)
- [Topic Index](#topic-index)

## Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Delegate without proxy/context | Inject full context + proxy |
| Share state between subagents | Isolate each subagent |
| Retry on permanent errors (403) | Fail fast on permanent errors |
| Skip logging/heartbeats | Log everything, monitor continuously |
| Hardcode timeouts | Use configurable timeouts with defaults |
| Ignore subagent timeouts | Monitor heartbeats, handle stalls |
| Write files from subagents | Read-only, return data via JSON |
| Single retry strategy | Exponential backoff + error classification |

---

**Version**: 1.0  
**Created**: 2026-07-31  
**Author**: Hermes Agent