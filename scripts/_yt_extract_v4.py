"""Extract YouTube video description - simpler approach using regex."""
import re, json, sys, os

html_dir = sys.argv[1]
out_dir = sys.argv[2]
os.makedirs(out_dir, exist_ok=True)

for fname in sorted(os.listdir(html_dir)):
    if not fname.startswith('yt_') or not fname.endswith('.html'):
        continue
    html_path = os.path.join(html_dir, fname)
    name = fname[3:-5]
    
    size = os.path.getsize(html_path)
    if size < 100:
        print(f"{name}: EMPTY ({size}b)")
        continue
    
    with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
        c = f.read()
    
    m = re.search(r'ytInitialData\s*=\s*(\{.+?\});', c, re.DOTALL)
    if not m:
        print(f"{name}: NO ytInitialData")
        continue
    
    try:
        data = json.loads(m.group(1))
    except:
        print(f"{name}: JSON error")
        continue
    
    raw = json.dumps(data, ensure_ascii=False)
    idx = raw.find('"attributedDescription"')
    if idx < 0:
        print(f"{name}: NO attributedDescription")
        continue
    
    chunk = raw[idx:idx+20000]
    
    # Use regex to extract content field value
    match = re.search(r'"content":\s*"((?:[^"]|\\")*)"', chunk)
    if match:
        desc = match.group(1)
    else:
        print(f"{name}: NO regex match")
        continue
    
    if len(desc) < 10:
        print(f"{name}: too short ({len(desc)})")
        continue
    
    # Unescape
    desc = desc.replace('\\n', '\n').replace('\\t', '\t')
    desc = desc.replace('\\"', '"').replace("\\'", "'")
    desc = desc.replace('\\xa0', ' ')
    desc = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), desc)
    
    out_path = os.path.join(out_dir, f"{name}.txt")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(desc)
    print(f"{name}: OK ({len(desc)} chars)")
