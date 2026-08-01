---
name: exfiltration-guard
description: Exfiltration Guard pattern from AI-First Business Playbook — scans all outbound content for API keys, secrets, PII before transmission. Blocks and logs.
---

# Exfiltration Guard — Outbound Content Security

Implements the AI-First Business Playbook exfiltration guard pattern:
Scans every outgoing message (Telegram, email, file write, HTTP request) for secrets before transmission.

## Architecture

```
exfiltration-guard/
├── SKILL.md                    # This file
├── references/
│   ├── PATTERNS.md                   # All regex patterns
│   ├── INTEGRATION_GUIDE.md          # How to integrate with bridges
│   └── INCIDENT_RESPONSE.md          # What happens on detection
├── scripts/
│   ├── exfil_guard.py            # Core scanner
│   ├── patterns.py               # Regex patterns
│   ├── telegram_integration.py   # Telegram bridge hook
│   ├── file_write_hook.py        # File write interceptor
│   └── http_hook.py              # HTTP request interceptor
└── templates/
    └── BLOCKED_ALERT.md.template
```

## Patterns to Detect

| Pattern | Example | Severity |
|---------|---------|----------|
| Anthropic API keys | `sk-ant-xxxxx` | CRITICAL |
| OpenAI API keys | `sk-xxxxx` | CRITICAL |
| GitHub tokens | `ghp_xxxxx`, `gho_xxxxx` | CRITICAL |
| Slack tokens | `xoxb-xxxxx`, `xoxa-xxxxx` | CRITICAL |
| AWS keys | `AKIAxxxxxxxxxxxx` | CRITICAL |
| Generic high-entropy | 40+ char hex/base64 | HIGH |
| Email addresses | `user@domain.com` | MEDIUM |
| Phone numbers | `+1-xxx-xxx-xxxx` | MEDIUM |
| Credit cards | `4xxx xxxx xxxx xxxx` | HIGH |
| Private keys | `-----BEGIN PRIVATE KEY-----` | CRITICAL |

## Integration Points (Implemented)

| Component | Hook | Function |
|-----------|------|----------|
| Telegram Bridge | `scripts/telegram_bridge.py:22-30, 74-78` | `check_telegram_message(text)` before send, raises `RuntimeError` if blocked |
| Knowledge Cube Write | `scripts/knowledge_cube.py:140-146` | `scan_outbound(text, source="kc_write:...")` before `add_experience()`, returns blocked status |
| Cron Job Execution | `hermes-agent/cron/scheduler.py:1985-1995` | `scan_outbound(job_content, source="cron_job:...")` before `run_job()`, returns error |
| Goal Executor | `scripts/goal_executor.py` (future) | Scan action commands before subprocess execution |

## Event-Driven Note

All integrations are **event-driven** — no cron polling. Exfiltration check runs inline at the point of outbound action (send, write, execute). Works with `signal_daemon.py` → `event_bus.py` → handler pattern.

## Patterns Detected

| Category | Patterns |
|----------|----------|
| API Keys | Anthropic (sk-ant-), OpenAI (sk-), GitHub (ghp_), Slack (xoxb-, xoxp-), AWS (AKIA), Google OAuth (ya29.), JWT, Bearer tokens |
| PII | Email, Phone (E.164), Credit Card, SSN, Private Keys, SSH Public Keys |
| Exfil Commands | curl/wget with secrets in URL, Authorization headers, POST data |

## Behavior on Detection

1. **BLOCK** — raise RuntimeError / return blocked status
2. **LOG** — audit entry to `logs/audit/audit_YYYYMMDD.jsonl`
3. **ALERT** — (future) notify operator
4. **QUARANTINE** — full content saved to `cache/exfil_quarantine/exfil_<timestamp>_<hash>.json`

## Kill Switch
```env
HERMES_EXFIL_GUARD_ENABLED=true
HERMES_EXFIL_ALERT_ON_BLOCK=true
HERMES_EXFIL_QUARANTINE=true
```