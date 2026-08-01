"""Extract YouTube video descriptions from downloaded HTML files."""
import re, json, sys, os

def extract_desc(html_path):
    with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
        c = f.read()
    
    m = re.search(r'ytInitialData\s*=\s*(\{.+?\});', c, re.DOTALL)
    if not m:
        return None  # No ytInitialData
    
    try:
        data = json.loads(m.group(1))
    except:
        return None
    
    raw = json.dumps(data, ensure_ascii=False)
    idx = raw.find('attributedDescription')
    if idx == -1:
        return None
    
    chunk = raw[idx:idx+20000]
    start = chunk.find('"content":"')
    if start == -1:
        return None
    
    start += len('"content":"')
    
    # Parse the JSON string value character by character
    chars = []
    i = start
    while i < len(chunk):
        ch = chunk[i]
        if ch == '\\' and i+1 < len(chunk):
            next_ch = chunk[i+1]
            if next_ch == 'n':
                chars.append('\n')
                i += 2
                continue
            elif next_ch == 't':
                chars.append('\t')
                i += 2
                continue
            elif next_ch == '"':
                chars.append('"')
                i += 2
                continue
            elif next_ch == '\\':
                chars.append('\\')
                i += 2
                continue
            elif next_ch == '/':
                chars.append('/')
                i += 2
                continue
            elif next_ch == 'u':
                # Unicode escape \uXXXX
                if i+5 < len(chunk):
                    try:
                        code = int(chunk[i+2:i+6], 16)
                        chars.append(chr(code))
                        i += 6
                        continue
                    except:
                        pass
        elif ch == '"':
            # End of string - check if this is really the end
            rest = chunk[i:i+10].replace('\n', ' ')
            if rest.startswith('", "'):
                break
            elif rest.startswith('",\n'):  # will check for key after
                rest2 = chunk[i+2:i+10].strip()
                if rest2.startswith('"') and len(rest2) > 2 and rest2[1].isalpha():
                    break
            chars.append(ch)
        else:
            chars.append(ch)
        i += 1
    
    desc = ''.join(chars)
    # Clean up
    desc = desc.replace('\\xa0', ' ')
    return desc

def main():
    cache_dir = sys.argv[1] if len(sys.argv) > 1 else 'D:/Portable_Soft/hermes/cache'
    output_dir = os.path.join(cache_dir, 'yt_descs')
    os.makedirs(output_dir, exist_ok=True)
    
    for fname in sorted(os.listdir(cache_dir)):
        if not fname.startswith('yt_') or not fname.endswith('.html'):
            continue
        html_path = os.path.join(cache_dir, fname)
        name = fname[3:-5]  # Remove 'yt_' and '.html'
        
        size = os.path.getsize(html_path)
        if size < 100:
            print(f"{name}: EMPTY ({size} bytes)")
            continue
        
        desc = extract_desc(html_path)
        if desc:
            out_path = os.path.join(output_dir, f"{name}.txt")
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(desc)
            print(f"{name}: OK ({len(desc)} chars)")
        else:
            print(f"{name}: FAIL (no description)")

if __name__ == '__main__':
    main()
