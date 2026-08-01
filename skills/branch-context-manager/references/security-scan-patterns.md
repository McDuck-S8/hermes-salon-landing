# Security Scan Patterns for Third-Party Code

When installing npm packages, GitHub repos, or pip packages — scan source FIRST.

## Quick Scan Checklist

```python
import re

SUSPICIOUS_PATTERNS = {
    'eval/exec': r'eval\s*\(|exec\s*\(|compile\s*\(',
    'env_exfil': r'process\.env|os\.environ|getenv',
    'network_calls': r'requests\.(get|post)|fetch\s*\(|http\.request|axios|urllib',
    'obfuscated': r'atob\s*\(|btoa\s*\(|Buffer\.from\s*\(.+base64|\\x[0-9a-f]{2}',
    'suspicious_urls': r'https?://[^\s"]+\.(ru|cn|tk|top|xyz|buzz)|pastebin|ngrok|tunnel',
    'shell_exec': r'child_process|subprocess|os\.system|os\.popen|spawn\s*\(',
    'dns_exfil': r'DNS|dns\.resolve|nslookup|dig\s+',
    'hardcoded_ips': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
    'crypto_mining': r'coinhive|crypto|miner|stratum\+tcp',
    'data_exfil': r'FormData|XMLHttpRequest|navigator\.sendBeacon',
}

def scan_file(filepath, content):
    findings = []
    for name, pattern in SUSPICIOUS_PATTERNS.items():
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            findings.append({'type': name, 'count': len(matches), 'file': filepath})
    return findings
```

## Scan Process

1. **Download source** (don't install yet) — `npm pack`, `git clone --depth=1`, `pip download --no-deps`
2. **Extract and scan** — run pattern scan on all .js/.ts/.py files
3. **Review findings** — some are legitimate (env reading for config, fetch for API calls)
4. **Red flags**: hardcoded IPs, base64 obfuscation, data exfiltration patterns, crypto mining
5. **If clean** — proceed with installation
6. **If suspicious** — report to user with specific files and line numbers

## Real-World Example (xray-browser-manager)

Found in package.json:
- "postinstall": "node scripts/postinstall.js" → postinstall scripts can run arbitrary code
- Registry: https://npm.pkg.github.com (not npmjs.com)

Found in source:
- eval() usage in environment.ts
- fetch() calls to external APIs
- hardcoded API URLs

Result: Blocked installation, reported to user.

## Quick Terminal Scan

```bash
# npm package
npm pack <package> && tar -xf *.tgz
grep -rn "eval\|exec\|atob\|coinhive\|subprocess" package/

# GitHub repo
git clone --depth=1 <url> /tmp/scan-target
grep -rn "eval\|exec\|atob\|coinhive\|subprocess" /tmp/scan-target/

# pip package
pip download --no-deps -d /tmp/scan-target <package>
# Extract and grep similarly
```
