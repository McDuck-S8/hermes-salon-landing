#!/usr/bin/env python3
"""Extract YouTube video description from page HTML via ytInitialData.

Works when youtube-transcript-api and yt-dlp are blocked (RequestBlocked).
Parses the attributedDescription field from the YouTube page's ytInitialData JSON.

Usage:
    python yt_extract_desc.py VIDEO_ID [proxy_url]
    
    If proxy_url omitted, uses HTTP_PROXY/HTTPS_PROXY env vars or no proxy.
    Proxy format: http://127.0.0.1:10806

Output: video description text to stdout (includes timestamps, links, repo lists).
Returns empty and exit code 1 on failure.
"""
import re, json, sys, os, subprocess

def extract_description(video_id: str, proxy_url: str = None) -> str:
    """Download YouTube page and extract attributedDescription from ytInitialData."""
    env = os.environ.copy()
    if proxy_url:
        env["HTTP_PROXY"] = proxy_url
        env["HTTPS_PROXY"] = proxy_url
        env["http_proxy"] = proxy_url
        env["https_proxy"] = proxy_url
        # Remove no-proxy that might interfere
        env.pop("no_proxy", None)
        env.pop("NO_PROXY", None)
    
    # Retry loop for intermittent SSL errors (exit 35)
    for attempt in range(5):
        try:
            r = subprocess.run(
                ["curl", "-s", "--max-time", "15",
                 "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                 f"https://www.youtube.com/watch?v={video_id}"],
                capture_output=True, text=True, timeout=20, env=env
            )
            if r.returncode == 0 and len(r.stdout) > 1000:
                break
        except Exception:
            pass
        if attempt < 4:
            import time
            time.sleep(2)
    else:
        return ""
    
    content = r.stdout
    m = re.search(r'ytInitialData\s*=\s*(\{.+?\});', content, re.DOTALL)
    if not m:
        return ""
    
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return ""
    
    raw = json.dumps(data, ensure_ascii=False)
    idx = raw.find("attributedDescription")
    if idx == -1:
        return ""
    
    chunk = raw[idx:idx+20000]
    start_idx = chunk.find('"content":"')
    if start_idx == -1:
        return ""
    
    start_idx += len('"content":"')
    
    # Find end of content - look for "," that starts next JSON key
    search_start = start_idx
    while True:
        end_idx = chunk.find('",\n', search_start)
        if end_idx == -1:
            end_idx = chunk.find('","', search_start)
        if end_idx == -1:
            break
        
        remainder = chunk[end_idx+1:end_idx+30].strip()
        if remainder.startswith('"') and len(remainder) > 2 and remainder[1].isalpha():
            desc = chunk[start_idx:end_idx]
            break
        search_start = end_idx + 3
    
    if "desc" not in dir():
        return ""
    
    # Unescape
    desc = desc.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
    desc = desc.replace('\\xa0', ' ')
    desc = re.sub(r'\\u[0-9a-fA-F]{4}', lambda m: chr(int(m.group(0)[2:], 16)), desc)
    
    return desc

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python yt_extract_desc.py VIDEO_ID [proxy_url]", file=sys.stderr)
        sys.exit(1)
    
    video_id = sys.argv[1]
    proxy = sys.argv[2] if len(sys.argv) > 2 else None
    
    desc = extract_description(video_id, proxy)
    if desc:
        print(desc)
    else:
        print(f"ERROR: Could not extract description for {video_id}", file=sys.stderr)
        sys.exit(1)
