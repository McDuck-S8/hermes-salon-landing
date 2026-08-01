#!/usr/bin/env python3
"""Check DB state."""
import sqlite3, json, os

DB_PATH = r'D:\Portable_Soft\hermes\projects\sales-machine\db\clients.db'
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print('Tables:', tables)

for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    count = cursor.fetchone()[0]
    print(f'\n=== {t} ({count} total) ===')
    if count > 0:
        cursor.execute(f"SELECT * FROM {t} LIMIT 3")
        rows = [dict(r) for r in cursor.fetchall()]
        print('Columns:', list(rows[0].keys()))
        for r in rows:
            print(json.dumps(r, indent=2, default=str, ensure_ascii=False)[:300])

conn.close()
