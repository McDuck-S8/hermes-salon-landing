#!/usr/bin/env python3
"""Initialize entity_engine.db with required tables and seed data."""

import sqlite3
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EE = os.path.join(ROOT, "cache", "entity_engine.db")

def main():
    conn = sqlite3.connect(EE)
    c = conn.cursor()

    # Create entity_types table
    c.execute('''
    CREATE TABLE IF NOT EXISTS entity_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT
    )
    ''')

    # Create entities table
    c.execute('''
    CREATE TABLE IF NOT EXISTS entities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        type_id INTEGER,
        mention_count INTEGER DEFAULT 0,
        last_seen_ts TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (type_id) REFERENCES entity_types(id)
    )
    ''')

    # Create relationships table
    c.execute('''
    CREATE TABLE IF NOT EXISTS relationships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id INTEGER,
        target_id INTEGER,
        relation_type TEXT,
        weight REAL DEFAULT 1.0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (source_id) REFERENCES entities(id),
        FOREIGN KEY (target_id) REFERENCES entities(id)
    )
    ''')

    # Insert default entity types
    default_types = [
        'AI Agent', 'Концепция', 'Проект', 'Платформа', 
        'Инструмент', 'Источник данных', 'Домен знаний',
        'Язык/Фреймворк', 'Технология', 'Человек', 'Совесть'
    ]
    for t in default_types:
        c.execute('INSERT OR IGNORE INTO entity_types (name) VALUES (?)', (t,))

    # Insert some seed entities
    seed_entities = [
        ('Hermes Agent (Я)', 'AI Agent'),
        ('Hermes Agent — Совесть', 'Совесть'),
        ('Александр', 'Человек'),
        ('Кристалл (Наблюдатель)', 'AI Agent'),
    ]
    for name, etype in seed_entities:
        c.execute('''
        INSERT OR IGNORE INTO entities (name, type_id, mention_count, last_seen_ts)
        SELECT ?, id, 0, datetime('now') FROM entity_types WHERE name=?
        ''', (name, etype))

    conn.commit()
    c.execute('SELECT name FROM sqlite_master WHERE type="table"')
    print('Tables:', c.fetchall())
    c.execute('SELECT COUNT(*) FROM entities')
    print('Entities:', c.fetchone()[0])
    c.execute('SELECT COUNT(*) FROM entity_types')
    print('Types:', c.fetchone()[0])
    conn.close()
    print('Done!')

if __name__ == '__main__':
    main()