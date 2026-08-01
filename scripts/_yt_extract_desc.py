"""Extract YouTube description from ytInitialData"""
import re, json, sys

filepath = sys.argv[1]
with open(filepath, 'r', encoding='utf-8') as f:
    c = f.read()

m = re.search(r'ytInitialData\s*=\s*(\{.+?\});', c, re.DOTALL)
if not m:
    print("NO ytInitialData")
    sys.exit(1)

data = json.loads(m.group(1))
raw = json.dumps(data, ensure_ascii=False)

idx = raw.find('attributedDescription')
if idx == -1:
    print("NO attributedDescription")
    sys.exit(1)

chunk = raw[idx:idx+20000]

# Find content field - anything between "content":" and the next "," that starts a key
start_idx = chunk.find('"content":"')
if start_idx == -1:
    print("NO content start")
    sys.exit(1)

start_idx += len('"content":"')
# The content is everything until we hit a pattern "," that looks like a JSON key
# Since content might have escaped quotes, we need to find the right boundary
# Strategy: find the position of '","' and check if what follows looks like a key (starts with letter)
search_start = start_idx
while True:
    end_idx = chunk.find('",\n', search_start)
    if end_idx == -1:
        end_idx = chunk.find('","', search_start)
    if end_idx == -1:
        break
    
    # Check what follows - if it looks like a key, this is the boundary
    remainder = chunk[end_idx+1:end_idx+30].strip()
    # A key starts with a quote followed by a word char
    if remainder.startswith('"') and len(remainder) > 2 and remainder[1].isalpha():
        desc = chunk[start_idx:end_idx]
        break
    
    search_start = end_idx + 3

if 'desc' in dir():
    desc = desc.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
    desc = desc.replace('\\xa0', ' ')
    # Unescape unicode
    desc = re.sub(r'\\u[0-9a-fA-F]{4}', lambda m: chr(int(m.group(0)[2:], 16)), desc)
    print(desc)
else:
    print("RAW:", repr(chunk[start_idx:start_idx+2000]))
