import sqlite3
KC = 'cache/knowledge_cube.db'
conn = sqlite3.connect(KC)
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM experiences WHERE source='crystal_will'")
print(f"crystal_will count: {c.fetchone()[0]}")

c.execute("SELECT DISTINCT source FROM experiences ORDER BY source")
print("All sources:")
for row in c.fetchall():
    print(f"  {row[0]}")
conn.close()