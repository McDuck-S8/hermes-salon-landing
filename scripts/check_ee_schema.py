import sqlite3
ee = sqlite3.connect('cache/entity_evolution.db')
c = ee.cursor()
c.execute('PRAGMA table_info(relationships)')
for row in c.fetchall():
    print(row)
ee.close()