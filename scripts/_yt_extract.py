"""Extract YouTube video description via curl + proxy."""
import subprocess, sys, re, json, html

video_id = sys.argv[1]
proxy = "http://127.0.0.1:10806"

env = {"HTTP_PROXY": proxy, "HTTPS_PROXY": proxy, "PATH": "C:/Windows/system32;C:/Program Files/Git/usr/bin"}

try:
    result = subprocess.run(
        ["curl", "-s", "--max-time", "15", f"https://www.youtube.com/watch?v={video_id}"],
        capture_output=True, text=True, timeout=20, env=env
    )
    content = result.stdout
except Exception as e:
    print(f"CURL ERROR: {e}")
    sys.exit(1)

# Extract ytInitialData
m = re.search(r'ytInitialData\s*=\s*(\{.+?\});', content, re.DOTALL)
if m:
    try:
        data = json.loads(m.group(1))
        # Try to find description text
        raw = json.dumps(data, ensure_ascii=False)
        # Find the description snippet
        desc_matches = re.findall(r'"description":{"simpleText":"([^"]+)"}', raw)
        if desc_matches:
            for d in desc_matches:
                print("DESC:", html.unescape(d)[:3000])
        else:
            # Try runs format
            desc_matches2 = re.findall(r'"runs":\[{"text":"([^"]+)"}\]', raw)
            if desc_matches2:
                for d in desc_matches2:
                    print("DESC:", html.unescape(d)[:3000])
            else:
                # Try to dump a section around "description"
                idx = raw.find('"description"')
                if idx > 0:
                    print(raw[idx:idx+2000])
    except Exception as e:
        print(f"PARSE ERROR: {e}")
else:
    print("NO ytInitialData found")
    # Fallback: meta description
    m2 = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', content)
    if m2:
        print("META:", html.unescape(m2.group(1))[:2000])
    # Also print title
    m3 = re.search(r'<title>(.+?)</title>', content)
    if m3:
        print("TITLE:", html.unescape(m3.group(1)))
    print(f"\nContent length: {len(content)} chars")
    # Print first 2000 chars
    print("RAW START:", content[:2000])
