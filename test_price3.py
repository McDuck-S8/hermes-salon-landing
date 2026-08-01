import re
text = 'PWA для ставок на крикет в Индии, CPA $10 за рег+деп, без KYC'
# The issue: "CPA $10" has a space not = or :
m = re.search(r'cpa\s+(\$?\d+(?:\.\d+)?)', text, re.I)
print(m)
if m:
    print(m.group(1))

# Better pattern:
m2 = re.search(r'cpa\s*[=:\$]?\s*\$?(\d+(?:\.\d+)?)', text, re.I)
print(m2)
if m2:
    print(m2.group(1))