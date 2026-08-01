#!/usr/bin/env python3
"""
Record user messages to Knowledge Cube + sync Entity Engine.
Run at session start and after every user message.
"""
import sys, os, json, sqlite3
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

KC_DB = os.path.join(ROOT, 'cache', 'knowledge_cube.db')
EE_DB = os.path.join(ROOT, 'cache', 'entity_engine.db')

def record_user_message(message, source="user_chat"):
    """Record a user message to KC experiences table."""
    conn = sqlite3.connect(KC_DB)
    now = datetime.now().isoformat()
    content = f"[user:Александр:{source}] {message}"
    
    conn.execute('''
        INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, source)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        now,
        content,
        message,
        str(hash(message))[:16],
        'user_communication',
        'neutral',
        source
    ))
    conn.commit()
    conn.close()
    return True

def record_principal_fact():
    """Record the fact that Alexander is the principal/owner of Hermes."""
    conn = sqlite3.connect(KC_DB)
    c = conn.cursor()
    
    # Check if already recorded
    c.execute('SELECT COUNT(*) FROM experiences WHERE source=? AND raw_text LIKE ?',
              ('system_init', '%принципал%'))
    if c.fetchone()[0] == 0:
        now = datetime.now().isoformat()
        fact = "Alexander (Александр) is the principal and owner of the entire Hermes system. The system serves him. He is NOT a phantom entity."
        conn.execute('''
            INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, source, importance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (now, fact, fact, str(hash(fact))[:16], 'user_identity', 'success', 'system_init', 10.0))
        conn.commit()
        print('✅ Principal fact recorded to KC')
    conn.close()

def sync_ee_from_kc():
    """Fast sync: read all KC text, count entity mentions, update EE."""
    # Read all KC text
    kc = sqlite3.connect(KC_DB)
    texts = []
    c = kc.cursor()
    for table_col in [
        ('experiences', 'raw_text'),
        ('experiences', 'content'),
        ('kc_entries', 'content'),
        ('kc_fts', 'content')
    ]:
        try:
            c.execute(f'SELECT {table_col[1]} FROM {table_col[0]}')
            for row in c.fetchall():
                if row[0] and isinstance(row[0], str):
                    texts.append(row[0])
        except:
            pass
    kc.close()
    
    big_text = '\n'.join(texts).lower()
    print(f'KC text: {len(big_text)} chars')
    
    # Update EE
    ee = sqlite3.connect(EE_DB)
    ee.row_factory = sqlite3.Row
    now = datetime.now().isoformat()
    
    # Get entities
    c = ee.cursor()
    c.execute('SELECT id, name FROM entities WHERE LENGTH(name) >= 3')
    entities = c.fetchall()
    
    updated = 0
    batch = []
    for idx, entity in enumerate(entities):
        name_lower = entity['name'].lower()
        count = big_text.count(name_lower)
        if count > 0:
            batch.append((count, now, entity['id']))
            updated += 1
        if len(batch) >= 100:
            ee.executemany('UPDATE entities SET mention_count=?, last_seen_ts=? WHERE id=?', batch)
            ee.commit()
            batch = []
    if batch:
        ee.executemany('UPDATE entities SET mention_count=?, last_seen_ts=? WHERE id=?', batch)
        ee.commit()
    
    # Create principal relationship
    c.execute('SELECT id FROM entities WHERE name=?', ('Александр',))
    alex = c.fetchone()
    c.execute('SELECT id FROM entities WHERE name=?', ('Hermes Agent (Я)',))
    hermes = c.fetchone()
    if alex and hermes:
        ee.execute('INSERT OR IGNORE INTO relationships (source_id, target_id, relation_type, weight) VALUES (?, ?, ?, ?)',
                   (alex['id'], hermes['id'], 'is_owner_of', 1.0))
        ee.commit()
    
    # Verify Alexander
    c.execute('SELECT mention_count FROM entities WHERE name=?', ('Александр',))
    alex_row = c.fetchone()
    alex_count = alex_row[0] if alex_row else 0
    print(f'Alexander mentions: {alex_count}')
    print(f'Entities with mentions: {updated}')
    
    ee.close()
    return updated

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--init':
        record_principal_fact()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--message':
        msg = sys.argv[2] if len(sys.argv) > 2 else ''
        if msg:
            record_user_message(msg)
            # Proactive processing: detect patterns in user's message
            try:
                from proactive_voice import process_user_message
                result = process_user_message(msg)
                if result.get('summary'):
                    print(f'  {result["summary"]}')
                if result.get('frustrations'):
                    print(f'  ⚠️  Frustration detected — streak: {result["frustrations"][0]}')
                if result.get('corrections'):
                    print(f'  ✅ Correction processed')
            except Exception as e:
                print(f'  Proactive processing: {e}')
            print(f'Recorded: {msg[:50]}...')
    
    if '--sync' in sys.argv:
        n = sync_ee_from_kc()
        print(f'Sync complete: {n} entities updated')
    
    if len(sys.argv) == 1:
        # Full init
        record_principal_fact()
        n = sync_ee_from_kc()
        print(f'Full init complete. Entities synced: {n}')
