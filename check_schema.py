import sqlite3
KC = 'cache/knowledge_cube.db'
conn = sqlite3.connect(KC)
c = conn.cursor()
c.execute("PRAGMA table_info(experiences)")
for row in c.fetchall():
    print(row)
conn.close()