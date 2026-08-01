#!/usr/bin/env python3
"""Fix mention_count for 'Александр' in Entity Engine from KC records."""
import sqlite3
import os

def fix_alexander_mentions():
    kc_path = os.path.join(os.path.dirname(__file__), '..', 'cache', 'knowledge_cube.db')
    ee_path = os.path.join(os.path.dirname(__file__), '..', 'cache', 'entity_engine.db')
    
    # Count mentions in KC
    kc = sqlite3.connect(kc_path)
    kc.row_factory = sqlite3.Row
    count = 0
    for row in kc.execute('SELECT content FROM experiences'):
        if 'Александр' in row['content'] or 'Александра' in row['content']:
            count += 1
    kc.close()
    
    # Update EE
    ee = sqlite3.connect(ee_path)
    ee.row_factory = sqlite3.Row
    c = ee.cursor()
    c.execute('UPDATE entities SET mention_count=?, last_seen_ts=datetime(\'now\') WHERE name=?', (count, 'Александр'))
    ee.commit()
    
    # Verify
    c.execute('SELECT id, name, mention_count, last_seen_ts FROM entities WHERE name=?', ('Александр',))
    row = c.fetchone()
    print(f'Александр: id={row[0]}, mentions={row[1]}, last_seen={row[2]}')
    
    # Also check type
    c.execute('SELECT et.name FROM entities e JOIN entity_types et ON e.type_id=et.id WHERE e.name=?', ('Александр',))
    type_name = c.fetchone()
    print(f'Type: {type_name[0]}')
    
    ee.close()

if __name__ == '__main__':
    fix_alexander_mentions()
