#!/usr/bin/env python3
"""Skill evolution — evaluate skills, detect gaps, suggest improvements.

Reads Knowledge Cube for skill usage patterns, checks skill_used events,
and prints actionable findings.

Runs via cron at 4am (no_agent).
"""
import json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path

HERMES = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
KC_DB = HERMES / "cache" / "knowledge_cube.db"
EVENTS_DB = HERMES / "cache" / "events.db"
SKILLS_DIR = HERMES / "skills"

report = []

def r(msg):
    report.append(msg)
    print(msg)

def check_skills():
    if not SKILLS_DIR.exists():
        r("Skills dir not found")
        return
    skills = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d/"SKILL.md").exists()]
    r(f"Skills installed: {len(skills)}")
    for s in sorted(skills):
        content = (SKILLS_DIR/s/"SKILL.md").read_text(encoding="utf-8", errors="replace")
        lines = content.strip().split("\n")
        desc = ""
        for line in lines:
            if line.startswith("# ") or line.startswith("description:"):
                desc = line.replace("# ", "").replace("description:", "").strip()
                break
        r(f"  {s:45s} {desc[:50]}")

def check_usage():
    conn = sqlite3.connect(str(EVENTS_DB))
    skill_events = conn.execute(
        "SELECT COUNT(*) FROM events WHERE event_type='skill_used'"
    ).fetchone()[0]
    r(f"Skill usage events: {skill_events}")
    if skill_events:
        recent = conn.execute(
            "SELECT data, timestamp FROM events WHERE event_type='skill_used' ORDER BY id DESC LIMIT 5"
        ).fetchall()
        for d, ts in recent:
            parsed = json.loads(d) if d else {}
            r(f"  {ts}: {parsed.get('skill_name','?')} success={parsed.get('success','?')}")
    conn.close()

def check_kc_skills():
    conn = sqlite3.connect(str(KC_DB))
    try:
        kc = conn.execute("SELECT * FROM experiences ORDER BY id DESC LIMIT 5").fetchall()
        cols = [c[1] for c in conn.execute("PRAGMA table_info(experiences)").fetchall()]
        r(f"KC experiences cols: {cols}")
        r(f"KC last 5 entries: {len(kc)}")
    except Exception as e:
        r(f"KC read error: {e}")
    conn.close()

r(f"=== Skill Evolution [{datetime.now().strftime('%Y-%m-%d %H:%M')}] ===")
check_skills()
check_usage()
check_kc_skills()
r("=== Skill Evolution Complete ===")
