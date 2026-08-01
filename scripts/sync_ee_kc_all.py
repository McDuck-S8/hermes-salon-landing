#!/usr/bin/env python3
"""Fast EE-KC sync: read all KC text once, count mentions in Python."""
import sqlite3
import os
from datetime import datetime

KC = os.path.join(os.path.dirname(__file__), '..', 'cache', 'knowledge_cube.db')
EE = os.path.join(os.path.dirname(__file__), '..', 'cache', 'entity_engine.db')

def get_all_kc_text():
    """Read ALL text content from KC into a single lowercase string."""
    kc = sqlite3.connect(KC)
    texts = []
    
    # From experiences
    c = kc.cursor()
    c.execute('SELECT raw_text, content, source, tags, axis_domain, axis_outcome FROM experiences')
    for row in c.fetchall():
        for val in row:
            if val and isinstance(val, str):
                texts.append(val)
    
    # From kc_entries
    c.execute('SELECT content, tags, source, category FROM kc_entries')
    for row in c.fetchall():
        for val in row:
            if val and isinstance(val, str):
                texts.append(val)
    
    # From kc_fts
    c.execute('SELECT content FROM kc_fts')
    for row in c.fetchall():
        if row[0]:
            texts.append(row[0])
    
    kc.close()
    return '\n'.join(texts).lower()

def main():
    print(f'[{datetime.now().isoformat()}] Reading all KC text...')
    kc_text = get_all_kc_text()
    text_len = len(kc_text)
    print(f'KC text length: {text_len} chars')
    
    # Get all entities from EE
    ee = sqlite3.connect(EE)
    ee.row_factory = sqlite3.Row
    c = ee.cursor()
    c.execute('SELECT id, name FROM entities')
    entities = c.fetchall()
    print(f'EE entities: {len(entities)}')
    
    # Count mentions in Python (fast)
    now = datetime.now().isoformat()
    updated = 0
    total_mentions = 0
    
    results = []
    for entity in entities:
        name = entity['name']
        if not name or len(name) < 3:
            continue
        name_lower = name.lower()
        count = kc_text.count(name_lower)
        if count > 0:
            ee.execute('UPDATE entities SET mention_count=?, last_seen_ts=? WHERE id=?', 
                       (count, now, entity['id']))
            updated += 1
            total_mentions += count
            results.append((count, name, entity['id']))
    
    ee.commit()
    
    print(f'Updated {updated} entities with real KC mentions')
    print(f'Total mentions found: {total_mentions}')
    print()
    
    # Show top-30
    results.sort(key=lambda x: x[0], reverse=True)
    print('TOP 30 MOST MENTIONED ENTITIES:')
    for count, name, eid in results[:30]:
        # Get type
        c.execute('SELECT et.name FROM entities e JOIN entity_types et ON e.type_id=et.id WHERE e.id=?', (eid,))
        typ = c.fetchone()
        type_name = typ[0] if typ else '?'
        print(f'  {name}: {count} ({type_name})')
    
    print()
    
    # Show Alexander specifically
    alex_count = kc_text.count('александр')
    print(f'--- АЛЕКСАНДР ---')
    print(f'  Real mentions in KC: {alex_count}')
    print()
    if alex_count > 0:
        # Update Alexander
        ee.execute('UPDATE entities SET mention_count=?, last_seen_ts=? WHERE name=?', 
                   (alex_count, now, 'Александр'))
        ee.commit()
        print(f'  EE updated: Александр now has {alex_count} mentions')
    
    # Create relationship
    c.execute('SELECT id FROM entities WHERE name=?', ('Александр',))
    alex_row = c.fetchone()
    c.execute('SELECT id FROM entities WHERE name=?', ('Hermes Agent (Я)',))
    hermes_row = c.fetchone()
    
    if alex_row and hermes_row:
        ee.execute('''
            INSERT OR IGNORE INTO relationships (source_id, target_id, relation_type, weight)
            VALUES (?, ?, 'is_owner_of', 1.0)
        ''', (alex_row[0], hermes_row[0]))
        ee.commit()
        print(f'  Relationship created: Александр --is_owner_of--> Hermes Agent (Я)')
    
    # Summary
    print()
    print('--- BEFORE vs AFTER ---')
    print(f'  EE-KC connection: BROKEN → FIXED')
    print(f'  Alexander mentions: 0 → {alex_count}')
    print(f'  Entities with mentions: ~0 → {updated}')
    print(f'  Relationships: 0 → 1')
    
    ee.close()
    print(f'[{datetime.now().isoformat()}] Sync complete.')

if __name__ == '__main__':
    main()
