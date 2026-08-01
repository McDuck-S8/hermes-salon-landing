import sqlite3
ee = sqlite3.connect('cache/entity_evolution.db')
c = ee.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
for row in c.fetchall():
    print(row)
ee.close()