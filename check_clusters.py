import sqlite3
conn = sqlite3.connect('D:/Portable_Soft/hermes/cache/knowledge_cube.db')
c = conn.cursor()
c.execute('SELECT cluster_id, size, representative_text FROM white_spot_clusters')
for row in c.fetchall():
    print(f'Cluster {row[0]}: size={row[1]}, rep={row[2][:100]}')
conn.close()