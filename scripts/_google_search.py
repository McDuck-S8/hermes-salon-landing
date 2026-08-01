#!/usr/bin/env python3
"""Extract Google search results through proxy - use env inheritance"""
import subprocess, re, html, sys, os

query = sys.argv[1]
encoded = query.replace(' ', '+')
url = f"https://www.google.com/search?q={encoded}&hl=en"

# Don't replace env - inherit parent
result = subprocess.run(
    ["curl", "-s", "--max-time", "12", "-x", "http://127.0.0.1:10806", url],
    capture_output=True, text=True, timeout=20
)
content = result.stdout

if not content or len(content) < 100:
    print(f"EMPTY (len={len(content)})")
    if result.stderr:
        print("STDERR:", result.stderr[:200])
    print("Content:", repr(content[:200]))
    sys.exit(1)

# Find links
links = re.findall(r'href="/url\?q=(https?://[^&\"]+)', content)
out = []
for link in links[:10]:
    decoded = html.unescape(link)
    out.append(f"LINK: {decoded}")

# Find snippets  
snippets = re.findall(r'<div[^>]*style="-webkit-line-clamp[^>]*>(.*?)</div>', content, re.DOTALL)
for s in snippets[:5]:
    text = re.sub(r'<[^>]+>', '', s).strip()
    text = html.unescape(text)
    if len(text) > 30:
        out.append(f"SNIPPET: {text[:400]}")

h3s = re.findall(r'<h3[^>]*>(.*?)</h3>', content, re.DOTALL)
for h in h3s[:5]:
    text = re.sub(r'<[^>]+>', '', h).strip()
    text = html.unescape(text)
    if text:
        out.append(f"H3: {text[:200]}")

if not out:
    out.append(f"UNPARSED (len={len(content)})")
    idx = content.find('<div id="search"')
    if idx > 0:
        out.append(content[idx:idx+2000])
    else:
        out.append(content[:2000])

print('\n'.join(out))
