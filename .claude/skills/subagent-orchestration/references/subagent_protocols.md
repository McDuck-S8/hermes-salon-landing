# Subagent Protocols — Reference Documentation

## Protocol Overview

This document defines the protocols for subagent orchestration in Hermes.

## 1. Delegation Protocol

### Request Format
```json
{
  "subagent_id": "sub_abc123",
  "task_type": "search_ozon",
  "params": {
    "query": "светодиодные лампы",
    "limit": 10,
    "sort": "price"
  },
  "context": {
    "proxy": "socks5://127.0.0.1:10806",
    "env_vars": {
      "HERMES_HOME": "D:/Portable_Soft/hermes",
      "HTTP_PROXY": "socks5://127.0.0.1:10806",
      "HTTPS_PROXY": "socks5://127.0.0.1:10806"
    },
    "tools": ["scripts/web_automation.py", "scripts/config_loader.py"],
    "permissions": {
      "network": true,
      "browser": true,
      "file_read": true,
      "file_write": false
    }
  },
  "instructions": "Use web_automation.search_and_extract...",
  "retry_policy": {
    "max_retries": 3,
    "backoff_base": 2,
    "retry_on": ["timeout", "proxy_error", "rate_limit"]
  },
  "output_format": {
    "success": true,
    "data": [],
    "error": null,
    "metadata": {}
  }
}
```

### Response Format
```json
{
  "success": true,
  "data": [
    {
      "title": "Светодиодная лампа 10W",
      "price": 150,
      "rating": 4.5,
      "reviewsCount": 123,
      "link": "https://www.ozon.ru/product/..."
    }
  ],
  "error": null,
  "metadata": {
    "subagent_id": "sub_abc123",
    "duration_ms": 45000,
    "retries": 0,
    "proxy_used": "socks5://127.0.0.1:10806"
  }
}
```

## 2. Heartbeat Protocol

Subagents MUST send heartbeats every 10 seconds while running.

### Heartbeat Message
```json
{
  "subagent_id": "sub_abc123",
  "status": "running",
  "timestamp": "2026-07-31T10:00:30.123Z",
  "progress": 0.45
}
```

### Timeout Handling
- No heartbeat for 300 seconds → mark as stalled
- Monitor may trigger retry or cleanup

## 3. Retry Protocol

### Retry Conditions
| Condition | Retry? | Max Retries |
|-----------|--------|-------------|
| Timeout | Yes | 3 |
| Proxy connection error | Yes | 3 |
| Rate limit (429) | Yes | 2 |
| Browser crash | Yes | 2 |
| Network error | Yes | 3 |
| 403 Forbidden | No | 0 |
| Invalid params | No | 0 |

### Backoff Strategy
```
Attempt 1: wait 2^1 = 2 seconds
Attempt 2: wait 2^2 = 4 seconds  
Attempt 3: wait 2^3 = 8 seconds
```

## 4. Logging Protocol

All subagent activities logged to Feedback Store (SQLite).

### Log Entry Schema
```sql
CREATE TABLE feedback (
  id INTEGER PRIMARY KEY,
  skill TEXT,           -- 'subagent_orchestration'
  timestamp TEXT,       -- ISO format
  result TEXT,          -- JSON payload
  tags TEXT,            -- JSON array
  source TEXT           -- 'subagent_orchestrator'
)
```

### Event Types
- `subagent_delegated` — Task assigned
- `subagent_completed` — Success
- `subagent_failed` — All retries exhausted
- `subagent_retry` — Retry attempt

## 5. Context Injection Protocol

### Required Environment Variables
```
HERMES_HOME=D:/Portable_Soft/hermes
HTTP_PROXY=socks5://127.0.0.1:10806
HTTPS_PROXY=socks5://127.0.0.1:10806
PLAYWRIGHT_BROWSERS_PATH=ms-playwright
PYTHONPATH=D:/Portable_Soft/hermes
```

### Required Tools Available
- `scripts/web_automation.py` — Browser + HTTP automation
- `scripts/config_loader.py` — Site config loading

### Permissions Matrix
| Permission | Granted | Notes |
|------------|---------|-------|
| Network (HTTP) | Yes | Through proxy only |
| Browser (Playwright) | Yes | Headless by default |
| File Read | Yes | Configs, references |
| File Write | No | Security |
| Subprocess | No | Security |

## 6. Task Templates Registry

### Built-in Templates
| Task Type | Tool | Method | Default Params |
|-----------|------|--------|----------------|
| search_ozon | web_automation | search_and_extract | site=ozon, limit=20, sort=price, pages=3 |
| search_wb | web_automation | search_and_extract | site=wb, limit=20, sort=price, pages=3 |
| get_product_details | web_automation | get_product_details | {} |
| search_github | web_automation | execute_site_action | action=search_repos |

### Adding Custom Templates
```python
orchestrator.task_templates["custom_task"] = {
    "tool": "web_automation",
    "method": "custom_method",
    "default_params": {},
    "timeout": 60,
    "max_retries": 2,
    "backoff_base": 2,
}
```

## 7. Monitoring API

### Get Stats
```python
monitor.get_stats()
# Returns: {"total": 10, "running": 2, "completed": 7, "failed": 1, ...}
```

### Get Running Subagents
```python
monitor.get_running()
# Returns list of SubagentInfo with RUNNING status
```

### Get Stalled Subagents
```python
monitor.get_stalled(threshold_seconds=60)
# Returns subagents without heartbeat
```

## 8. Error Handling

### Error Categories
| Category | Examples | Handling |
|----------|----------|----------|
| Transient | Timeout, network error, proxy error | Retry with backoff |
| Rate limit | 429, 403 (temp) | Wait longer, retry |
| Permanent | 403 (perm), 404, invalid params | Fail immediately |
| Infrastructure | Browser crash, OOM | Restart browser, retry |

### Error Response Format
```json
{
  "success": false,
  "data": null,
  "error": "Timeout after 120s",
  "metadata": {
    "subagent_id": "sub_abc123",
    "duration_ms": 120000,
    "retries": 3,
    "proxy_used": "socks5://127.0.0.1:10806"
  }
}
```

---

**Version**: 1.0  
**Created**: 2026-07-31  
**Author**: Hermes Agent