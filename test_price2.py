import re
text = 'PWA для ставок на крикет в Индии, CPA $10 за рег+деп, без KYC'
print(repr(text))
m = re.search(r'cpa\s*[=:]\s*\$?(\d+(?:\.\d+)?)', text, re.I)
print(m)
if m:
    print(m.group(1))