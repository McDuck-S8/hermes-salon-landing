#!/usr/bin/env python3
"""Subconscious loop — spread activation through Knowledge Cube.

Autonomous: reads recent events, surfaces related KC entries.
Self-contained inside Hermes (no external dependencies).

Runs via cron every 120m (no_agent).
"""
import json, sqlite3, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERMES = Path(__file__).resolve().parent.parent
KC_DB = HERMES / "cache" / "knowledge_cube.db"
EVENTS_DB = HERMES / "cache" / "events.db"

report = []

def r(msg):
    report.append(msg)
    print(msg)

def spread_activation():
    """Find recent events, spread activation to related KC entries."""
    now = datetime.now(timezone.utc)
    since = (now - timedelta(hours=2)).isoformat()
    
    # Read recent events
    conn = sqlite3.connect(str(EVENTS_DB))
    recent = conn.execute(
        "SELECT event_type, data, timestamp FROM events WHERE timestamp > ? ORDER BY id DESC",
        (since,)
    ).fetchall()
    conn.close()
    
    r(f"Events in last 2h: {len(recent)}")
    if not recent:
        return
    
    # Collect domains from recent events
    domains = set()
    topics = []
    for et, data, ts in recent[:50]:
        parsed = json.loads(data) if data else {}
        domain = parsed.get("domain", parsed.get("axis_domain", ""))
        if domain:
            domains.add(domain)
        topics.append((et, domain, str(parsed)[:60]))
    
    r(f"Active domains: {domains}")
    
    # Find related KC entries for each domain
    conn = sqlite3.connect(str(KC_DB))
    
    for domain in sorted(domains):
        if not domain:
            continue
        # Ensure last_activated column
        cols = [r[1] for r in conn.execute("PRAGMA table_info(experiences)").fetchall()]
        if "last_activated" not in cols:
            conn.execute("ALTER TABLE experiences ADD COLUMN last_activated TEXT")
            conn.commit()
        
        related = conn.execute(
            "SELECT id, content, importance, last_activated FROM experiences "
            "WHERE axis_domain = ? ORDER BY ts DESC LIMIT 5",
            (domain,)
        ).fetchall()
        
        if related:
            r(f"  {domain}: {len(related)} entries")
            for eid, content, importance, last_act in related:
                content_preview = (content[:60] + "...") if content and len(content) > 60 else (content or "N/A")
                age = ""
                if last_act:
                    try:
                        last_dt = datetime.fromisoformat(last_act)
                        age = f" (last activated {(now - last_dt).total_seconds()/3600:.1f}h ago)"
                    except: pass
                r(f"    [{eid}] imp={importance} {content_preview}{age}")
                
                # Update last_activated
                conn.execute(
                    "UPDATE experiences SET last_activated = ? WHERE id = ?",
                    (now.isoformat(), eid)
                )
        else:
            r(f"  {domain}: no KC entries found")
    
    conn.commit()
    conn.close()
    r(f"Activation spread to {len(domains)} domain(s)")

r(f"=== Subconscious Loop [{datetime.now().strftime('%Y-%m-%d %H:%M')}] ===")
spread_activation()
r("=== Subconscious Complete ===")
