#!/usr/bin/env python3
"""Dream memory consolidation — replay recent KC entries, find patterns.

Consolidates recent knowledge by cross-referencing entries across domains.
Self-contained inside Hermes.

Runs via cron every 3h (no_agent).
"""
import json, sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERMES = Path(__file__).resolve().parent.parent
KC_DB = HERMES / "cache" / "knowledge_cube.db"
EVENTS_DB = HERMES / "cache" / "events.db"

report = []

def r(msg):
    report.append(msg)
    print(msg)

def consolidate():
    now = datetime.now(timezone.utc)
    since_24h = (now - timedelta(hours=24)).isoformat()
    
    conn = sqlite3.connect(str(KC_DB))
    
    # Count recent KC entries
    recent = conn.execute(
        "SELECT COUNT(*) FROM experiences WHERE ts > ?",
        (since_24h,)
    ).fetchone()[0]
    r(f"KC entries in last 24h: {recent}")
    
    # Domain distribution
    domains = conn.execute(
        "SELECT axis_domain, COUNT(*) as cnt FROM experiences "
        "WHERE ts > ? AND axis_domain IS NOT NULL "
        "GROUP BY axis_domain ORDER BY cnt DESC",
        (since_24h,)
    ).fetchall()
    r("Domains active in last 24h:")
    for d, cnt in domains:
        r(f"  {d or '?':30s} {cnt} entries")
    
    # Cross-domain entries (adjacent patterns)
    cross = conn.execute(
        "SELECT content, tags FROM experiences WHERE ts > ? "
        "ORDER BY random() LIMIT 3",
        (since_24h,)
    ).fetchall()
    if cross:
        r("Sample new entries:")
        for content, tags in cross:
            preview = (content[:80] + "...") if content and len(content) > 80 else (content or "N/A")
            r(f"  {preview} | tags={tags}")
    
    conn.close()
    r("Dream consolidation cycle complete")

r(f"=== Dream Consolidation [{datetime.now().strftime('%Y-%m-%d %H:%M')}] ===")

# Heartbeat: module alive
try:
    from chain_heartbeat import beat
    beat("dream_memory_cron")
except ImportError:
    pass

consolidate()
r("=== Dream Complete ===")
