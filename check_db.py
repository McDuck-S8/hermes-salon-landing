import sqlite3
conn = sqlite3.connect('D:/Portable_Soft/hermes/cache/knowledge_cube.db')
c = conn.cursor()

c.execute('SELECT COUNT(*) FROM experiences')
total = c.fetchone()[0]

c.execute('SELECT COUNT(*) FROM experiences WHERE is_white_spot = 1')
white_spots = c.fetchone()[0]

c.execute('SELECT axis_domain, COUNT(*) FROM experiences GROUP BY axis_domain ORDER BY COUNT(*) DESC')
domains = c.fetchall()

c.execute('SELECT axis_outcome, COUNT(*) FROM experiences GROUP BY axis_outcome ORDER BY COUNT(*) DESC')
outcomes = c.fetchall()

print(f'Total experiences: {total}')
print(f'White spots: {white_spots} ({white_spots/total*100:.1f}%)')
print('Domains:')
for d, cnt in domains:
    print(f'  {d}: {cnt}')
print('Outcomes:')
for o, cnt in outcomes:
    print(f'  {o}: {cnt}')

conn.close()