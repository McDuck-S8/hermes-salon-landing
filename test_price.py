import re
text = 'PWA для ставок на крикет в Индии, CPA $10 за рег+деп, без KYC'
patterns = [
    r'\$(\d+(?:\.\d+)?)',
    r'(\d+(?:\.\d+)?)\s*(?:руб|р\.|rub)',
    r'cpa\s*[=:]\s*\$?(\d+(?:\.\d+)?)',
    r'cps\s*[=:]\s*(\d+(?:\.\d+)?)%',
]
for p in patterns:
    m = re.search(p, text, re.I)
    if m:
        print(f'Matched {p}: {m.group(1)}')