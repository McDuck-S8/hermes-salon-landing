"""Extract YouTube video description - simplest possible approach."""
import re, json, sys, os

html_dir = sys.argv[1]  # directory containing yt_*.html
out_dir = sys.argv[2]   # output directory

os.makedirs(out_dir, exist_ok=True)

for fname in sorted(os.listdir(html_dir)):
    if not fname.startswith('yt_') or not fname.endswith('.html'):
        continue
    html_path = os.path.join(html_dir, fname)
    name = fname[3:-5]  # 'yt_VIDEOID.html' -> 'VIDEOID'
    
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
    except Exception as e:
        print(f"{name}: JSON parse error: {e}")
        continue
    
    # Serialize and search for attributedDescription  
    raw = json.dumps(data, ensure_ascii=False)
    idx = raw.find('"attributedDescription"')
    if idx < 0:
        print(f"{name}: NO attributedDescription")
        continue
    
    chunk = raw[idx:idx+20000]
    # Try both with and without space after colon
    start = chunk.find('"content": "')
    if start < 0:
        start = chunk.find('"content":"')
    if start < 0:
        print(f"{name}: NO content field")
        continue
    
    start = chunk.index('"', start + len('"content": ')) + 1 if '"content": "' in chunk[start:start+50] else start + len('"content":"')
    
    # Find the end: next "," that leads into a key name
    # Strategy: find all "," positions and check what follows
    end = -1
    search_pos = start
    while search_pos < len(chunk):
        pos = chunk.find('",\\n', search_pos)
        if pos < 0:
            pos = chunk.find('","', search_pos)
        if pos < 0:
            break
        
        after = chunk[pos+1:pos+10].replace('\n', ' ').replace('\r', ' ').strip()
        # If it looks like a key: "word":
        if after.startswith('"') and len(after) > 2 and (after[1].isalpha() or after[1] == '_'):
            end = pos
            break
        search_pos = pos + 1
    
    if end < 0:
        print(f"{name}: NO end delimiter found")
        continue
    
    desc = chunk[start:end]
    # Unescape
    desc = desc.replace('\\n', '\n').replace('\\t', '\t')
    desc = desc.replace('\\"', '"').replace("\\'", "'")
    desc = desc.replace('\\xa0', ' ')
    # Unescape unicode
    desc = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), desc)
    
    out_path = os.path.join(out_dir, f"{name}.txt")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(desc)
    
    print(f"{name}: OK ({len(desc)} chars, first 80: {desc[:80].strip()})")
