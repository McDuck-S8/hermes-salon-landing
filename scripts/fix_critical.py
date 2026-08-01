#!/usr/bin/env python3
"""Fix critical infrastructure: KC tables, meditation insights"""
import sqlite3, json, time, os


> Revisit: when fix critical logic, critical error detection, or auto-fix triggers change. Last touched: 2026-07-02.
BASE = "D:/Portable_Soft/hermes"

# Fix 1: Recreate old knowledge_cube.db experiences table
db_path = os.path.join(BASE, "cache", "knowledge_cube.db")
db = sqlite3.connect(db_path)

db.execute("""CREATE TABLE IF NOT EXISTS experiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    tags TEXT,
    source TEXT DEFAULT 'agent',
    created_at INTEGER,
    verified INTEGER DEFAULT 0,
    usefulness REAL DEFAULT 0.0
)""")

db.execute("""CREATE TABLE IF NOT EXISTS errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error TEXT NOT NULL,
    fix TEXT,
    tags TEXT,
    source TEXT DEFAULT 'agent',
    created_at INTEGER
)""")

db.execute("""CREATE TABLE IF NOT EXISTS corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correction TEXT NOT NULL,
    context TEXT,
    created_at INTEGER
)""")

db.commit()
tables = [t[0] for t in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
count = db.execute("SELECT COUNT(*) FROM experiences").fetchone()[0]
print(f"KC tables: {tables}, experiences rows: {count}")
db.close()

# Fix 2: Fix meditation_insights.json
insights_path = os.path.join(BASE, "cache", "meditation_insights.json")
try:
    with open(insights_path) as f:
        data = json.load(f)
except:
    data = {}

if "cycles" not in data:
    data["cycles"] = 0
data["last_updated"] = int(time.time())

with open(insights_path, "w") as f:
    json.dump(data, f, indent=2)
print(f"meditation_insights.json: cycles={data['cycles']}")

print("Done: KC tables + insights fixed")
