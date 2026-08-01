#!/usr/bin/env python3
"""Missing domains analysis — delegated to agent.
WARNING: Hand-written by Hermes directly. Should have been delegated.
Kept as reference for the skill workflow."""
import sqlite3, json
from collections import Counter

db = sqlite3.connect('D:/Portable_Soft/hermes/cache/knowledge_cube.db')
db.row_factory = sqlite3.Row
c = db.cursor()

c.execute("SELECT DISTINCT axis_domain FROM experiences WHERE axis_domain IS NOT NULL AND axis_domain != ''")
existing = set(r['axis_domain'] for r in c.fetchall())

c.execute("SELECT tags FROM experiences WHERE tags IS NOT NULL AND tags != ''")
tag_domains = Counter()
for r in c.fetchall():
    try:
        tags = json.loads(r['tags']) if isinstance(r['tags'], str) else [r['tags']]
    except:
        tags = [r['tags']]
    for tag in tags if isinstance(tags, list) else [tags]:
        ts = str(tag).strip()
        if ts.startswith('domain:'):
            bare = ts.replace('domain:', '')
            if bare not in existing:
                tag_domains[ts] += 1

print('Domains in tags but NOT in axis_domain:')
for dom, cnt in tag_domains.most_common():
    print(f'  {dom:<35} {cnt:>4}')
print(f'\nTotal missing: {len(tag_domains)}')
db.close()
