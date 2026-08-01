import sqlite3
KC = 'cache/knowledge_cube.db'
conn = sqlite3.connect(KC)
c = conn.cursor()
c.execute("SELECT raw_text FROM experiences WHERE source='crystal_will' ORDER BY id DESC LIMIT 10")
for row in c.fetchall():
    print(row[0][:200])
    print('---')
conn.close()