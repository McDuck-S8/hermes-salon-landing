# Local Code Audit Before Dependency Install

When a user asks to install dependencies (npm install, pip install) or run unfamiliar code, FIRST scan the source for malicious patterns. This is a QUICK local audit, not a full forensic investigation.

## When to Use
- User says "install X" or "run this project"
- First time running a project from a new source
- User explicitly asks "check for malicious code" or "проверь на зловредный инжект"

## Scan Patterns (regex-based, run in execute_code)

```python
import os, re

target = r"D:\path\to\project"

patterns = {
    'eval/exec': r'\b(eval|exec)\s*\(',
    'child_process': r'(child_process|spawn|execFile|execSync)',
    'env_exfil': r'(process\.env|\.env|ENCRYPTION_KEY|API_KEY|SECRET|TOKEN|PASSWORD)',
    'network_calls': r'(fetch|axios|request|http\.get|https\.get|XMLHttpRequest)',
    'crypto_mining': r'(crypto\.createHash|bitcoin|ethereum|miner|hashrate)',
    'fs_write': r'(fs\.write|fs\.append|writeFile|appendFile)',
    'base64_decode': r'(atob|Buffer\.from.*base64|base64)',
    'obfuscated': r'(\\\\x[0-9a-f]{2}|\\\\u[0-9a-f]{4}|String\.fromCharCode)',
    'shell_exec': r'(shell|cmd|powershell|bash|/bin/sh)',
    'dns_exfil': r'(dns\.resolve|dns\.lookup|resolve4)',
    'websocket': r'(WebSocket|ws://|wss://)',
    'post_requests': r'(method.*POST|\.post\(|axios\.post)',
    'hardcoded_ips': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
    'suspicious_urls': r'(pastebin|ngrok|serveo|localtunnel|webhook\.site)',
    'require_dynamic': r'(require\s*\(\s*[^"\'a-z]|require\s*\(\s*`)',
}
```

## How to Interpret Results

**NORMAL for web servers/apps:**
- `env_exfil` — reading config from process.env is standard
- `network_calls` — fetch/axios for API calls is the purpose
- `post_requests` — POST methods on Express routes
- `eval/exec` — `db.exec()` is SQLite, NOT JavaScript eval
- `hardcoded_ips` — `127.0.0.1` in tests is localhost, safe

**RED FLAGS (investigate further):**
- `obfuscated` — encoded strings hiding real intent
- `shell_exec` — spawning shells (unless it's a dev tool)
- `dns_exfil` — DNS lookups for data exfiltration
- `suspicious_urls` — pastebin/ngrok/webhook.site = data exfil
- `require_dynamic` — loading modules by variable name
- `base64_decode` — decoding hidden payloads
- `crypto_mining` — actual mining, not just hashing

## Reporting
- List all findings grouped by severity
- For normal patterns, explain WHY they're normal (e.g., "db.exec() is SQLite, not JS eval")
- For red flags, show the actual code line for manual review
- Verdict: CLEAN / SUSPICIOUS / MALICIOUS

## Example Verdict Format
```
CLEAN. Scanned 47 files. All findings are legitimate:
- env_exfil: standard config reading (process.env.PORT, ENCRYPTION_KEY)
- network_calls: API proxy to Google/Cloudflare (this IS the app's purpose)
- db.exec(): SQLite table creation, not JS eval
- 127.0.0.1: localhost in test files
No obfuscation, no shell exec, no data exfil, no suspicious URLs.
```
