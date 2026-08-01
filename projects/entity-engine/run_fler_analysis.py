#!/usr/bin/env python3
"""
Batch Fler Engine analysis of all sessions from state.db.
Reads user messages, analyzes sentiment, aggregates by session, saves to fler_engine.db.
"""

import sqlite3
import json
import os
import sys
from pathlib import Path

# Add fler_engine to path
sys.path.insert(0, str(Path(__file__).parent))
from fler_engine import analyze_session, init_db, save_session

STATE_DB = Path("D:/Portable_Soft/hermes/state.db")
FLER_DB_PATH = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))) / "cache" / "fler_engine.db"


def get_user_messages(state_conn, session_id):
    """Get all user messages for a session from state.db."""
    c = state_conn.cursor()
    # Try common table names
    for table in ["messages", "chat_messages", "conversations"]:
        try:
            c.execute(f"PRAGMA table_info({table})")
            cols = [row[1] for row in c.fetchall()]
            if cols:
                # Find the right columns
                role_col = None
                content_col = None
                sid_col = None
                for col in cols:
                    if col.lower() in ("role", "sender", "type", "author"):
                        role_col = col
                    if col.lower() in ("content", "text", "message", "body"):
                        content_col = col
                    if col.lower() in ("session_id", "session", "chat_id", "thread_id"):
                        sid_col = col
                
                if role_col and content_col and sid_col:
                    c.execute(f"SELECT {content_col} FROM {table} WHERE {sid_col} = ? AND {role_col} IN ('user', 'human')", (session_id,))
                    return [row[0] for row in c.fetchall() if row[0]]
        except Exception:
            continue
    return []


def get_all_sessions(state_conn):
    """Get all unique session IDs from state.db."""
    c = state_conn.cursor()
    # Try common table names
    for table in ["messages", "chat_messages", "conversations"]:
        try:
            c.execute(f"PRAGMA table_info({table})")
            cols = [row[1] for row in c.fetchall()]
            if cols:
                # Find session ID column
                sid_col = None
                for col in cols:
                    if col.lower() in ("session_id", "session", "chat_id", "thread_id"):
                        sid_col = col
                        break
                if sid_col:
                    c.execute(f"SELECT DISTINCT {sid_col} FROM {table}")
                    sessions = [row[0] for row in c.fetchall() if row[0]]
                    if sessions:
                        print(f"[INFO] Found {len(sessions)} sessions in table '{table}'")
                        return sessions, table
        except Exception:
            continue
    return [], None


def main():
    print("=" * 70)
    print("  FLER ENGINE - BATCH ANALYSIS OF ALL SESSIONS")
    print("=" * 70)
    print()
    
    # Connect to state.db
    if not STATE_DB.exists():
        print(f"[ERROR] State DB not found: {STATE_DB}")
        sys.exit(1)
    
    state_conn = sqlite3.connect(str(STATE_DB))
    
    # Get all sessions
    sessions, table_name = get_all_sessions(state_conn)
    if not sessions:
        print("[ERROR] No sessions found in state.db")
        print("[INFO] Listing tables and their schemas:")
        c = state_conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        for t in tables:
            tname = t[0]
            c.execute(f"PRAGMA table_info({tname})")
            cols = c.fetchall()
            print(f"  Table: {tname}")
            for col in cols:
                print(f"    {col[1]} ({col[2]})")
        state_conn.close()
        sys.exit(1)
    
    # Init fler DB
    fler_conn = init_db()
    fler_c = fler_conn.cursor()
    # Clear old results
    fler_c.execute("DELETE FROM fler_sessions")
    fler_conn.commit()
    
    # Analyze each session
    results = []
    for i, session_id in enumerate(sessions):
        messages = get_user_messages(state_conn, session_id)
        if not messages:
            continue
        
        result = analyze_session(messages)
        if result is None:
            continue
        
        # Save to fler DB
        fler_c.execute("""
            INSERT INTO fler_sessions 
            (session_id, message_count, tone, energy, tension, engagement, 
             contamination, aftertaste, contamination_events, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(session_id),
            result["message_count"],
            result["fler"]["tone"],
            result["fler"]["energy"],
            result["fler"]["tension"],
            result["fler"]["engagement"],
            result["fler"]["contamination"],
            result["aftertaste"],
            json.dumps(result["contamination_events"]),
            json.dumps(result, ensure_ascii=False)
        ))
        
        results.append({
            "session_id": session_id,
            "message_count": result["message_count"],
            "tone": result["fler"]["tone"],
            "energy": result["fler"]["energy"],
            "tension": result["fler"]["tension"],
            "engagement": result["fler"]["engagement"],
            "contamination": result["fler"]["contamination"],
            "aftertaste": result["aftertaste"],
            "contamination_events": len(result["contamination_events"]),
        })
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(sessions)} sessions...")
    
    fler_conn.commit()
    
    state_conn.close()
    fler_conn.close()
    
    if not results:
        print("[WARN] No results to display")
        sys.exit(0)
    
    # Sort by tone
    sorted_by_tone = sorted(results, key=lambda x: x["tone"], reverse=True)
    
    # Top 10 positive sessions
    print()
    print("=" * 70)
    print("  TOP 10 POSITIVE SESSIONS (highest tone)")
    print("=" * 70)
    for i, r in enumerate(sorted_by_tone[:10]):
        tone_str = f"{r['tone']:+.2f}"
        print(f"  {i+1:2d}. [{tone_str}] msgs={r['message_count']:3d} energy={r['energy']}/10 "
              f"tension={r['tension']}/10 contamination={r['contamination']}/10 "
              f"aftertaste={r['aftertaste']}")
        print(f"      session_id: {r['session_id']}")
    
    # Top 10 negative sessions
    print()
    print("=" * 70)
    print("  TOP 10 NEGATIVE SESSIONS (lowest tone)")
    print("=" * 70)
    for i, r in enumerate(sorted_by_tone[-10:]):
        tone_str = f"{r['tone']:+.2f}"
        print(f"  {i+1:2d}. [{tone_str}] msgs={r['message_count']:3d} energy={r['energy']}/10 "
              f"tension={r['tension']}/10 contamination={r['contamination']}/10 "
              f"aftertaste={r['aftertaste']}")
        print(f"      session_id: {r['session_id']}")
    
    # Overall statistics
    total = len(results)
    avg_tone = sum(r["tone"] for r in results) / total
    avg_energy = sum(r["energy"] for r in results) / total
    avg_tension = sum(r["tension"] for r in results) / total
    avg_engagement = sum(r["engagement"] for r in results) / total
    avg_contamination = sum(r["contamination"] for r in results) / total
    total_messages = sum(r["message_count"] for r in results)
    
    aftertaste_counts = {}
    for r in results:
        at = r["aftertaste"]
        aftertaste_counts[at] = aftertaste_counts.get(at, 0) + 1
    
    tone_distribution = {
        "positive (>0.2)": sum(1 for r in results if r["tone"] > 0.2),
        "neutral (-0.2..0.2)": sum(1 for r in results if -0.2 <= r["tone"] <= 0.2),
        "negative (<-0.2)": sum(1 for r in results if r["tone"] < -0.2),
    }
    
    contaminated_sessions = sum(1 for r in results if r["contamination"] > 0)
    sessions_with_events = sum(1 for r in results if r["contamination_events"] > 0)
    
    print()
    print("=" * 70)
    print("  OVERALL STATISTICS")
    print("=" * 70)
    print(f"  Sessions analyzed:      {total}")
    print(f"  Total user messages:    {total_messages}")
    print(f"  Avg messages/session:   {total_messages / total:.1f}")
    print()
    print(f"  Avg tone:               {avg_tone:+.2f}")
    print(f"  Avg energy:             {avg_energy:.1f}/10")
    print(f"  Avg tension:            {avg_tension:.1f}/10")
    print(f"  Avg engagement:         {avg_engagement:.1f}/10")
    print(f"  Avg contamination:      {avg_contamination:.1f}/10")
    print()
    print("  Tone distribution:")
    for label, count in tone_distribution.items():
        pct = count / total * 100
        print(f"    {label:25s} {count:4d} ({pct:5.1f}%)")
    print()
    print("  Aftertaste distribution:")
    for label, count in sorted(aftertaste_counts.items()):
        pct = count / total * 100
        print(f"    {label:25s} {count:4d} ({pct:5.1f}%)")
    print()
    print(f"  Sessions with contamination > 0:  {contaminated_sessions}")
    print(f"  Sessions with contamination events: {sessions_with_events}")
    print()
    print(f"  Results saved to: {FLER_DB_PATH}")
    print("=" * 70)


if __name__ == "__main__":
    main()
