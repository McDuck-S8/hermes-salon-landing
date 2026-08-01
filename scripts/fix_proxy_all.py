#!/usr/bin/env python3
"""Fix all Telegram API calls to use HTTP proxy."""
import os
import re

PROXY = "http://127.0.0.1:10809"
SCRIPTS_DIR = "D:/Portable_Soft/hermes/scripts"

def fix_urllib_proxy(content):
    """Add proxy handler to urllib calls."""
    # Pattern: urllib.request.urlopen(req, timeout=30)
    # Need to add proxy handler
    if "urllib.request.urlopen" in content and "proxy" not in content.lower():
        # Add proxy handler at top of file
        proxy_code = f'''
# Proxy configuration
proxy_handler = urllib.request.ProxyHandler({{
    'http': '{PROXY}',
    'https': '{PROXY}'
}})
opener = urllib.request.build_opener(proxy_handler)
'''
        # Insert after imports
        import_end = content.find('\n\n')
        if import_end > 0:
            content = content[:import_end] + proxy_code + content[import_end:]
            # Replace urlopen with opener
            content = content.replace('urllib.request.urlopen(', 'opener.open(')
    return content

def fix_curl_proxy(content):
    """Add --proxy to curl calls."""
    # Pattern: ["curl", "-s", "--proxy", "http://127.0.0.1:10809", "https://api.telegram.org
    if 'curl' in content and 'api.telegram.org' in content:
        content = content.replace(
            '["curl", "-s", "--proxy", "http://127.0.0.1:10809", "https://api.telegram.org',
            f'["curl", "-s", "--proxy", "{PROXY}", "https://api.telegram.org'
        )
        content = content.replace(
            '["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",\\n             "--connect-timeout", "5", "https://api.telegram.org',
            f'["curl", "-s", "-o", "/dev/null", "-w", "%{{http_code}}",\\n             "--connect-timeout", "5", "--proxy", "{PROXY}", "https://api.telegram.org'
        )
    return content

def fix_httpx_proxy(content):
    """Add proxy to httpx calls."""
    if 'httpx' in content and 'api.telegram.org' in content:
        content = content.replace(
            'httpx.get("https://api.telegram.org", proxy="http://127.0.0.1:10809"", proxy="http://127.0.0.1:10809"',
            f'httpx.get("https://api.telegram.org", proxy="http://127.0.0.1:10809"", proxy="http://127.0.0.1:10809"", proxy="{PROXY}"'
        )
        content = content.replace(
            'httpx.post("https://api.telegram.org", proxy="http://127.0.0.1:10809"", proxy="http://127.0.0.1:10809"',
            f'httpx.post("https://api.telegram.org", proxy="http://127.0.0.1:10809"", proxy="http://127.0.0.1:10809"", proxy="{PROXY}"'
        )
    return content

# Process all files
fixed = []
for root, dirs, files in os.walk(SCRIPTS_DIR):
    for f in files:
        if not f.endswith('.py'):
            continue
        path = os.path.join(root, f)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                content = fh.read()
            
            original = content
            content = fix_urllib_proxy(content)
            content = fix_curl_proxy(content)
            content = fix_httpx_proxy(content)
            
            if content != original:
                with open(path, 'w', encoding='utf-8') as fh:
                    fh.write(content)
                fixed.append(f)
                print(f"Fixed: {f}")
        except Exception as e:
            print(f"Error {f}: {e}")

print(f"\nTotal fixed: {len(fixed)}")
