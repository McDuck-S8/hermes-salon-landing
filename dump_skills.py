#!/usr/bin/env python3
"""Dump all skills from skill_index for inspection."""
import sqlite3, json
conn = sqlite3.connect('cache/knowledge_cube.db')
cur = conn.cursor()
cur.execute('SELECT skill_name, description, category, tags FROM skill_index ORDER BY skill_name')
rows = cur.fetchall()
print(f"Total skills: {len(rows)}")
for r in rows:
    print(f"SKILL|{r[0]}|CAT|{r[2]}|TAGS|{r[3]}|DESC|{(r[1] or '')[:150]}")
conn.close()
