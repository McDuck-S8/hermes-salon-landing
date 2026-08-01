import json
import re

with open('/tmp/yt_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

raw = json.dumps(data, ensure_ascii=False)
idx = raw.find('attributedDescription')
if idx != -1:
    chunk = raw[idx:idx+20000]
    start_idx = chunk.find('"content":"')
    if start_idx != -1:
        start_idx += len('"content":"')
        search_start = start_idx
        desc = None
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
        if desc:
            desc = desc.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
            desc = desc.replace('\\xa0', ' ')
            desc = re.sub(r'\\u[0-9a-fA-F]{4}', lambda m: chr(int(m.group(0)[2:], 16)), desc)
            print(desc[:5000])
        else:
            print('NOT FOUND desc')
    else:
        print('content not found')
else:
    print('attributedDescription not found')