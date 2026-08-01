#!/usr/bin/env python3
"""Ingest recent sessions into Knowledge Cube."""
import sys, os, json, sqlite3
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))
from knowledge_cube import add_experience, get_cube_stats

# Heartbeat: module alive
try:
    from chain_heartbeat import beat
    beat("cube_session_ingester")
except ImportError:
    pass

# Find session DB
HERMES_HOME = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
SESSION_DB = HERMES_HOME / "sessions.db"

if not SESSION_DB.exists():
    print("No session DB found")
    sys.exit(0)

conn = sqlite3.connect(str(SESSION_DB))
conn.row_factory = sqlite3.Row

# Get sessions from last 24h
cutoff = (datetime.now() - timedelta(hours=24)).timestamp()
rows = conn.execute("""
    SELECT id, title, started_at, message_count
    FROM sessions
    WHERE started_at > ?
    ORDER BY started_at DESC
    LIMIT 20
""", (cutoff,)).fetchall()

if not rows:
    print("No new sessions in last 24h")
    sys.exit(0)

added = 0
for r in rows:
    title = r[1] or r[0]
    text = "Session: {} ({} messages)".format(title, r[3])
    result = add_experience(
        text=text,
        source="session_ingester",
        dynamic_axes={"session_id": r[0], "message_count": r[3]}
    )
    if result["status"] == "added":
        added += 1

stats = get_cube_stats()
print("Ingested {} sessions. Cube: {} experiences, {} white spots ({}%)".format(
    added, stats["total_experiences"], stats["white_spots"], stats["white_spot_pct"]))

conn.close()
