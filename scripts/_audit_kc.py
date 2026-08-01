#!/usr/bin/env python3
"""Audit KC content classification"""
import sqlite3
kc = sqlite3.connect('../cache/knowledge_cube.db')
c = kc.cursor()

total = c.execute('SELECT COUNT(*) FROM experiences').fetchone()[0]

# Count by prefix pattern
patterns = {
    'suggestion': "raw_text LIKE '%[suggestion:%'",
    'pattern_fact': "(raw_text LIKE '%[pattern]%' OR raw_text LIKE '%[fact]%')",
    'user_msg': "raw_text LIKE '%[user:%'",
    'domain': "raw_text LIKE '%[domain]%'",
    'skill': "raw_text LIKE '%Skill%belongs%'",
}

counts = {}
for name, cond in patterns.items():
    cnt = c.execute(f'SELECT COUNT(*) FROM experiences WHERE {cond}').fetchone()[0]
    counts[name] = cnt
    print(f'  {name}: {cnt} ({cnt/total*100:.1f}%)')

classified = sum(counts.values())
other = total - classified
print(f'  other: {other} ({other/total*100:.1f}%)')

# Unique raw_text
unique = c.execute('SELECT COUNT(DISTINCT raw_text) FROM experiences').fetchone()[0]
print(f'\nUnique raw_text: {unique} ({unique/total*100:.1f}%)')

# Sample other
rows = c.execute(f'''
    SELECT raw_text, axis_domain, axis_outcome, ts 
    FROM experiences 
    WHERE raw_text NOT LIKE '%[suggestion:%' 
      AND raw_text NOT LIKE '%[pattern]%' 
      AND raw_text NOT LIKE '%[fact]%' 
      AND raw_text NOT LIKE '%[user:%'
      AND raw_text NOT LIKE '%[domain]%'
      AND raw_text NOT LIKE '%Skill%belongs%'
    LIMIT 8
''').fetchall()
print('\n=== OTHER SAMPLES ===')
for r in rows:
    text = r[0][:200] if r[0] else ''
    print(f'  [{r[3][:19]}] {r[2]}/{r[1]}: {text}')
    print()

# Suggestionees — how many unique [suggestion:XXX] types?
c.execute("SELECT DISTINCT SUBSTR(raw_text, 1, 40) FROM experiences WHERE raw_text LIKE '%[suggestion:%' LIMIT 20")
print('=== SUGGESTION TYPES ===')
for r in c.fetchall():
    print(f'  {r[0][:60]}')

kc.close()
