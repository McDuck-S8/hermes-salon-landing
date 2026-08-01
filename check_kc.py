import sqlite3
conn = sqlite3.connect('/d/Portable_Soft/hermes/cache/knowledge_cube.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tables:', tables)
conn.close()