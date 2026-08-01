"""Extract YouTube description - navigate the JSON structure directly."""
import re, json, sys

html_path = sys.argv[1]
out_path = sys.argv[2]

with open(html_path, 'r', encoding='utf-8') as f:
    c = f.read()

m = re.search(r'ytInitialData\s*=\s*(\{.+?\});', c, re.DOTALL)
if not m:
    print("NO ytInitialData")
    sys.exit(1)

data = json.loads(m.group(1))

# Navigate to find the description
# TwoColumnWatchNextResults -> results -> results -> contents
# Then itemSectionRenderer or videoSecondaryInfoRenderer
try:
    twc = data['contents']['twoColumnWatchNextResults']['results']['results']['contents']
    for item in twc:
        if 'videoSecondaryInfoRenderer' in item:
            vsir = item['videoSecondaryInfoRenderer']
            # Try various paths to description
            if 'attributedDescription' in vsir:
                desc = vsir['attributedDescription']['content']
                break
            # Fallback: look for description in any sub-object
            for key in vsir:
                if isinstance(vsir[key], dict):
                    if 'content' in vsir[key]:
                        desc = vsir[key]['content']
                        break
except (KeyError, TypeError) as e:
    desc = None

if desc:
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(desc)
    print(f"OK: {len(desc)} chars")
else:
    # Try extracting from raw string as fallback
    raw = json.dumps(data, ensure_ascii=False)
    idx = raw.find('attributedDescription')
    if idx > 0:
        chunk = raw[idx:idx+15000]
        # Simple: find content between "content":" and next ","
        start = chunk.find('"content":"')
        if start >= 0:
            start += len('"content":"')
            end = chunk.find('","', start)
            if end > start:
                desc = chunk[start:end]
                # Unescape
                desc = desc.replace('\\n', '\n').replace('\\t', '\t')
                desc = desc.replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
                desc = desc.replace('\\xa0', ' ')
                desc = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), desc)
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(desc)
                print(f"OK (raw): {len(desc)} chars")
            else:
                print("NO end found")
        else:
            print(f"NO content in chunk: {chunk[:200]}")
    else:
        print("NO attributedDescription (raw)")
