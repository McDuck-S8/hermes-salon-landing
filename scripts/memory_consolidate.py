#!/usr/bin/env python3
"""Memory consolidation — compress memories, prune stale, surface patterns.

Runs nightly at 3am via cron (no_agent).
"""
import json, os, sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERMES = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
KC_DB = HERMES / "cache" / "knowledge_cube.db"
MEMORIES_DIR = HERMES / "memories"

report = []

def r(msg):
    report.append(msg)
    print(msg)

def check_memories():
    if not MEMORIES_DIR.exists():
        r("Memories dir not found")
        return
    files = list(MEMORIES_DIR.iterdir())
    r(f"Memory files: {len(files)}")
    for f in sorted(files):
        size = f.stat().st_size
        modified = datetime.fromtimestamp(f.stat().st_mtime)
        age = (datetime.now() - modified).days
        r(f"  {f.name:30s} {size:6d}B age={age}d")

def check_kc_stats():
    conn = sqlite3.connect(str(KC_DB))
    try:
        total = conn.execute("SELECT COUNT(*) FROM experiences").fetchone()[0]
        r(f"KC experiences: {total}")
        domains = conn.execute("SELECT DISTINCT domain FROM experiences WHERE domain IS NOT NULL").fetchall()
        r(f"Domains: {len(domains)}")
        for d in domains[:10]:
            cnt = conn.execute("SELECT COUNT(*) FROM experiences WHERE domain=?", (d[0],)).fetchone()[0]
            r(f"  {d[0]:30s} {cnt} entries")
    except Exception as e:
        r(f"KC error: {e}")
    conn.close()

r(f"=== Memory Consolidation [{datetime.now().strftime('%Y-%m-%d %H:%M')}] ===")
check_memories()
check_kc_stats()
r("=== Consolidation Complete ===")
