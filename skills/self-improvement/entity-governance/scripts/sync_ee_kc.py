#!/usr/bin/env python3
"""
EE-KC Sync: update entity mention_counts from all KC tables.
Usage: python scripts/sync_ee_kc_all.py
"""
import sqlite3
from datetime import datetime
import time

KC = 'cache/knowledge_cube.db'
EE = 'cache/entity_engine.db'

def get_all_kc_text():
    kc = sqlite3.connect(KC)
    texts = []
    c = kc.cursor()
    for table, cols in [('experiences', ('raw_text', 'content', 'source', 'tags')),
                         ('kc_entries', ('content', 'tags', 'source', 'category')),
                         ('kc_fts', ('content',))]:
        for col in cols:
            try:
                c.execute(f'SELECT {col} FROM {table}')
                for row in c.fetchall():
                    if row[0] and isinstance(row[0], str): texts.append(row[0])
            except: pass
    kc.close()
    return '\n'.join(texts).lower()

def main():
    start = time.time()
    big_text = get_all_kc_text()
    print(f'KC text: {len(big_text)} chars in {time.time()-start:.1f}s')
    
    ee = sqlite3.connect(EE)
    ee.row_factory = sqlite3.Row
    now = datetime.now().isoformat()
    
    c = ee.cursor()
    c.execute('SELECT id, name FROM entities WHERE LENGTH(name) >= 3')
    entities = c.fetchall()
    print(f'Entities: {len(entities)}')
    
    updated, batch = 0, []
    for entity in entities:
        count = big_text.count(entity['name'].lower())
        if count > 0:
            batch.append((count, now, entity['id']))
            updated += 1
        if len(batch) >= 100:
            ee.executemany('UPDATE entities SET mention_count=?,last_seen_ts=? WHERE id=?', batch)
            ee.commit(); batch = []
    if batch:
        ee.executemany('UPDATE entities SET mention_count=?,last_seen_ts=? WHERE id=?', batch)
        ee.commit()
    
    print(f'Updated {updated} entities in {time.time()-start:.1f}s')
    ee.close()

if __name__ == '__main__':
    main()
