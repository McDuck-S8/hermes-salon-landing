import re, json

with open('/tmp/yt_page.html', 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'ytInitialData\s*=\s*(\{.+?\});', content, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    raw = json.dumps(data, ensure_ascii=False)
    idx = raw.find('attributedDescription')
    if idx != -1:
        chunk = raw[idx:idx+20000]
        start_idx = chunk.find('"content":"')
        if start_idx != -1:
            start_idx += len('"content":"')
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
            if 'desc' in dir():
                desc = desc.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
                desc = desc.replace('\\xa0', ' ')
                desc = re.sub(r'\\u[0-9a-fA-F]{4}', lambda m: chr(int(m.group(0)[2:], 16)), desc)
                print(desc)
            else:
                print('NOT FOUND')
        else:
            print('content not found')
    else:
        print('attributedDescription not found')
else:
    print('ytInitialData not found')