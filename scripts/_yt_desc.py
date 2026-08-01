"""Extract YouTube description from ytInitialData"""
import re, json, sys

filepath = sys.argv[1]
with open(filepath, 'r', encoding='utf-8') as f:
    c = f.read()

# Method 1: shortDescription in ytInitialData
m = re.search(r'shortDescription":"([^"]+)"', c)
if m:
    print("SHORT_DESC:", m.group(1)[:1000])
    sys.exit(0)

# Method 2: Direct regex for description in ytInitialData  
m = re.search(r'ytInitialData\s*=\s*(\{.+?\});', c, re.DOTALL)
if not m:
    print("NO ytInitialData")
    sys.exit(1)

data = json.loads(m.group(1))
raw = json.dumps(data, ensure_ascii=False)

# Find videoSecondaryInfoRenderer  
idx = raw.find("videoSecondaryInfoRenderer")
if idx == -1:
    print("NO videoSecondaryInfoRenderer")
    sys.exit(1)

chunk = raw[idx:idx+8000]

# Try to find attributedDescriptionBodyText
body_idx = chunk.find("attributedDescriptionBodyText")
if body_idx > -1:
    body_chunk = chunk[body_idx:body_idx+5000]
    texts = re.findall(r'"text":"([^"]+)"', body_chunk)
    desc = " ".join(texts)
    if desc:
        print("DESC:", desc[:1000])
        sys.exit(0)

# Try expandableVideoDescriptionBody
body_idx = chunk.find("expandableVideoDescriptionBody")
if body_idx > -1:
    body_chunk = chunk[body_idx:body_idx+5000]
    texts = re.findall(r'"text":"([^"]+)"', body_chunk)
    desc = " ".join(texts)
    if desc:
        print("DESC:", desc[:1000])
        sys.exit(0)

# Try simple runs
runs = re.findall(r'"runs":\[{"text":"([^"]+)"}\]', chunk)
if runs:
    desc = " ".join(runs)
    print("DESC:", desc[:1000])
    sys.exit(0)

# Print a sample of what's in the chunk
print("CHUNK_START:", repr(chunk[:500]))
