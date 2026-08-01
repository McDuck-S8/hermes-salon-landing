# Exfiltration Guard — Implementation Notes (Session 2026-07-03)

## Actual Work Done

### 1. Scanner (`scripts/exfil_guard.py`)
- **API Key patterns**: Anthropic (`sk-ant-...`), OpenAI (`sk-...`), GitHub (`ghp_...`), Slack (`xoxb-...`), AWS (`AKIA...`), JWT, Bearer tokens
- **PII patterns**: Email, Phone (E.164), Credit Card, SSN, Private Keys, SSH keys
- **Exfil patterns**: curl/wget with secrets in URLs, Authorization headers
- **Quarantine**: JSON files in `cache/exfil_quarantine/` with full content + metadata
- **Audit log**: JSONL append to `logs/audit/audit_YYYYMMDD.jsonl`

### 2. Integration Points Verified
| Component | Integration | Status |
|-----------|-------------|--------|
| `scripts/telegram_bridge.py` | `check_telegram_message()` before send | ✅ Blocks + quarantines |
| `scripts/knowledge_cube.py` | `scan_outbound()` before `add_experience()` | ✅ Blocks + returns status |
| `hermes-agent/cron/scheduler.py` | `scan_outbound()` on job prompt/script | ✅ Blocks before execution |

### 3. Key Code Patterns

**`scripts/telegram_bridge.py`**:
```python
if _EXFIL_ENABLED:
    exfil_result = check_telegram_message(text)
    if exfil_result.get("blocked"):
        raise RuntimeError(f"Exfiltration blocked: {exfil_result['matches']}. Quarantined: {exfil_result.get('quarantine_id')}")
```

**`scripts/knowledge_cube.py`**:
```python
try:
    from skills.devops.exfiltration_guard.scripts.exfil_guard import scan_outbound
    exfil_result = scan_outbound(text, source=f"kc_write:{source}")
    if exfil_result.get("blocked"):
        return {"status": "blocked", "reason": f"Exfiltration detected: {exfil_result['matches']}", "quarantine_id": exfil_result.get("quarantine_id")}
except ImportError:
    pass
```

**`hermes-agent/cron/scheduler.py`**:
```python
job_content = job.get("prompt", "") or job.get("script", "")
if job_content:
    from exfil_guard import scan_outbound
    exfil_result = scan_outbound(job_content, source=f"cron_job:{job_id}")
    if exfil_result.get("blocked"):
        return False, "", "", err
```

### 4. Patterns File (`scripts/patterns.py`)
- Centralized compiled regex patterns
- Categories: API_KEY_PATTERNS, PII_PATTERNS, EXFIL_PATTERNS
- Easy to extend/maintain

### 5. Next Steps
1. Add `write_file` tool wrapper hook (currently no direct integration)
2. Add HTTP client hook for outbound API calls
3. Implement alert to operator (Telegram/email) on detection
4. Add allowlist for legitimate secrets (test keys, CI tokens)
5. Schedule periodic quarantine cleanup