#!/usr/bin/env python3
"""Sync Entity Engine mention_counts from Knowledge Cube records."""
import sqlite3
import os
import re
from datetime import datetime

EE = os.path.join(os.path.dirname(__file__), '..', 'cache', 'entity_engine.db')
KC = os.path.join(os.path.dirname(__file__), '..', 'cache', 'knowledge_cube.db')

def get_all_entities():
    ee = sqlite3.connect(EE)
    ee.row_factory = sqlite3.Row
    c = ee.cursor()
    c.execute('SELECT id, name, type_id FROM entities')
    entities = []
    for row in c.fetchall():
        name_clean = row['name'].strip()
        if name_clean:
            entities.append({'id': row['id'], 'name': name_clean, 'type_id': row['type_id']})
    ee.close()
    return entities

def get_kc_records():
    kc = sqlite3.connect(KC)
    kc.row_factory = sqlite3.Row
    c = kc.cursor()
    c.execute('SELECT id, raw_text, axis_domain, axis_outcome, source FROM experiences')
    records = c.fetchall()
    kc.close()
    return [dict(r) for r in records]

def sync_mentions():
    print(f'[{datetime.now().isoformat()}] Starting EE-KC sync...')
    
    entities = get_all_entities()
    print(f'Entities: {len(entities)}')
    
    records = get_kc_records()
    print(f'KC records: {len(records)}')
    
    # Count mentions for each entity
    mention_counts = {e['id']: 0 for e in entities}
    entity_names = {e['name']: e['id'] for e in entities}
    
    for record in records:
        text = record.get('raw_text', '') or ''
        if not text.strip():
            continue
        text_lower = text.lower()
        for entity in entities:
            name_lower = entity['name'].lower()
            if name_lower in text_lower:
                mention_counts[entity['id']] += 1
    
    # Update EE
    ee = sqlite3.connect(EE)
    ee.row_factory = sqlite3.Row
    now = datetime.now().isoformat()
    
    updated = 0
    for eid, count in mention_counts.items():
        if count > 0:
            ee.execute('UPDATE entities SET mention_count=?, last_seen_ts=? WHERE id=?', (count, now, eid))
            updated += 1
        elif count > 0:
            pass
    
    ee.commit()
    
    # Print results
    print(f'Updated {updated} entities with real mentions')
    print()
    print('--- TOP 30 MOST MENTIONED ENTITIES ---')
    c = ee.cursor()
    c.execute('''
        SELECT e.id, e.name, e.mention_count, et.name as type
        FROM entities e
        JOIN entity_types et ON e.type_id = et.id
        ORDER BY e.mention_count DESC
        LIMIT 30
    ''')
    for row in c.fetchall():
        print(f'  {row[1]}: {row[2]} ({row[3]})')
    
    # Show Alexander specifically
    c.execute('SELECT id, name, mention_count, type_id FROM entities WHERE name LIKE ?', ('%Александр%',))
    alex = c.fetchone()
    print()
    if alex:
        print(f'--- АЛЕКСАНДР ---')
        print(f'  ID: {alex[0]}, Name: {alex[1]}, Mentions: {alex[2]}, Type: {alex[3]}')
    else:
        print('--- АЛЕКСАНДР: NOT FOUND IN DB ---')
    
    ee.close()
    print(f'[{datetime.now().isoformat()}] Sync complete.')

if __name__ == '__main__':
    sync_mentions()
